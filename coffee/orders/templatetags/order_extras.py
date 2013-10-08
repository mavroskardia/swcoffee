from django import template

register = template.Library()

@register.inclusion_tag('order_item.html')
def show_order_item(item):
	return {'item':item}



