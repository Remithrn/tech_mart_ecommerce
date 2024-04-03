from django.urls import path
from . import views
app_name='adminUser'
urlpatterns=[
    path("",views.adminDashboard,name='users'),
    path("register",views.adminRegistration,name='adminregistration'),
    path('toggle/customer/<int:customer_id>/', views.toggle_customer_status, name='toggle_customer_status'),
    path('create/category/', views.create_category, name='create_category'),
    path('create/product/', views.create_product12, name='create_product'),
    path('edit/category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete/category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('edit/product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('error/',views.error_view,name='error'),
    path('users/',views.user_management,name='dashboard'),
    path('products/',views.product_management,name='products'),
    path('categories/',views.category_management,name='categories'),
    path('orders/',views.order_management,name='orders'),
    path('edit_order/<int:order_id>/',views.edit_order,name='edit_order'),
    path('sales_report/',views.sales_report,name='sales_report'),
    path('coupons/',views.coupon_management,name='coupons'),
    path('create/coupon/',views.create_coupon,name='create_coupon'),
    path('edit/coupon/<int:coupon_id>/',views.edit_coupon,name='edit_coupon'),
    path('delete/coupon/<int:coupon_id>/',views.delete_coupon,name='delete_coupon'),
   
]