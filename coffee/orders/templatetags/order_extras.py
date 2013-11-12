from django import template
from django.db.models import Count, Min, Sum, Max, Avg

register = template.Library()

@register.inclusion_tag('item_collection.html')
def show_item_collection(items, can_delete, *columns):
	return {'items':items,'columns':columns,'can_delete':can_delete}

@register.inclusion_tag('order_item.html')
def show_order_item(item, can_delete, columns):
	return {'item':item,'can_delete':can_delete,'columns':columns}

@register.inclusion_tag('order_totals.html')
def show_order_totals(order, action_text):
	return {'order':order, 'action_text':action_text}

@register.inclusion_tag('person_total_for_order.html')
def person_total(person, order):
	total = 0.0
	for item in order.orderitem_set.filter(person=person.id,personal=True):
		total += float(item.value() or 0.0)
	if person.team == order.team:
		total += float(order.team_individual_contribution())
	return {'total':total}

@register.inclusion_tag('person_paid.html')
def person_paid(items):
	return {'paid':sum([i.paid for i in items])}

@register.inclusion_tag('coffee_values.html')
def coffee_values(orderitems):
	one = [o for o in orderitems if o.size is 1]
	two = [o for o in orderitems if o.size is 2]
	five = [o for o in orderitems if o.size is 5]

	oneq = sum([q.quantity for q in one])
	twoq = sum([q.quantity for q in two])
	fiveq = sum([q.quantity for q in five])

	return {
		'one': one,
		'oneq': oneq,
		'two': two,
		'twoq': twoq,
		'five': five,
		'fiveq': fiveq,
		'totallbs': oneq + (2*twoq) + (5*fiveq)
	}

