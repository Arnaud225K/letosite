from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse
from django.contrib import messages
from .models import Product, Order, OrderItem, Zakaz
from .forms import OrderCreateForm, ZakazForm
from .cart import CartManager
from decimal import Decimal 
from django.core.files.storage import default_storage
from django.db import transaction
import logging
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import json 
from django.utils.decorators import method_decorator
from django.conf import settings
import uuid
from django.views.decorators.http import require_POST
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotification, WebhookNotificationEventType
# from yookassa.domain.common import SecurityHelper
# from yookassa.domain.notification import (WebhookNotificationEventType,
#                                           WebhookNotificationFactory)
from django.views.decorators.csrf import csrf_exempt

from letosite.views import cart_context 
from django.contrib.sites.shortcuts import get_current_site


# from . import orderpy as zayavka
from utils.utils import send_notification

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re



logger = logging.getLogger(__name__)

# --- Configuration YooKassa ---
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

# --- Constantes de Livraison
SUBTOTAL_THRESHOLD = 10000
MKAD_INSIDE_LOW_COST = 500
MKAD_OUTSIDE_RATE_PER_KM = 50
RUSSIA_SHIPPING_COST = 0


SHIPPING_INFO_SESSION_ID = 'shipping_info'

INFO_EMAIL = "kouakanarnaud@gmail.com"

@require_POST
def cart_update_quantity(request, product_id):
    """Met à jour la quantité d'un produit ou le supprime si quantité <= 0."""
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    cart = CartManager(request)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

    max_quantity_per_item = getattr(settings, 'CART_ITEM_MAX_QUANTITY', 1000)

    try:
        data = json.loads(request.body.decode('utf-8'))
        requested_quantity = int(data.get('quantity'))
        quantity = min(max(0, requested_quantity), max_quantity_per_item)

        action = ''
        if quantity <= 0:
            cart.remove(product)
            action = 'removed'
            new_quantity = 0
            logger.info(f"Product {product_id} removed from cart by quantity update.")
        else:
            cart.add(product=product, quantity=quantity, update_quantity=True)
            action = 'updated'
            new_quantity = cart.cart_data.get(str(product_id), {}).get('quantity', 0)
            logger.info(f"Product {product_id} quantity updated to {new_quantity}.")


        # --- VÉRIFICATION ET NETTOYAGE SESSION LIVRAISON ---
        cart_data_after_update = cart.get_cart_data()
        cart_unique_items_count = len(cart_data_after_update)
        # print(f"Update Quantity View - Cart Data After Update: {cart_data_after_update}")
        # print(f"Update Quantity View - Unique Items Count Sent: {cart_unique_items_count}")
        
        cart_is_now_empty = cart_unique_items_count

        if cart_is_now_empty:
            if 'shipping_info' in request.session:
                del request.session['shipping_info']
                logger.info("Shipping info cleared from session because cart became empty.")
        # ----------------------------------------------------

        response_data = {
            'success': True,
            'action': action,
            'product_id': product_id,
            'new_quantity': new_quantity,
            'cart_total_items':cart_unique_items_count,
            'cart_total_price': str(cart.get_total_price()),
            'item_total_price': str(product.price * new_quantity) if new_quantity > 0 else '0'
        }
        return JsonResponse(response_data)

    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
        logger.warning(f"Invalid data received for cart quantity update: {e}")
        return JsonResponse({'success': False, 'error': 'Invalid data provided'}, status=400)
    except Exception as e:
        logger.error(f"Error updating cart quantity for product {product_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Server error'}, status=500)



@require_POST
def update_shipping_session(request):
    """Met à jour les informations de livraison dans la session via AJAX."""
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
        shipping_method = data.get('shipping_method')
        shipping_distance_km_str = data.get('shipping_distance_km')

        valid_methods = [choice[0] for choice in Order.DELIVERY_CHOICES]
        if shipping_method not in valid_methods:
            request.session.pop('shipping_info', None)
            request.session.modified = True
            logger.warning(f"Invalid or empty shipping method received via AJAX: {shipping_method}")
            return JsonResponse({'success': True, 'message': 'Shipping info cleared.'})


        distance_km = None
        if shipping_method == Order.DELIVERY_MKAD_OUTSIDE:
            try:
                distance_km = int(shipping_distance_km_str) if shipping_distance_km_str else 0
                if distance_km <= 0:
                    distance_km = None
                    logger.warning(f"Invalid distance received via AJAX for MKAD_OUTSIDE: {shipping_distance_km_str}")

            except (ValueError, TypeError):
                distance_km = None
                logger.warning(f"Non-integer distance received via AJAX for MKAD_OUTSIDE: {shipping_distance_km_str}")

        request.session['shipping_info'] = {
            'method': shipping_method,
            'distance_km': distance_km
        }
        request.session.modified = True
        logger.debug(f"Session updated via AJAX with shipping: {request.session['shipping_info']}")

        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        logger.error("AJAX update_shipping_session: Invalid JSON received.")
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error updating shipping session via AJAX: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Server error'}, status=500)




class CheckoutView(View):
    template_name = 'checkout/p-checkout.html'
    form_class = OrderCreateForm

    def _get_context_data(self, request, cart=None, form=None, shipping_info=None):
        """Helper pour construire le contexte commun."""
        if cart is None:
            cart = CartManager(request)
        if form is None:
            form = self.form_class()
        if shipping_info is None:
            shipping_info = request.session.get('shipping_info', {})

        shipping_method_choices = Order.DELIVERY_CHOICES
        payment_method_choices = Order.PAYMENT_METHOD_CHOICES
        selected_shipping_method = shipping_info.get('method')
        shipping_distance_km_session = shipping_info.get('distance_km')

        shipping_method_display = dict(shipping_method_choices).get(selected_shipping_method)

        return {
            'cart': cart,
            'form': form,
            'shipping_choices': shipping_method_choices,
            'payment_choices': payment_method_choices,
            'selected_shipping_method': selected_shipping_method,
            'shipping_distance_km_session': shipping_distance_km_session,
            'shipping_method_display': shipping_method_display,
            'DELIVERY_MKAD_OUTSIDE': Order.DELIVERY_MKAD_OUTSIDE,
            'DELIVERY_MKAD_INSIDE': Order.DELIVERY_MKAD_INSIDE,
            'DELIVERY_RUSSIA': Order.DELIVERY_RUSSIA,
            'PAYMENT_ONLINE_YOOKASSA': Order.PAYMENT_ONLINE_YOOKASSA,
        }

    def get(self, request, *args, **kwargs):
        """Affiche la page checkout avec panier, livraison, formulaire."""
        cart = CartManager(request)
        context = self._get_context_data(request, cart)

        if not cart:
            messages.info(request, "Ваша корзина пуста.")

        return render(request, self.template_name, context)

    @method_decorator(transaction.atomic)
    def post(self, request, *args, **kwargs):
        """Traite la soumission du formulaire et la création de la commande."""
        cart = CartManager(request)
        if not cart:
            messages.error(request, "Ваша корзина пуста. Невозможно оформить заказ.")
            return redirect('checkout:checkout_page')

        form = self.form_class(request.POST, request.FILES)

        # --- Récupération et Validation Finale de la Livraison (Côté Serveur) ---
        shipping_info = request.session.get('shipping_info', {})
        shipping_method = shipping_info.get('method')
        shipping_distance_km = shipping_info.get('distance_km')

        valid_shipping_methods = [choice[0] for choice in Order.DELIVERY_CHOICES]
        if not shipping_method or shipping_method not in valid_shipping_methods:
            messages.error(request, "Пожалуйста, выберите способ доставки в разделе корзины.")
            context = self._get_context_data(request, cart, form, shipping_info)
            return render(request, self.template_name, context)

        # Re-valide la distance si la méthode est MKAD_OUTSIDE
        if shipping_method == Order.DELIVERY_MKAD_OUTSIDE:
            if shipping_distance_km is None or shipping_distance_km <= 0:
                logger.warning(f"Invalid distance in session for MKAD_OUTSIDE for potential order. Session: {shipping_info}")
                messages.error(request, "Указано неверное расстояние для доставки за МКАД. Пожалуйста укажите его.")
                context = self._get_context_data(request, cart, form, shipping_info)
                return render(request, self.template_name, context)
        else:
            shipping_distance_km = None

        # --- Fin Validation Livraison ---

        if form.is_valid():
            
            logger.info("Checkout form is valid. Proceeding to create order.")
            
            order = form.save(commit=False)
            order.shipping_method = shipping_method
            order.shipping_distance_km = shipping_distance_km

            # GET IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            order.ip_address = (x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR'))

            # --- Recalcull du Total Items + Validation Existence/Dispo ---
            items_total_cost = Decimal('0')
            calculated_shipping_cost = Decimal('0')
            product_ids = cart.get_cart_data().keys()
            products_in_db = Product.objects.filter(
                id__in=product_ids, available=True, is_hidden=False
            ).only('id', 'title', 'price')
            product_dict = {str(p.id): p for p in products_in_db}
            items_to_create_instances = []
            cart_items_data = cart.get_cart_data()
            missing_or_unavailable_products = []

            for product_id in product_ids:
                if product_id not in product_dict:
                    item_info = cart_items_data.get(product_id)
                    title_in_cart = item_info.get('product_title', f'ID: {product_id}') if item_info else f'ID: {product_id}'
                    missing_or_unavailable_products.append(title_in_cart)

            if missing_or_unavailable_products:
                logger.warning(f"Order creation failed during POST: Products not available/found: {', '.join(missing_or_unavailable_products)}")
                messages.error(request, f"Некоторые товары больше не доступны ({', '.join(missing_or_unavailable_products)}). Заказ не создан.")
                context = self._get_context_data(request, cart, form, shipping_info)
                return render(request, self.template_name, context)

            for product_id, item_data in cart_items_data.items():
                product = product_dict.get(product_id)
                item_price = product.price
                item_quantity = item_data['quantity']
                items_total_cost += item_price * Decimal(item_quantity)
                items_to_create_instances.append(
                    OrderItem(
                        product=product, product_title=product.title,
                        price=item_price, quantity=item_quantity
                    )
                )

            if not items_to_create_instances:
                messages.error(request, "Не удалось добавить товары в заказ (корзина пуста?).")
                context = self._get_context_data(request, cart, form, shipping_info)
                return render(request, self.template_name, context)
            # --- Fin Calcul Total Items ---

            # --- Recalcul Frais de Port Côté Serveur ---
            calculated_shipping_cost = Decimal('0')
            if order.shipping_method == Order.DELIVERY_MKAD_INSIDE:
                calculated_shipping_cost = Decimal('0') if items_total_cost >= SUBTOTAL_THRESHOLD else Decimal(MKAD_INSIDE_LOW_COST)
            elif order.shipping_method == Order.DELIVERY_MKAD_OUTSIDE:
                if order.shipping_distance_km and order.shipping_distance_km > 0:
                    calculated_shipping_cost = Decimal(order.shipping_distance_km * MKAD_OUTSIDE_RATE_PER_KM)
            elif order.shipping_method == Order.DELIVERY_RUSSIA:
                calculated_shipping_cost = Decimal(RUSSIA_SHIPPING_COST)
            
            # --- Calcul du Total Général ---
            final_grand_total = items_total_cost + calculated_shipping_cost
            # --- Fin Calcul Frais de Port ---

            # Assignation les coûts finaux
            order.total_cost = items_total_cost
            order.shipping_cost = calculated_shipping_cost
            order.grand_total_amount = final_grand_total
            order.status = Order.STATUS_PENDING

            # --- Logique de Paiement ---
            if order.payment_method == Order.PAYMENT_ONLINE_YOOKASSA:
                # order.status = Order.STATUS_PENDING_PAYMENT
                # order.paid = False

                # # Sauvegarde initiale de la commande pour avoir un ID et order_key
                # try:
                #     order.save()
                #     logger.info(f"Order {order.id} (YooKassa pending) pre-saved.")
                #     # Sauvegarde du fichier après la première sauvegarde
                #     if 'file' in form.cleaned_data and form.cleaned_data['file']:
                #         order.file = form.cleaned_data['file']
                #         order.save(update_fields=['file','updated_at'])

                #     # Création des OrderItems associés
                #     for item_instance in items_to_create_instances: item_instance.order = order
                #     OrderItem.objects.bulk_create(items_to_create_instances)
                #     logger.info(f"OrderItems created for pending YooKassa order {order.id}.")

                # except Exception as e:
                #     logger.error(f"Error pre-saving order for YooKassa payment: {e}", exc_info=True)
                #     messages.error(request, "Ошибка при подготовке заказа к оплате.")
                #     context = self._get_context_data(request, cart, form, shipping_info)
                #     return render(request, self.template_name, context)


                # # --- Création du Paiement YooKassa ---
                # try:
                #     payment_data = {
                #         "amount": {
                #             "value": str(order.grand_total_amount),
                #             "currency": "RUB"
                #         },
                #         "confirmation": {
                #             "type": "redirect",
                #             "return_url": settings.YOOKASSA_RETURN_URL # URL de retour
                #         },
                #         "capture": True, # Capturer automatiquement le paiement si succès
                #         "description": f"Заказ №{order.id} ({order.order_key})",
                #         "metadata": { # Stocke des infos utiles pour le webhook
                #             'order_internal_id': order.id,
                #             'order_key': str(order.order_key)
                #         }
                #         # Ajouter d'autres infos si besoin (email client, etc.)
                #         # "receipt": { ... } # Pour envoyer un reçu fiscal
                #     }
                #     # Génère une clé d'idempotence unique pour cette tentative
                #     idempotence_key = str(uuid.uuid4())

                #     payment_response = Payment.create(payment_data, idempotence_key)

                #     # Sauvegarde l'ID de paiement YooKassa sur la commande
                #     order.yookassa_payment_id = payment_response.id
                #     order.yookassa_payment_status = payment_response.status # Devrait être 'pending'
                #     order.save(update_fields=['yookassa_payment_id', 'yookassa_payment_status', 'updated_at'])
                #     logger.info(f"YooKassa payment created for order {order.id}. Payment ID: {payment_response.id}, Status: {payment_response.status}")

                #     # Vider le panier SEULEMENT SI le paiement est initié avec succès
                #     cart.clear()
                #     request.session.pop('shipping_info', None)
                #     logger.info(f"Cart and shipping info cleared AFTER successful YooKassa payment initiation for order {order.id}.")

                #     # Redirige l'utilisateur vers l'URL de confirmation de YooKassa
                #     confirmation_url = payment_response.confirmation.confirmation_url
                #     return redirect(confirmation_url)

                # except Exception as e:
                #     # La transaction atomique annulera la création de la commande si erreur ici
                #     logger.error(f"CRITICAL: YooKassa payment creation failed for potential order ID {order.id}. Error: {e}", exc_info=True)
                #     order.status = Order.STATUS_PAYMENT_FAILED # Met à jour le statut en cas d'échec
                #     order.save(update_fields=['status', 'updated_at'])
                #     messages.error(request, "Не удалось инициировать онлайн-оплату. Пожалуйста, попробуйте другой способ оплаты или свяжитесь с нами.")
                #     # Ne pas vider le panier ici, l'utilisateur doit pouvoir réessayer
                #     context = self._get_context_data(request, cart, form, shipping_info)
                #     return render(request, self.template_name, context)

                messages.error(request, "Выбранный способ оплаты (Онлайн) временно недоступен. Пожалуйста, выберите другой.")
                # Ré-afficher le formulaire avec l'erreur et les données actuelles
                shipping_info_for_render = request.session.get('shipping_info', None)
                context = self._get_context_data(request, cart, form, shipping_info_for_render)
                return render(request, self.template_name, context)

            else: # Autres méthodes de paiement (Cash, On Delivery)
                # Statut initial standard (peut-être 'processing' si pas besoin de confirmation)
                order.status = Order.STATUS_PROCESSING # Ou garder STATUS_PENDING

                # Sauvegarde Order et Items (comme avant, transaction atomique gère)
                try:
                    order.save()
                    form.save_m2m()
                    if 'file' in form.cleaned_data and form.cleaned_data['file']:
                        order.file = form.cleaned_data['file']
                        order.save(update_fields=['file','updated_at'])

                    for item_instance in items_to_create_instances: item_instance.order = order
                    OrderItem.objects.bulk_create(items_to_create_instances)

                    cart.clear()
                    request.session.pop('shipping_info', None)

                    messages.success(request, "Ваш заказ успешно оформлен!")
                    # Redirige vers la page de confirmation standard
                    return redirect(reverse('checkout:order_created', args=[order.order_key]))

                except Exception as e:
                    logger.error(f"Error saving non-YooKassa order: {e}", exc_info=True)
                    messages.error(request, "Произошла ошибка при сохранении вашего заказа.")
                    context = self._get_context_data(request, cart, form, shipping_info)
                    return render(request, self.template_name, context)
    
        else: # Formulaire Client Invalide
            logger.warning("Checkout form is INVALID.")
            # Affiche toutes les erreurs trouvées par Django
            logger.warning(f"Form errors: {form.errors.as_json()}")
            # Affiche les données POST reçues (pour vérifier les noms et valeurs)
            logger.debug(f"Received POST data: {request.POST}")
            # Affiche les fichiers reçus
            logger.debug(f"Received FILES data: {request.FILES}")

            messages.error(request, "Пожалуйста, исправьте ошибки в форме адреса.")
            shipping_info = request.session.get('shipping_info', {})
            context = self._get_context_data(request, cart, form, shipping_info)
            return render(request, self.template_name, context)





# --- Vue de confirmation (order_created_view reste identique) ---
def order_created_view(request, order_key):
    order = get_object_or_404(Order, order_key=order_key)
    return render(request, 'checkout/order_created.html', {'order': order})




@require_POST
def cart_add(request, product_id):
    """
    Ajoute un produit au panier via AJAX et renvoie une réponse JSON
    pour afficher un modal de confirmation.
    """
    # Vérifier si c'est une requête AJAX (bonne pratique)
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request type'}, status=400)

    cart = CartManager(request)
    try:
        product = Product.objects.get(id=product_id, is_hidden=False, available=True) # Vérifie dispo ici
    except Product.DoesNotExist:
        logger.warning(f"Attempted to add non-existent or unavailable product {product_id} to cart.")
        return JsonResponse({'success': False, 'error': 'Товар не найден или недоступен'}, status=404)

    try:
        # Récupérer la quantité depuis les données POST JSON (si envoyées) ou formulaire standard
        quantity = 1 # Par défaut 1
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
            quantity = int(data.get('quantity', 1))
        else: # Fallback pour formulaire standard
            quantity = int(request.POST.get('quantity', 1))

        # Valider et limiter la quantité
        max_quantity_per_item = getattr(settings, 'CART_ITEM_MAX_QUANTITY', 1000)
        # Si on ajoute, on prend la quantité actuelle + la nouvelle, puis on limite
        current_cart_quantity = cart.cart_data.get(str(product.id), {}).get('quantity', 0)
        final_quantity_to_set = min(max(1, current_cart_quantity + quantity), max_quantity_per_item) # Assure au moins 1 et pas plus que max

        # Utilise update_quantity=True pour définir la quantité finale calculée
        new_quantity_in_cart = cart.add(product=product, quantity=final_quantity_to_set, update_quantity=True)

        logger.info(f"Product {product_id} added/updated in cart. New quantity: {new_quantity_in_cart}")

        # --- Préparer la réponse JSON ---
        # Récupérer le nouveau compte total d'items UNIQUES pour le header
        # new_cart_context = cart_context(request) # Appelle le context processor
        # header_count = new_cart_context.get('cart_items_count', 0)
        cart_data_final = cart.get_cart_data()
        header_count_final = len(cart_data_final)
        print(f"CART_ADD VIEW - Final Cart Data: {cart_data_final}")
        print(f"CART_ADD VIEW - Final Header Count Calculated: {header_count_final}")

        response_data = {
            'success': True,
            'message': 'Товар добавлен в корзину!',
            'product_id': product.id,
            'product_title': product.title,
            'product_image_url': product.image.url, # Utilise votre méthode modèle
            'quantity_added': quantity, # Quantité demandée à ajouter
            'new_quantity_in_cart': new_quantity_in_cart, # Quantité résultante dans le panier
            'cart_total_items': header_count_final, # Nombre d'articles UNIQUES pour le header
            'cart_total_price': str(cart.get_total_price()), # Nouveau total $
        }
        return JsonResponse(response_data)

    except (ValueError, TypeError):
        logger.warning(f"Invalid quantity format received for product {product_id}.")
        return JsonResponse({'success': False, 'error': 'Неверное количество'}, status=400)
    except Exception as e:
        logger.error(f"Error adding product {product_id} to cart: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Ошибка сервера при добавлении в корзину'}, status=500)




@require_POST
def cart_remove(request, product_id):
    cart = CartManager(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product) # remove() dans CartManager sauvegarde déjà la session
    messages.info(request, f"'{product.title}' удален из корзины.")

    # --- AJOUT : Vérification si le panier est vide après suppression ---
    if len(cart) == 0:
        if SHIPPING_INFO_SESSION_ID in request.session:
            del request.session[SHIPPING_INFO_SESSION_ID]
            # cart.save() est appelé par cart.remove() donc pas besoin ici,
            # mais s'assurer que la session est marquée modifiée si ce n'était pas le cas
            request.session.modified = True
            logger.info("Shipping info cleared from session because cart became empty after removal.")
            print("Shipping info cleared from session because cart became empty after removal.") # Debug
    # -----------------------------------------------------------------

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            cart_data_after_remove = cart.get_cart_data()
            new_cart_context = cart_context(request)
            header_count = new_cart_context.get('cart_items_count', 0)
            response_data = {
                'success': True,
                'message': f"'{product.title}' удален.",
                'product_id': product_id,
                'cart_total_items': header_count,
                'cart_total_price': str(cart.get_total_price()),
            }
            return JsonResponse(response_data)
        else: # Comportement standard si pas AJAX
            messages.info(request, f"'{product.title}' удален из корзины.")
            return redirect('checkout:checkout_page')
    # Redirige vers la page checkout après suppression
    # return redirect('checkout:checkout_page')





#--------WEBHOOK FOR YOOKASSA -----------#

@method_decorator(csrf_exempt, name='dispatch') # Désactive CSRF pour le webhook
class YooKassaWebhookView(View):
    """
    Reçoit les notifications webhook de YooKassa pour mettre à jour le statut des commandes.
    """
    def post(self, request, *args, **kwargs):
        try:
            event_json = json.loads(request.body.decode('utf-8'))
            notification_object = WebhookNotification(event_json)
            payment_info = notification_object.object # Contient les infos du paiement

            if not payment_info or not payment_info.id:
                logger.warning("Webhook YooKassa reçu sans ID de paiement.")
                return HttpResponse(status=200) # Répondre 200 OK même si on ne traite pas

            logger.info(f"Webhook YooKassa reçu. Event: {notification_object.event}, Payment ID: {payment_info.id}, Status: {payment_info.status}")

            # Utilise une transaction pour la mise à jour
            with transaction.atomic():
                # Trouve la commande associée via yookassa_payment_id
                try:
                    order = Order.objects.select_for_update().get(yookassa_payment_id=payment_info.id)
                except Order.DoesNotExist:
                    logger.error(f"Webhook YooKassa : Commande non trouvée pour Payment ID {payment_info.id}")
                    # Répondre 200 OK pour que YooKassa ne renvoie pas la notif
                    return HttpResponse(status=200)
                except Order.MultipleObjectsReturned:
                    logger.error(f"Webhook YooKassa : Plusieurs commandes trouvées pour Payment ID {payment_info.id}!")
                    return HttpResponse(status=500) # Problème grave

                # Met à jour le statut YooKassa local
                order.yookassa_payment_status = payment_info.status

                # Logique de mise à jour basée sur le statut YooKassa
                if payment_info.status == 'succeeded':
                    # Vérifie si le paiement n'était pas déjà marqué comme réussi
                    if not order.paid:
                        order.paid = True
                        order.status = Order.STATUS_PROCESSING # Ou STATUS_COMPLETED si pas d'étape de traitement
                        # Enregistrer le montant payé (optionnel mais utile)
                        if payment_info.amount and payment_info.amount.value:
                            order.total_paid = Decimal(payment_info.amount.value)
                        # Mettre à jour l'ID de transaction si disponible et différent
                        if payment_info.id and order.transaction_id != payment_info.id:
                            order.transaction_id = payment_info.id # Utilise l'ID de paiement YooKassa comme ID de transaction
                        order.save(update_fields=['paid', 'status', 'total_paid', 'transaction_id', 'yookassa_payment_status', 'updated_at'])
                        logger.info(f"Webhook YooKassa: Order {order.id} marquée comme payée (succeeded).")
                        # --- ICI : Déclencher l'envoi d'email de confirmation, etc. ---
                        # send_order_confirmation_email(order)
                    else:
                        logger.info(f"Webhook YooKassa: Order {order.id} déjà marquée comme payée (succeeded reçu à nouveau).")

                elif payment_info.status == 'canceled':
                    if order.status != Order.STATUS_CANCELLED: # Évite updates inutiles
                        order.status = Order.STATUS_PAYMENT_FAILED # Ou STATUS_CANCELLED
                        order.paid = False
                        order.save(update_fields=['status', 'paid', 'yookassa_payment_status', 'updated_at'])
                        logger.warning(f"Webhook YooKassa: Paiement annulé pour Order {order.id} (canceled).")
                        # --- ICI : Potentiellement notifier l'admin ou le client ---

                elif payment_info.status == 'waiting_for_capture':
                    # Si vous utilisez capture: False, vous recevrez ce statut.
                    # Vous devez alors appeler Payment.capture(payment_info.id, ...)
                    logger.info(f"Webhook YooKassa: Paiement en attente de capture pour Order {order.id}.")
                    order.save(update_fields=['yookassa_payment_status', 'updated_at'])
                    # Implémentez la logique de capture si nécessaire

                else: # pending, etc.
                    logger.info(f"Webhook YooKassa: Statut {payment_info.status} reçu pour Order {order.id}, pas d'action immédiate.")
                    order.save(update_fields=['yookassa_payment_status', 'updated_at']) # Sauvegarde juste le statut


            # YooKassa s'attend à une réponse 200 OK pour confirmer la réception
            return HttpResponse(status=200)

        except json.JSONDecodeError:
            logger.error("Webhook YooKassa : Impossible de décoder le JSON.")
            return HttpResponse(status=400) # Bad Request
        except Exception as e:
            logger.error(f"Webhook YooKassa : Erreur inattendue: {e}", exc_info=True)
            return HttpResponse(status=500) # Internal Server Error


class YooKassaReturnView(View):
    """
    Page où l'utilisateur est redirigé après la tentative de paiement YooKassa.
    Vérifie le statut du paiement (facultatif mais recommandé) et affiche un message.
    """
    template_name_success = 'checkout/elements/yookassa/yookassa_success.html'
    template_name_pending = 'checkout/elements/yookassa/yookassa_pending.html'
    template_name_failure = 'checkout/elements/yookassa/yookassa_failure.html'

    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('paymentId') # YooKassa peut ajouter ceci, mais pas garanti
        order_key = request.GET.get('orderKey')   # Vous pourriez ajouter ceci à return_url

        # Tenter de récupérer la commande (soit via paymentId si présent, soit via une clé de commande passée)
        order = None
        if payment_id:
            try:
                # Vérifier le statut réel auprès de YooKassa est PLUS FIABLE que de se fier
                # uniquement à la redirection. Le webhook est la source de vérité.
                payment_info = Payment.find_one(payment_id)
                order = Order.objects.filter(yookassa_payment_id=payment_id).first()

                if payment_info.status == 'succeeded':
                    # Même si le webhook n'est pas encore arrivé, on peut afficher succès
                    logger.info(f"YooKassa Return: Paiement {payment_id} réussi.")
                    return render(request, self.template_name_success, {'order': order})
                elif payment_info.status == 'canceled':
                    logger.warning(f"YooKassa Return: Paiement {payment_id} annulé.")
                    return render(request, self.template_name_failure, {'order': order})
                else: # pending, waiting_for_capture
                    logger.info(f"YooKassa Return: Paiement {payment_id} en attente ({payment_info.status}).")
                    return render(request, self.template_name_pending, {'order': order})

            except Exception as e:
                logger.error(f"YooKassa Return: Erreur lors de la vérification du paiement {payment_id}: {e}", exc_info=True)
                # Afficher un message générique en cas d'erreur
                messages.error(request, "Не удалось проверить статус вашего платежа. Пожалуйста, проверьте вашу почту или свяжитесь с нами.")
                return redirect('checkout:checkout_page') # Ou une autre page d'erreur

        elif order_key: # Fallback si paymentId n'est pas dans l'URL
            order = get_object_or_404(Order, order_key=order_key)
            # Ici, on se fie davantage au statut local (mis à jour par webhook idéalement)
            if order.paid:
                return render(request, self.template_name_success, {'order': order})
            elif order.status == Order.STATUS_PAYMENT_FAILED or order.status == Order.STATUS_CANCELLED:
                return render(request, self.template_name_failure, {'order': order})
            else: # pending_payment, etc.
                return render(request, self.template_name_pending, {'order': order})
        else:
            logger.error("YooKassa Return: Ni paymentId ni orderKey trouvés dans l'URL de retour.")
            messages.error(request, "Произошла ошибка при возвращении со страницы оплаты.")
            return redirect('checkout:checkout_page') # Redirection générique
        



#::::::::::::::: ЗАЯВКА ::::::::::::::::::::::::#

class OrderCallbackView(View):
    pass
	# type_order = ""
	
	# def post(self, request):
	# 	zayavka.create_order(request, self.type_order, None)
	# 	return HttpResponse(json.dumps({}), content_type="application/json")


class SendFormOrder(View):

    def post(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = ZakazForm(request.POST)

        if form.is_valid():
            logger.info("Form submitted and is valid.")
            try:
                order = form.save(commit=False)
                order.type_order = form.cleaned_data.get('type', 'Заявка (не указан)')
                order.ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
                text_order = form.cleaned_data.get('comment', '')
                # Ajoutez ici la logique pour produit_title/price si nécessaire pour certains types
                # if order.type_order == 'Под заказ' or order.type_order == 'Быстрый заказ':
                #     produit_title = post_data.get('produit_title', '')
                #     produit_price = post_data.get('produit_price', '')
                    
                #     text_order += f"Заказ: {produit_title}\n"
                #     text_order += f"Стоимость - {produit_price}\n"
                order.text = text_order


                order.save()
                logger.info(f"Zakaz object {order.id} created successfully.")

                request.session['order_number'] = order.id

                #:::::::::::::::::::::::::::::::::::::::::::#
                #::::::: SEND NOTIFICATION ORDER :::::::::::#
                #:::::::::::::::::::::::::::::::::::::::::::#
                # order_number = order.id
                # mail_subject = f"Vous avez reçu un nouveau message - Type: {order.type_order}"
                # mail_template = 'orders/new_order_phone_received.html'
                # context = {
                #     'order_type': order.type_order,
                #     'phone': order.phone if order.phone else "Non fourni",
                #     # 'email': order.email if order.email else "Non fourni",
                #     'name': order.name if order.name else "Anonyme",
                #     # 'text_order':order.text if order.text else "Non fourni",
                #     'order_number': order_number,
                #     'order_date': order.date,
                #     'to_email': INFO_EMAIL, 
                # }
                # send_notification(mail_subject, mail_template, context)
                #:::::::::::::::::::::::::::::::::::::::::::#
                #::::::: END SEND NOTIFICATION ORDER :::::::::::#
                #:::::::::::::::::::::::::::::::::::::::::::#

                # --- Réponse ---
                if is_ajax:
                    thank_you_url = request.build_absolute_uri(reverse('checkout:thank-you'))
                    return JsonResponse({'success': True, 'thank_you_url': thank_you_url})
                else:
                    return redirect('checkout:thank-you')

            except Exception as e_save:
                logger.error(f"Error saving Zakaz object after validation: {e_save}", exc_info=True)
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Ошибка сохранения данных.'}, status=500)
                else:
                    messages.error(request, "Произошла ошибка при сохранении заявки.")
                    return redirect('checkout:generic-error')

        else:
            logger.warning(f"Form submission invalid: {form.errors.as_json()}")
            if is_ajax:
                if 'form_input' in form.errors and any(e.code == 'honeypot' for e in form.errors['form_input']):
                    return JsonResponse({'success': False, 'error': 'Ошибка безопасности.'}, status=400)
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.get_json_data()
                }, status=400)
            else:
                if 'form_input' in form.errors and any(e.code == 'honeypot' for e in form.errors['form_input']):
                    return redirect(reverse('checkout:generic-error'))
                else:
                    messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
                    return redirect(request.META.get('HTTP_REFERER', reverse('checkout:generic-error')))



class ThankYouView(View):
	def get(self, request):
		is_thank_you = True
        
		message = "Наши менеджеры свяжутся с вами в ближайшее время для <br> уточнения деталей."

		context = {
			'is_thank_you': is_thank_you,
			'message': message,
		}

		return render(request, 'catalog/thank-you.html', context)
	

class GenericErrorView(View):
	def get(self, request):
		is_generic_error = True
		message = "Ваша заявка не была успешной из-за мер безопасности. <br> Пожалуйста, повторите попытку позже."
		context = {
			'is_generic_error':is_generic_error,
			'message':message,
		}
		return render(request, 'catalog/generic-error.html', context)