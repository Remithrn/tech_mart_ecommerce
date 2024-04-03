from django.urls import path
from . import views
app_name='cart'

urlpatterns = [
    path('',views.cart_view,name='view_cart'),
    path('add/<str:slug>/',views.add_cart,name='add_cart'),
    path('remove/<str:slug>/',views.remove_item,name='remove_from_cart'),
    path('remove_all/<str:slug>/',views.remove_all_item,name='remove_all_from_cart'),
    path('add_to_wishlist/<str:slug>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('remove_from_wishlist/<str:slug>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('wishlist/',views.whishlist,name='wishlist'),
    path('remove_coupon/',views.remove_coupon,name='remove_coupon'),



]
