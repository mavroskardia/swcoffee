import sys
import sqlite3
from people_manager import PeopleManager

class Team(object):

	def __init__(self, name, description):
		self.name = name
		self.description = description

	def asjson(self):
		return {'name': self.name, 'description': self.description }

	def __repr__(self):
		return '%s | %s' % (self.name, self.description)

class TeamManager(object):
	def __init__(self, db='teams.db'):
		self.db = sqlite3.connect(db)
		self.db.execute('create table if not exists teams (name text not null, description text, unique (name))')
		self.teams = self.retrieve()

	def retrieve(self):		
		rows = self.db.execute('select * from teams')
		return [self.make_from_row(row) for row in rows]

	def make_from_row(self, row):
		return Team(row[0], row[1])

	def add(self, name, description):
		t = Team(name, description)
		self.teams.append(t)

	def remove(self, name):
		eligible = [t for t in self.teams if t.name == name]
		for e in eligible:
			self.teams.remove(e)

	def find(self, name):
		return [t for t in self.teams if name in t.name]

	def print(self):
		for t in self.teams:
			print(t)

	def commit(self):
		self.db.execute('delete from teams')
		for t in self.teams:
			try:
				self.db.execute('insert into teams values (?, ?)', (t.name, t.description))
			except sqlite3.IntegrityError:
				print('failed to add %s because it already exists' % t.name)			
		self.db.commit()

	def clear(self):
		self.db.execute('drop table if exists teams')
		self.db.commit()

if __name__ == '__main__':
	tm = TeamManager()

	if (len(sys.argv) == 4 and sys.argv[1] == 'add'):
		tm.add(sys.argv[2], sys.argv[3])
		tm.commit()
	elif (len(sys.argv) == 3 and sys.argv[1] == 'remove'):
		tm.remove(sys.argv[2])
		tm.commit()
	elif (len(sys.argv) == 2 and sys.argv[1] == 'print'):
		tm.print()
	elif (len(sys.argv) == 2 and sys.argv[1] == 'clear'):
		tm.clear()
	else:
		print('usage: add/remove/print/clear')