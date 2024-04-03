from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.ProductList.as_view(), name="home"),
    path("product/<str:slug>", views.ProductDetail.as_view(), name="detail"),
    path("category1/", views.ShopList.as_view(), name="shop"),
    path('category/', views.allProdCat, name='allProdCat-old'),
    path('category/<slug:c_slug>/', views.allProdCat, name='by_category'),
    path('filter/', views.filter_product_list, name='allProdCat'),
     path('review/<int:pk>/edit/', views.edit_review, name='edit_review'),
]
