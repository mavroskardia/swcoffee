

class BaseManager(object):
	'''eventual refactoring of the other managers'''
	
	def __init__(self, db, tablename, columns):
		self.db = sqlite3.connect(db)
		self.tablename = tablename
		self.createdb(tablename, columns)		
		self.objects = self.retrieve()

	def createdb(self, tablename, columns):
		self.db.execute('create table if not exists %s (%s)' % (', '.join(columns)))

	def retrieve(self):
		objects = [
		rows = self.db.execute('select * from %s' % self.tablename)
		for row in rows:
			objects.append(self.make_from_row(row))
		return objects
