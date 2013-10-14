import django.utils.timezone

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from orders.models import Order,Team,Person,Coffee,OrderItem
from orders.forms import OrderForm,OrderItemForm,TeamForm,CoffeeForm,PersonForm

import orders.sweetwaterscraper

def index(req):

	if req.method == 'POST':
		orderform = OrderForm(req.POST)
		if orderform.is_valid():
			try:
				o = orderform.save()
			except IntegrityError as e:
				messages.error(req, e)
				return HttpResponseRedirect(reverse('orders:index'))

			return HttpResponseRedirect(reverse('orders:detail', args=(o.id,)))
	else:
		orderform = OrderForm()

	return render(req,
		'orders/index.html', {
			'title': 'Coffee Ordering',
			'allorders': Order.objects.all(),
			'orderform': orderform
		}
	)

def latest(req):
	try:
		order = Order.objects.latest('date')
	except Order.DoesNotExist as e:
		messages.error(req, 'No latest order yet!')
		return HttpResponseRedirect(reverse('orders:index'))

	return HttpResponseRedirect(reverse('orders:detail', args=(order.id,)))

def delete_item(req, item_id):

	if req.method != 'POST':
		messages.error(req, 'Cannot delete by GET')
		return HttpResponseRedirect(reverse('orders:index'))

	order_item = get_object_or_404(OrderItem, pk=item_id)
	order_id = order_item.order_id

	order_item.delete()

	messages.info(req, 'Removed item')

	return HttpResponseRedirect(reverse('orders:detail', args=(order_id,)))

def detail(req, order_id):

	order = get_object_or_404(Order, pk=order_id)

	if order.placed:
		return HttpResponseRedirect(reverse('orders:placed', args=(order_id,)))

	if order.closed:
		return HttpResponseRedirect(reverse('orders:closed', args=(order_id,)))

	if req.method == 'POST':
		orderform = OrderItemForm(req.POST)
		if orderform.is_valid():
			oi = orderform.save(commit=False)
			oi.order_id = order_id

			if oi.person.team != oi.order.team:
				oi.personal = True
				messages.warning(req, '%s is not on team %s, forcing order to personal' % (oi.person.name, oi.order.team))

			oi.save()
	else:
		orderform = OrderItemForm()

	return render(req,
		'orders/detail.html', {
			'title': 'Order %s' % order.name,
			'order': order,
			'orderform': orderform,
			'teamitems': order.orderitem_set.filter(personal=False),
			'personalitems': order.orderitem_set.filter(personal=True) 
		}
	)

def placed(req, order_id):

	order = get_object_or_404(Order, pk=order_id)

	if order.closed:
		return HttpResponseRedirect(reverse('orders:closed', args=(order_id,)))

	return render(req,
		'orders/placed.html', {
			'title': 'Placed Order %s' % order.name,
			'order': order
		}
	)

def place(req, order_id):
	if req.method == 'POST':
		o = get_object_or_404(Order, pk=order_id)
		o.placed = True
		o.save()

		return HttpResponseRedirect(reverse('orders:placed', args=(order_id,)))

	messages.error(req, 'Cannot place an order this way')
	return HttpResponseRedirect(reverse('orders:detail', args=(order_id,)))

def close(req, order_id):
	if req.method == 'POST':
		o = get_object_or_404(Order, pk=order_id)
		o.closed = True
		o.save()

		return HttpResponseRedirect(reverse('orders:closed', args=(order_id,)))

	messages.error(req, 'Cannot close an order this way')
	return HttpResponseRedirect(reverse('orders:placed', args=(order_id,)))

def closed(req, order_id):
	order = get_object_or_404(Order, pk=order_id)

	if not order.closed:
		return HttpResponseRedirect(reverse('orders:detail', args=(order_id,)))

	people_who_ordered = set([oi.person.name for oi in order.orderitem_set.all()])
	leftover_people = order.team.person_set.exclude(name__in=people_who_ordered)

	return render(req,
		'orders/closed.html', {
			'title': 'Closed Order %s' % order.name,
			'order': order,
			'sorteditems': order.orderitem_set.all().order_by('person'),
			'leftoverpeople': leftover_people
		}
	)

def recalculate(req, order_id):
	order = get_object_or_404(Order, pk=order_id)

	return HttpResponseRedirect(reverse('orders:closed', args=(order_id,)))

def teams(req):

	if req.method == 'POST':
		tf = TeamForm(req.POST)
		if tf.is_valid():
			team  = tf.save()
		return render(req,
				'orders/teams.html', {
					'title': 'Teams',
					'teams': Team.objects.all(),
					'tf': tf
				})
	else:
		tf = TeamForm()
	return render(req,
		'orders/teams.html', {
			'title': 'Teams',
			'teams': Team.objects.all(),
			'tf': tf
		}
	)

def coffee(req):
	if req.method == 'POST':
		cf = CoffeeForm(req.POST)
		if cf.is_valid():
			coffee = cf.save()
			return HttpResponseRedirect(reverse('orders:coffee'))
	else:
		cf = CoffeeForm()
	return render(req,
		'orders/coffee.html', {
			'title': 'Coffee',
			'coffee': Coffee.objects.all(),
			'cf': cf
		}
	)

def people(req):

	if req.method == 'POST':
		pf = PersonForm(req.POST)
		if pf.is_valid():
			person = pf.save()
	else:
		pf = PersonForm()

	return render(req,
		'orders/people.html', {
			'title': 'People',
			'people': Person.objects.all(),
			'pf': pf 
		}
	)

def generate_coffee(req):
	def create_coffee(coffee):
		# skip duplicates
		if Coffee.objects.filter(name=coffee.name).count() > 0:
			messages.warning(req, 'Skipped "%s" since a coffee with that name already exists' % coffee.name)
			return
		
		c = Coffee()
		c.name = coffee.name
		c.description = coffee.description
		c.one_pound_price = coffee.one_pound_price
		c.two_pound_price = coffee.two_pound_price
		c.five_pound_price = coffee.five_pound_price
		c.set_image(coffee.image_data)

		c.save()

	orders.sweetwaterscraper.scrape(create_coffee)

	return HttpResponseRedirect(reverse('orders:coffee'))
