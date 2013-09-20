import sys
import sqlite3

class Person(object):

	def __init__(self, name, team):
		self.name = name
		self.team = team

	def __repr__(self):
		return '%s | Team: %s' % (self.name, self.team)

class PeopleManager(object):

	def __init__(self, db='people.db'):
		self.db = sqlite3.connect(db)
		self.db.execute('CREATE TABLE if not exists people (name text, team text, unique (name, team))')
		self.people = self.retrieve()

	def retrieve(self):		
		rows = self.db.execute('SELECT * FROM people')
		return [Person(row[0], row[1]) for row in rows]

	def add(self, name, team):
		p = Person(name, team)
		self.people.append(p)

	def remove(self, name, team):
		eligible = [p for p in self.people if p.name == name and p.team == team]
		for e in eligible:
			self.people.remove(e)

	def commit(self):
		self.db.execute('DELETE FROM people')
		for p in self.people:
			try:
				self.db.execute('INSERT INTO people VALUES(?, ?)', (p.name, p.team))
			except sqlite3.IntegrityError:
				print('skipping adding %s to team %s because (s)he is already on that team' % (p.name, p.team))
		self.db.commit()

	def find(self, search):
		return [p for p in self.people if search in p.name]

	def clear(self):
		self.db.execute('DROP TABLE if exists people')
		self.db.commit()

	def print(self):
		for p in self.people:
			print(p)

if __name__ == '__main__':
	pm = PeopleManager()

	if len(sys.argv) == 4 and sys.argv[1] == 'add':
		pm.add(sys.argv[2], sys.argv[3])
		pm.commit()
	elif len(sys.argv) == 4 and sys.argv[1] == 'remove':
		pm.remove(sys.argv[2], sys.argv[3])
		pm.commit()
	elif len(sys.argv) == 2 and sys.argv[1] == 'print':
		pm.print()
		pm.commit()
	elif len(sys.argv) == 2 and sys.argv[1] == 'clear':
		pm.clear()
	else:
		print('usage: add/remove/print')