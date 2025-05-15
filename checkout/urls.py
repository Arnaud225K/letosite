from django.urls import include, path, re_path
from . import views

app_name = 'checkout'

urlpatterns = [
    # path('', views.cart_detail, name='cart_detail'),
    path('', views.CheckoutView.as_view(), name='checkout_page'),
    path('add/<str:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<str:product_id>/', views.cart_remove, name='cart_remove'),
    path('update-quantity/<str:product_id>/', views.cart_update_quantity, name='cart_update_quantity'),
    path('update-shipping-session/', views.update_shipping_session, name='update_shipping_session'),
    path('created/<uuid:order_key>/', views.order_created_view, name='order_created'),

    # --- URLs YooKassa ---
    path('yookassa/return/', views.YooKassaReturnView.as_view(), name='yookassa_return'),
    path('yookassa/webhook/', views.YooKassaWebhookView.as_view(), name='yookassa_webhook'),

    # --- URLs zayvka ---
    path('send_form_order/', views.SendFormOrder.as_view(), name='send_form_order'),
    # path('order_callback_form/', views.OrderCallbackView.as_view(type_order="Рассчитать стоимость(форма)"), name='order_callback_form'),
    path('thank-you/', views.ThankYouView.as_view(), name='thank-you'),
    path('generic-error/', views.GenericErrorView.as_view(), name='generic-error'),

]