import sys
import sqlite3
import json
import datetime
import locale

from people_manager import PeopleManager, Person
from team_manager import TeamManager, Team
from coffee_manager import CoffeeManager, Coffee

locale.setlocale(locale.LC_ALL, '')

class OrderJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Order):
			print('serializing order')
			return { 'name': obj.name, 'team': obj.team, 'date': obj.date.isoformat(), 'items': obj.items}
		elif isinstance(obj, Team):
			print('serializing team')
			return { 'name': obj.name, 'description': obj.description }
		elif isinstance(obj, Item):
			print('serializing item')
			return { 'person': obj.person.name, 'coffee': obj.coffee.name, 'pounds': obj.pounds, 'quantity': obj.quantity, 'personal': obj.personal }
		else:
			return []

class Order(object):
	
	def __init__(self):
		self.name = '<no name>'
		self.team = '<no team>'
		self.date = datetime.datetime.now()
		self.items = []

	def __repr__(self):
		rep = []

		rep.append('%s for %s (%s)' % (self.name, self.team, self.date.strftime('%Y-%m-%d')))
		
		return '\n'.join(rep)

class Item(object):

	def __init__(self, person, coffee, pounds, quantity, personal=False):
		self.person = person
		self.coffee = coffee
		self.pounds = pounds
		self.quantity = quantity
		self.personal = personal

	def __repr__(self):
		return '\t%s: %sx %slb(s) of %s (%s)' % (self.person.name, self.quantity, self.pounds, self.coffee.name, 'Personal' if self.personal else 'part of team order')

class OrderManager(object):
	'''Manages orders'''

	def __init__(self, db='orders.db'):
		self.pm = PeopleManager()
		self.tm = TeamManager()
		self.cm = CoffeeManager()

		self.db = sqlite3.connect(db)
		self.db.execute('create table if not exists orders (name text, document text, unique (name))')
		self.orders = self.retrieve()

	def retrieve(self):
		rows = self.db.execute('select * from orders')
		return [self.make_from_row(row) for row in rows]

	def add(self, name, team):
		team = self.find_team(team)
		o = Order()
		o.name = name
		o.team = team
		self.orders.append(o)

	def create_item(self, person, coffee, pounds, quantity, personal):
		return Item(person, coffee, pounds, quantity, personal)

	def add_item(self, order, person, coffee, lbs, qty, personal):
		o = self.find(order)
		p = self.pm.find(person)
		c = self.cm.find(coffee)

		if len(o) != 1:
			#print('Did not find a unique order match for "%s"' % order)
			return False

		o = o[0]

		if len(p) != 1:
			#print('Did not find a unique person match for "%s"' % person)
			return False

		p = p[0]

		if len(c) != 1:
			#print('Did not find a unique coffee match for "%s"' % coffee)
			return False

		# TODO remove the list/obj inconsistencies so stuff like this can go away
		if isinstance(o.team, list): o.team = o.team[0]
		if isinstance(p.team, list): p.team = p.team[0]

		if o.team.name != p.team:
			#print('%s is not on team %s, forcing personal order' % (p.name, o.team))
			personal = True

		item = self.create_item(p, c[0], lbs, qty, personal)
		o.items.append(item)

		return True

	def remove_item(self, order, who, coffee):
		o = self.find(order)[0]
		who = self.pm.find(who)[0]
		c = self.cm.find(coffee)[0]

		allitems = [i for i in o.items]
		
		eligible = [i for i in o.items if i.person.name == who.name and i.coffee.name == c.name]

		#print('Found %s coffee to remove' % len(eligible))

		for e in eligible:
			o.items.remove(e)

	def update_item(self, order, who, coffee, pounds, quantity):
		o = self.find(order)[0]
		who = self.pm.find(who)[0]

		eligible = [i for i in o.items if i.person.name == who.name and i.coffee.name == coffee]

		if len(eligible) > 1:
			raise Exception('Too many matching items (%s) to update' % len(eligible))

		c = eligible[0]

		c.quantity = quantity
		c.pounds = pounds		

	def find(self, search):
		return [o for o in self.orders if search in o.name]

	def find_team(self, teamname):
		team = self.tm.find(teamname)
		if len(team) != 1:
			print('failed to find a unique team with search "%s"' % teamname)
			return None
		return team

	def remove(self, name):
		eligible = [o for o in self.orders if o.name == name]
		for e in eligible:
			self.orders.remove(e)

	def commit(self):
		self.db.execute('delete from orders')
		for o in self.orders:
			try:
				self.db.execute('insert into orders values (?, ?)', (o.name, json.dumps(o, cls=OrderJSONEncoder)))
			except sqlite3.IntegrityError:
				print('failed to add order "%s" because an order with that name already exists' % o.name)
		self.db.commit()

	def print(self):
		for o in self.orders:
			print(o)

	def clear(self):
		self.db.execute('drop table orders')
		self.db.commit()

	def make_from_row(self, row):
		name = row[0]
		return self.deserialize(row[1])

	def deserialize(self, doc):
		doc = json.loads(doc)
		o = Order()
		o.name = doc['name']
		o.date = datetime.datetime.strptime(doc['date'], '%Y-%m-%dT%H:%M:%S.%f')

		if isinstance(doc['team'], list):
			doc['team'] = doc['team'][0]
		
		o.team = Team(doc['team']['name'], doc['team']['description'])
		
		for i in doc['items']:
			p = self.pm.find(i['person'])[0]
			c = self.cm.find(i['coffee'])[0]
			lbs = i['pounds']
			qty = i['quantity']
			item = Item(p, c, lbs, qty, i['personal'])
			o.items.append(item)
		
		return o

	def teamtotal(self, order):
		return sum([(i.quantity * i.coffee.prices[i.pounds]) for i in order.items if not i.personal])

	def personaltotal(self, order):
		return sum([(i.quantity * i.coffee.prices[i.pounds]) for i in order.items if i.personal])

	def grandtotal(self, order):
		return self.teamtotal(order) + self.personaltotal(order)

	def individualtotal(self, order, who):
		'''if on team: teamtotal / numonteam + personalorder, otherwise: personalorder'''
		summo = 0
		who = self.pm.find(who)[0]

		if order.team.name == who.team:
			num_on_team = len([p for p in self.pm.people if p.team == order.team.name])			
			summo = self.teamtotal(order) / float(num_on_team)
			summo += sum([i.quantity*i.coffee.prices[i.pounds] for i in order.items if i.personal and i.person.name == who.name])
		else:
			summo = sum([i.quantity * i.coffee.prices[i.pounds] for i in order.items if i.personal and i.person.name == who.name])

		return summo

	def totals(self, order):
		cur = locale.currency
		s = []
		o = self.find(order)[0]
		s.append('''
	Team Total......%s
	Personal Total..%s
	Grand Total.....%s
	Individual Totals:''' % (cur(self.teamtotal(o)), cur(self.personaltotal(o)), cur(self.grandtotal(o))))
		unique_people = set([i.person.name for i in o.items])
		for p in unique_people:
			s.append('\t%s: %s' % (p, locale.currency(self.individualtotal(o, p))))
	
		return ''.join(s)

class OrderManagerConsole(object):

	def __init__(self, om):
		self.om = om
		self.done = False
		self.actions = {
			'exit': self.exit,
			'new order': self.new_order,
			'new person': self.new_person,
			'new team': self.new_team,
			'commit all': self.commit_all,
			'orders': self.print_orders,
			'teams': self.print_teams,
			'people': self.print_people,
			'coffee': self.print_coffee,
			'add to order': self.add_to_order,
			'clear all': self.clear_all,
			'totals': self.totals,
			'remove item': self.remove_item,
			'update item': self.update_item
		}

	def noaction(self, command):
		print('invalid command: %s' % command)

	def exit(self, command): self.done = True
	def print_orders(self, command): self.om.print()
	def print_teams(self, command): self.om.tm.print()
	def print_people(self, command): self.om.pm.print()
	def print_coffee(self, command): self.om.cm.print()

	def new_order(self, command):
		name = input('Order Name: ')
		team = input('Team: ')		
		self.om.add(name, team)
	
	def commit_all(self, command):
		self.om.pm.commit()
		self.om.tm.commit()
		self.om.commit()

	def clear_all(self, command):
		self.om.pm.clear()
		self.om.tm.clear()
		self.om.clear()
	
	def new_team(self, command):
		name = input('Team Name: ')
		description = input('Description: ')
		self.om.tm.add(name.strip(), description.strip())
	
	def new_person(self, command):
		name = input('Name: ')
		description = input('Team: ')
		self.om.pm.add(name, description)

	def add_to_order(self, command):
		order = input('Order: ')
		who = input('For whom: ')
		what = input('Coffee: ')
		lbs = input('Pounds: ')
		qty = input('How many: ')
		pers = input('Personal: ')

		self.om.add_item(order, who, what, lbs, qty, pers == 'y')

	def remove_item(self, command):
		order = input('Order: ')
		who = input('Who: ')
		coffee = input('Coffee: ')

		self.om.remove_item(order, who, coffee)

	def update_item(self, command):
		order = input('Order: ')
		who = input('Who: ')
		coffee = input('Coffee: ')
		lbs = input('Pounds: ')
		qty = input('How many: ')

		self.om.update_item(order, who, coffee, quantity, pounds)

	def totals(self, command):		
		print(self.om.totals(input('Order: ')))
		
	def run(self):
		while not self.done:			
			command = input('> ')
			self.actions.get(command, self.noaction)(command)

class OrderManagerTester(object):

	def __init__(self, order_manager):
		self.om = order_manager

		self.mock_teams = [
			self.create_team('Team1'),
			self.create_team('Team2'),
			self.create_team('Team3')
		]

		self.mock_people = [
			self.create_person('Andy', 'Team1'),
			self.create_person('Sarah', 'Team1'),
			self.create_person('Kyle', 'Team2')
		]

		self.mock_coffee = [
			self.create_coffee('Coffee1'),
			self.create_coffee('Coffee2'),
			self.create_coffee('Coffee3')
		]

	def create_person(self, name, team):
		return Person(name, team)

	def create_team(self, name):
		return Team(name, name+ ' Desc')

	def create_coffee(self, name):
		c = Coffee()
		c.name = name
		c.desc = name + ' desc'
		c.prices = {1: 1.00, 2: 2.00, 5: 5.00}
		return c

	def run(self):
		self.test_totals()

	def test_totals(self):
		self.om.pm.people = self.mock_people[:]
		self.om.tm.teams = self.mock_teams[:]
		self.om.cm.coffee = self.mock_coffee[:]

		self.om.add('mock order', 'Team1')

		o = self.om.find('mock')

		assert len(o) == 1

		o = o[0]
		
		assert o.name == 'mock order'

		self.om.add_item(o.name, 'Andy', '1', '5', '1', True) # Personal: $5

		assert self.om.grandtotal(o) == 5.00

		self.om.add_item(o.name, 'Andy', '2', '2', '2', False) # Team: $4

		assert self.om.grandtotal(o) == 9.00
		assert self.om.teamtotal(o) == 4.00, self.om.teamtotal(o)

		self.om.add_item(o.name, 'Kyle', '3', '1', '3', False) # Team ---- Personal! $3

		assert self.om.grandtotal(o) == 12.00, self.om.grandtotal(o)

		self.om.add_item(o.name, 'Sarah', '1', '2', '4', True) # Personal: $8
		self.om.add_item(o.name, 'Sarah', '2', '5', '5', False) # Team: $25
		
		assert self.om.grandtotal(o) == 45.00, self.om.grandtotal(o)
		assert self.om.teamtotal(o) == 29.00, self.om.teamtotal(o)
		assert self.om.personaltotal(o) == 5 + 3 + 8, self.om.personaltotal(o)
		assert self.om.individualtotal(o, 'Andy') == 29.00/2 + 5, str(self.om.individualtotal(o, 'Andy')) + ' != ' + str(29.00/2 + 5)
		assert self.om.individualtotal(o, 'Sarah') == 29.00/2 + 8, str(self.om.individualtotal(o, 'Sarah')) + ' != ' + str(29.00/2 + 8)
		assert self.om.individualtotal(o, 'Kyle') == 3, self.om.individualtotal(o, 'Kyle')

		assert self.om.grandtotal(o) == self.om.teamtotal(o) + self.om.personaltotal(o)

		it = self.om.individualtotal(o, 'Andy') + self.om.individualtotal(o, 'Sarah') + self.om.individualtotal(o, 'Kyle')

		assert self.om.grandtotal(o) == it, str(self.om.grandtotal(o)) + ' != ' + str(it)
		
if __name__ == '__main__':
	om = OrderManager()

	if (len(sys.argv) == 4 and sys.argv[1] == 'add'):
		om.add(sys.argv[2], sys.argv[3])
		om.commit()
	elif (len(sys.argv) == 3 and sys.argv[1] == 'remove'):
		om.remove(sys.argv[2])
		om.commit()
	elif (len(sys.argv) == 2 and sys.argv[1] == 'print'):
		om.print()
	elif (len(sys.argv) == 2 and sys.argv[1] == 'clear'):
		om.clear()
	elif (len(sys.argv) == 2 and sys.argv[1] == 'console'):
		OrderManagerConsole(om).run()
	elif (len(sys.argv) == 2 and sys.argv[1] == 'test'):
		OrderManagerTester(om).run()
	else:
		print('usage: add/remove/print/clear')