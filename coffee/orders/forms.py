from django import forms
from orders.models import Order,OrderItem,Team,Person,Coffee

class OrderForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A unique name for this order'}))
	team = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control'}), queryset=Team.objects.all())
	class Meta:
		model = Order
		exclude = ('placed', 'closed')

class OrderItemForm(forms.ModelForm):
	person = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control'}), queryset=Person.objects.all())
	coffee = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control'}), queryset=Coffee.objects.filter(active=True))
	size = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=((1,1),(2,2),(5,5)))
	quantity = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6)))
	personal = forms.BooleanField(required=False)

	class Meta:
		model = OrderItem
		exclude = ('order','paid')

class TeamForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A unique name for this team'}))
	description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description of the team'}))

	class Meta:
		model = Team

class PersonForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A unique name for this person'}))
	team = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control'}), queryset=Team.objects.all())

	class Meta:
		model = Person

class CoffeeForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A unique name for this coffee'}))
	description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description of the coffee'}))
	one_pound_price = forms.DecimalField(min_value=0.0,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Price for a single pound bag'}))
	two_pound_price = forms.DecimalField(min_value=0.0,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Price for a two pound bag'}))
	five_pound_price = forms.DecimalField(min_value=0.0,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Price for a five pound bag'}))
	image = forms.ImageField()
	active = forms.BooleanField()

	class Meta:
		model = Coffee
