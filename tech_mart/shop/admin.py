from django.contrib import admin
from .models import Product,Category,ProductImage,Brand,Review
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}
    list_per_page=20
admin.site.register(Product,ProductAdmin)
class CategoryAdmin(admin.ModelAdmin):
    list_display=['name','slug']
    prepopulated_fields={'slug':('name',)}
admin.site.register(Category,CategoryAdmin)
admin.site.register(ProductImage)
admin.site.register(Brand)
admin.site.register(Review)
