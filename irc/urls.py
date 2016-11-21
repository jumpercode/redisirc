
from django.conf.urls import url
from django.contrib import admin
from main.views import *

urlpatterns = [
	url(r'^$', inicio, name = 'inicio'),
    url(r'^admin/', admin.site.urls),
    url(r'^salas/', list_sala, name='list-sala'),

    url(r'^registro/$', registro, name='register'),
    url(r'^login/$', login, name='login'),
    url(r'^logon$', logon, name='logon'),
    url(r'^salas-add$', add_sala, name='add-salas'),
    url(r'^enviarM$', enviarM, name='enviarM'),
    url(r'^recibirM$', recibirM, name='recibirM'),
    url('^logout$', logout, name='logout'),
    url(r'^cambiar_sala/', Cambiar_sala, name="Cambiar_sala"),
    url(r'^cambiasala/(?P<id_sala>\d+)/$', Cambiasala, name="Cambiasala"),

]
