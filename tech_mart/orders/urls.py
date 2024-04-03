from django.urls import path
from. import views
app_name = 'orders'
urlpatterns = [
  
    path('place_order/',views.checkout,name='place_order'),
    path('cancel_order/<int:id>',views.cancel_order,name='cancel'),
    path('order_details/<int:id>',views.order_details,name='order_details'),
    path('payment_success/<str:id>',views.payment_success,name='payment_success'),
    path('payment_failed/<str:id>',views.payment_failed,name='payment_failed'),
    path('return_order/<int:id>',views.return_order,name='return_order'),
    path('wallet/',views.view_wallet,name='wallet'),
    path('chage_payment/<int:order_id>',views.change_payment_method,name='change_payment_method'),
  
  
    
]