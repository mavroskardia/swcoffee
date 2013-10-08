try:
	import http.client as http
except:
	import httplib as http

import base64
from orders.models import Coffee

try:
	from html.parser import HTMLParser
except:
	from HTMLParser import HTMLParser

from bs4 import BeautifulSoup

def scrape(update_function=None):
	page = None
	coffee = []

	pages = [
		'/coffees/',
		'/coffees/?u=&ss=&CustProds=&ProdGrpID=&submit_group=10',
		'/coffees/?u=&ss=&CustProds=&ProdGrpID=&submit_group=20',
		'/coffees/?u=&ss=&CustProds=&ProdGrpID=&submit_group=30'
	]

	for p in pages:
		c = http.HTTPConnection('sweetwatercoffee.e-beans.net')
		c.request('GET', p)
		resp = c.getresponse()
		assert resp.status == 200
		page = resp.read().decode('utf-8')
		c.close()

		table = BeautifulSoup(page).select('#store-grid-table')[0]

		pics = table.find_all('img')
		text = []

		for cell in table.select('.store-grid-description'):
			atags = cell.find_all('a')
			if not atags: continue

			name = atags[0]['title']
			desc = ' '.join([i for i in cell.contents if isinstance(i, str) and i != '\n']).encode('utf-8')
			prices = [e.get_text().strip().split(' ')[-1] for e in cell.find_all('select')[0].find_all('option')]
			
			text.append((name, desc, prices))

		pagecoffee = list(zip(pics, text))

		for p in pagecoffee:
			image_data = get_image_data(p[0]['src'].replace('_thumb', ''))
			coffee.append(make_coffee((p[1][0], p[1][1], p[1][2][0], p[1][2][1], p[1][2][2], image_data)))
			if update_function:
				update_function(coffee[-1])

	return coffee

def make_coffee(row):
	'''makes a coffee object from the db row'''

	OnePoundPrices = {'$12.95': 8.75, '$13.95': 9.75, '$14.95': 9.50, '$14.45': 9.50}
	TwoPoundPrices = {'$24.15': 8.50*2, '$24.95': 8.50*2, '$24.75': 8.50*2, '$28.20': 8.50*2, '$25.70': 8.50*2, '$26.70': 8.50*2}
	FivePoundPrices = {'$59.15': 8.25*5, '$59.00': 8.25*5, '$70.50': 9.25*5, '$60.35': 9.25*5, '$63.35': 9.25*5, '$63.65': 9.25*5}

	c = Coffee()
	c.name = row[0]
	c.description = row[1]
	c.one_pound_price = OnePoundPrices[row[2]]
	c.two_pound_price = TwoPoundPrices[row[3]]
	c.five_pound_price = FivePoundPrices[row[4]]
	c.prices = {1: c.one_pound_price, 2: c.two_pound_price, 5: c.five_pound_price }
	c.image_data = row[5]

	return c

def get_image_data(url):
	c = http.HTTPConnection('sweetwatercoffee.e-beans.net')
	c.request('GET', url)
	resp = c.getresponse()
	assert resp.status == 200
	image_data = resp.read()
	c.close()
	return image_data
