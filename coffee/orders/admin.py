from django.contrib import admin
from orders.models import Order,OrderItem,Team,Person,Coffee,Payment

class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 1

class OrderAdmin(admin.ModelAdmin):
	fields = ['name', 'team', 'placed']
	inlines = [OrderItemInline]
	list_display = ('name', 'team', 'date')
	list_filter = ['date']
	search_fields = ['name']
	date_hierarchy = 'date'

class CoffeeAdmin(admin.ModelAdmin):
	list_display = ('name', 'one_pound_price', 'two_pound_price', 'five_pound_price')

admin.site.register(Order, OrderAdmin)
admin.site.register(Team)
admin.site.register(Person)
admin.site.register(Coffee, CoffeeAdmin)
admin.site.register(Payment)
