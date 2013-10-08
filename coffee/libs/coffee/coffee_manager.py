import sys
import sqlite3
try:
	import http.client as http
except:
	import httplib as http

import base64

from html.parser import HTMLParser
from bs4 import BeautifulSoup

class Coffee(object):

	def __init__(self):
		self.name = 'no name'
		self.description = 'no desc'
		self.one_pound_price = 0.00
		self.two_pound_price = 0.00
		self.five_pound_price = 0.00
		self.prices = { 1: self.one_pound_price, 2: self.two_pound_price, 3: self.five_pound_price }
		self.image_data = None

	def __repr__(self):
		return '%s:\n\t%s\n\t(%s, %s, %s)' % (self.name, self.description, self.one_pound_price, self.two_pound_price, self.five_pound_price)

class CoffeeManager(object):

	# 16 different prices recorded on the website right now. i have no idea what the wholesale translation is 
	OnePoundPrices = {'$12.95': 8.75, '$13.95': 9.75, '$14.95': 9.50, '$14.45': 9.50}
	TwoPoundPrices = {'$24.15': 8.50*2, '$24.95': 8.50*2, '$24.75': 8.50*2, '$28.20': 8.50*2, '$25.70': 8.50*2, '$26.70': 8.50*2}
	FivePoundPrices = {'$59.15': 8.25*5, '$59.00': 8.25*5, '$70.50': 9.25*5, '$60.35': 9.25*5, '$63.35': 9.25*5, '$63.65': 9.25*5}

	def __init__(self, db='coffee.db'):
		self.db = sqlite3.connect(db)
		self.db.execute('CREATE TABLE if not exists coffee (name text, description text, one_pound_price real, two_pound_price real, five_pound_price real, image text, unique (name))')
		self.coffee = self.retrieve()

	def retrieve(self):
		rows = self.db.execute('SELECT * FROM coffee')
		return [self.make_coffee(row) for row in rows]

	def make_coffee(self, row):
		'''makes a coffee object from the db row'''
		c = Coffee()
		c.name = row[0]
		c.description = row[1]
		c.one_pound_price = CoffeeManager.OnePoundPrices[row[2]]
		c.two_pound_price = CoffeeManager.TwoPoundPrices[row[3]]
		c.five_pound_price = CoffeeManager.FivePoundPrices[row[4]]
		c.prices = {1: c.one_pound_price, 2: c.two_pound_price, 5: c.five_pound_price }
		c.image_data = row[5]

		return c

	def print(self):
		'''prints the current coffee list. will display:
the latest in the db prior to an update
the current in-memory coffee list after an update but before a commit
'''
		for c in self.coffee: print(c)

	def commit(self):
		for c in self.coffee:
			self.db.execute('INSERT INTO coffee VALUES (?, ?, ?, ?, ?, ?)', (c.name, c.description, c.one_pound_price, c.two_pound_price, c.five_pound_price, c.image_data))

		self.db.commit()

	def find(self, search):
		return [c for c in self.coffee if search in c.name]

	def update(self):
		page = None
		coffee = []

		pages = [
			'/coffees/',
			'/coffees/?u=&ss=&CustProds=&ProdGrpID=&submit_group=10',
			'/coffees/?u=&ss=&CustProds=&ProdGrpID=&submit_group=20',
			'/coffees/?u=&ss=&CustProds=&ProdGrpID=&submit_group=30'
		]

		for p in pages:
			print('processing page...', end='')
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

			print('done. found %s coffees.' % len(pagecoffee))

			for p in pagecoffee:
				image_data = self.get_image_data(p[0]['src'].replace('_thumb', ''))
				coffee.append(self.make_coffee((p[1][0], p[1][1], p[1][2][0], p[1][2][1], p[1][2][2], image_data)))

		print(len(coffee))

		self.coffee = coffee

	def get_image_data(self, url):
		c = http.client.HTTPConnection('sweetwatercoffee.e-beans.net')
		c.request('GET', url)
		resp = c.getresponse()
		assert resp.status == 200
		image_data = base64.b64encode(resp.read())
		c.close()
		return image_data

if __name__ == '__main__':
	cm = CoffeeManager('coffee.db')

	if len(sys.argv) == 2:
		if sys.argv[1] == 'update':
			cm.update()
			cm.commit()
		else:
			cm.print()
	else:
		cm.print()



