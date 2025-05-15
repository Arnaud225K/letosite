from decimal import Decimal
from django.conf import settings
from menu.models import Product 

CART_SESSION_ID = 'zakaz'

CART_SESSION_ID = 'cart'
SHIPPING_INFO_SESSION_ID = 'shipping_info'


class CartManager:
    """Manages the shopping cart using the Django session ONLY."""
    def __init__(self, request):
        self.session = request.session
        cart_data = self.session.get(CART_SESSION_ID)
        if not cart_data:
            cart_data = self.session[CART_SESSION_ID] = {}
        self.cart_data = cart_data

    def save(self):
        """Marks session as modified to ensure backup."""
        self.session.modified = True

    def add(self, product, quantity=1, update_quantity=False):
        """Ajoute un produit au panier ou met à jour sa quantité, en respectant une limite."""
        product_id = str(product.id)
        current_price = str(product.price)
        # Récupère la limite depuis les settings, avec une valeur par défaut raisonnable
        max_quantity_per_item = getattr(settings, 'CART_ITEM_MAX_QUANTITY', 1000)

        if product_id not in self.cart_data:
            self.cart_data[product_id] = {'quantity': 0, 'price': current_price}

        current_cart_quantity = self.cart_data[product_id]['quantity']
        final_quantity = 0

        if update_quantity:
            # Remplacement : la quantité demandée est la nouvelle quantité
            final_quantity = quantity
        else:
            # Ajout : additionne à la quantité existante
            final_quantity = current_cart_quantity + quantity

        # --- Application de la Limite Maximale ---
        final_quantity = min(max(0, final_quantity), max_quantity_per_item)
        # max(0, ...) assure qu'on ne descend pas en dessous de 0
        # min(..., max_quantity_per_item) assure qu'on ne dépasse pas la limite

        # --- Mise à jour ou Suppression ---
        if final_quantity <= 0:
            # Si la quantité finale est 0 (ou moins), on supprime
            self.remove(product) # remove() appelle save()
        else:
            # Met à jour la quantité et le prix stocké
            self.cart_data[product_id]['quantity'] = final_quantity
            self.cart_data[product_id]['price'] = current_price # Met à jour au cas où
            self.save() # Sauvegarde la session
        return final_quantity

    def remove(self, product):
        """Remove a product from the cart."""
        product_id = str(product.id)
        if product_id in self.cart_data:
            del self.cart_data[product_id]
            self.save()

    def __iter__(self):
        """
        Iterates on cart items. Retrieves Product objects from DB
        objects for display and calculates totals using CURRENT prices.
        """
        product_ids = self.cart_data.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(p.id): p for p in products}

        cart = self.cart_data.copy()

        items_to_remove = []

        for product_id, item_data in cart.items():
            product = product_dict.get(product_id)
            if product:
                item_data['product'] = product
                item_data['total_price'] = product.price * item_data['quantity']
                yield item_data
            else:
                items_to_remove.append(product_id)
                print(f"Warning: Product ID {product_id} found in cart session but not in DB. Removing.")

        if items_to_remove:
            for product_id in items_to_remove:
                if product_id in self.cart_data:
                    del self.cart_data[product_id]
            self.save()


    def __len__(self):
        """Returns the total quantity of items in the basket."""
        return sum(item['quantity'] for item in self.cart_data.values())

    def get_total_price(self):
        """
        Calculates total cart price using CURRENT product PRICES.
        """
        product_ids = self.cart_data.keys()
        products = Product.objects.filter(id__in=product_ids).only('id', 'price')
        product_prices = {str(p.id): p.price for p in products}

        total = Decimal(0)
        items_to_remove = []

        for product_id, item_data in self.cart_data.items():
            current_price = product_prices.get(product_id)
            if current_price is not None:
                total += current_price * item_data['quantity']
            else:
                items_to_remove.append(product_id)

        if items_to_remove:
            for product_id in items_to_remove:
                 if product_id in self.cart_data:
                     del self.cart_data[product_id]
            self.save()

        return total


    def clear(self):
        """Vide le panier ET les informations de livraison de la session."""
        # Vide les articles du panier
        if CART_SESSION_ID in self.session:
            del self.session[CART_SESSION_ID]
            self.cart_data = {} # Réinitialise aussi la donnée interne
            print("Cart data cleared from session.") # Debug

        # Vide les informations de livraison
        if SHIPPING_INFO_SESSION_ID in self.session:
            del self.session[SHIPPING_INFO_SESSION_ID]
            print("Shipping info cleared from session.") # Debug

        self.save() # Assure que les modifications de session sont sauvegardées

    def get_cart_data(self):
        """Returns the raw data structure of the cart (for debugging or other purposes)."""
        return self.cart_data