import os
from django.core.files.images import ImageFile
from io import BytesIO
from base64 import b64encode,b64decode
from django.db import models
from django.db.models import Sum

class Team(models.Model):
	name = models.CharField(max_length=128)
	description = models.CharField(max_length=1024)

	def __unicode__(self):
		return self.name
	def __str__(self):
		return self.__unicode__()

class Person(models.Model):
	name = models.CharField(max_length=128)
	team = models.ForeignKey(Team)

	def __unicode__(self):
		return self.name
	def __str__(self):
		return self.__unicode__()

class Coffee(models.Model):
	name = models.CharField(max_length=128)
	description = models.CharField(max_length=1024)
	one_pound_price = models.DecimalField(max_digits=5,decimal_places=2)
	two_pound_price = models.DecimalField(max_digits=5,decimal_places=2)
	five_pound_price = models.DecimalField(max_digits=5,decimal_places=2)
	image = models.ImageField(upload_to='images')

	class BadSizeException(Exception):
		pass

	def __unicode__(self):
		return self.name
	def __str__(self):
		return self.__unicode__()

	def value(self, pounds, quantity):
		if pounds == 1:
			return quantity * self.one_pound_price
		elif pounds == 2:
			return quantity * self.two_pound_price
		elif pounds == 5:
			return quantity * self.five_pound_price
		else:
			raise Coffee.BadSizeException

	def set_image(self, image_data):
		iof = BytesIO(image_data)
		self.image = ImageFile(iof)
		self.image.name = os.path.join('images', '%s.png' % self.name)

	def image_data_url(self):
		self.image.open()
		b64 = b64encode(self.image.read()).decode('utf-8')
		self.image.close()
		return 'data:image/png;base64,%s' % b64

class Order(models.Model):
	name = models.CharField(max_length=128,help_text="Name of this order")
	team = models.ForeignKey(Team,help_text="Team divides the non-personal total")
	date = models.DateField(auto_now_add=True)
	placed = models.BooleanField(default=False)
	closed = models.BooleanField(default=False)

	def team_total(self):
		return sum([i.value() for i in self.orderitem_set.filter(personal=False)])

	def personal_total(self):
		return sum([i.value() for i in self.orderitem_set.filter(personal=True)])

	def grand_total(self):
		return self.team_total() + self.personal_total()

	def team_individual_contribution(self):
		return self.team_total() / (self.team.person_set.count() or 1)

	def total_remaining(self):
		return self.grand_total() - self.total_paid()

	def total_paid(self):
		return self.payment_set.aggregate(Sum('paid'))['paid__sum']

	def __unicode__(self):
		return self.name
	def __str__(self):
		return self.__unicode__()

class OrderItem(models.Model):
	order = models.ForeignKey(Order)
	person = models.ForeignKey(Person)
	coffee = models.ForeignKey(Coffee)
	size = models.IntegerField(choices=((1,1), (2,2), (5,5)), default=1)
	quantity = models.IntegerField()
	personal = models.BooleanField(default=False)
	paid = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
	
	def value(self):
		return self.coffee.value(self.size, self.quantity)

	def as_csv(self):
		return ','.join([str(i) for i in [self.person.name,self.coffee.name,self.quantity,self.size,self.personal,self.value()]])

	def __unicode__(self):
		'''[person] placed [a|qty] [size] pound bag(s) of [coffee] for [team]'''
		#return u'{a.person} placed {a.quantity}x {a.size} pound bag(s) of {a.coffee} for {team_or_personal}'.format(a=self, team_or_personal='him/herself' if self.personal else self.person.team)
		return u'{a.quantity} {a.coffee} ({a.size} - {a.person} | {team_or_personal}): {v}'.format(v=self.value(),a=self, team_or_personal='him/herself' if self.personal else self.person.team)
	def __str__(self):
		return self.__unicode__()

class Payment(models.Model):
	order = models.ForeignKey(Order)
	person = models.ForeignKey(Person)
	owed = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
	paid = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)

	def __unicode__(self):
		return '%s: (%s) %s' % (self.person.name, self.owed, self.paid)

	def __str__(self):
		return self.__unicode__()
