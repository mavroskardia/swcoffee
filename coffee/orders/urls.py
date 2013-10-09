from django.conf.urls import patterns, url

from orders import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^latest/$', views.latest, name='latest'),
	url(r'^(?P<order_id>\d+)/detail/$', views.detail, name='detail'),
	url(r'^(?P<order_id>\d+)/placed/$', views.placed, name='placed'),
	url(r'^(?P<order_id>\d+)/place/$', views.place, name='place'),
	url(r'^(?P<order_id>\d+)/close/$', views.close, name='close'),
	url(r'^(?P<order_id>\d+)/closed/$', views.closed, name='closed'),
	url(r'^(?P<order_id>\d+)/recalculate/$', views.recalculate, name='recalculate'),
	url(r'^(?P<item_id>\d+)/delete_item/$', views.delete_item, name='delete_item'),
	url(r'^teams/$', views.teams, name='teams'),
	url(r'^coffee/$', views.coffee, name='coffee'),
	url(r'^people/$', views.people, name='people'),
	url(r'^coffee/generate/$', views.generate_coffee, name='generate_coffee'),
)
