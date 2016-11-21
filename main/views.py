from django.shortcuts import render, redirect
from .models import Salas, Usuario, Mensaje
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
import hashlib
import json
from redis.sentinel import Sentinel

_limite_ = 10

def Cambiar_sala(request ,id=None):
    sala=Salas.objects.all()
    return render(request, 'main/cambiar_sala.html', {'sala': sala })  

def Cambiasala(request ,id_sala):
	request.session['sala'] = str(id_sala)
	return redirect('/salas')       

def inicio(request):
    return render(request, 'main/inicio.html')

def list_sala(request):

	if('nick' in request.session.keys()):
		return render(request, 'main/list_salas.html', {'nick': request.session['nick'], 'sala': request.session['sala']})
	else:
		return redirect('/login')

def add_sala(request):
	if request.method == 'POST':

		sala = Salas()
		sala.nombre = request.POST['nombre']
		sala.save()
	return render(request, 'main/add_sala.html')

def logout(request):
    auth.logout(request)
    return redirect("/")

def login(request):
	salas = Salas.objects.all()
	return render(request, 'main/login.html', {'salas':salas})

def logon(request):
	if request.method == 'POST':

		ust = Usuario.objects.get(nick=request.POST['nick'])
		if(ust):

			cif = hashlib.sha512()
			cif.update(request.POST['password'].encode('utf8'))

			quqo = cif.hexdigest()

			if(ust.password == quqo):
				request.session['nick'] = request.POST['nick']
				request.session['sala'] = request.POST['sala']
				return redirect('/salas')
	else:
		return redirect('/login')

def registro(request):
	if request.method == 'POST':
		cif = hashlib.sha512()
		cif.update(request.POST['password'].encode('utf8'))

		quqo = cif.hexdigest()
		print(quqo)

		usuario = Usuario()
		usuario.nick = request.POST['nick']
		usuario.password = quqo
		usuario.save()

	return render(request, 'main/register.html')

@csrf_exempt
def enviarM(request):
	if request.method == 'POST':
		data = json.loads(request.body.decode('utf8'))

		try:
			sentinel = Sentinel([('10.14.0.12', 26379), ('10.14.0.13', 26379), ('10.14.0.14', 26379) ], socket_timeout=0.5, password='upc2016')
			r = sentinel.master_for('mymaster', socket_timeout=0.5)
			ro = {'nick':data['nick'], 'msg':data['mensaje']}
			print(ro)
			r.rpush(data['sala'], json.dumps(ro))
			tama = r.llen(data['sala'])
			print("===========", tama)
			if(tama > _limite_ ):

				tocong = r.lrange(data['sala'], 0, _limite_-1)
				r.ltrim(data['sala'], _limite_, -1)

				for m in tocong:

					obj = json.loads(m.decode('utf8'))
					usuario=Usuario.objects.get(nick=obj['nick'])

					mensaje = Mensaje()
					mensaje.usuario_id = usuario.id

					mensaje.salas_id = data['sala']
					mensaje.mensaje = obj['msg']
					mensaje.save()

			dic = {'status': 'ok!'}

			return HttpResponse(json.dumps(dic), content_type='application/json')
		except Exception as ex:
			print("=========================", ex)
			dic = {'status': str(ex)}
			return HttpResponse(json.dumps(dic), content_type='application/json')

	else:
		dic = {'status': 'then request must be a POST type'}
		return HttpResponse(json.dumps(dic), content_type='application/json')

@csrf_exempt
def recibirM(request):

	if request.method == 'POST':
		data = json.loads(request.body.decode('utf8'))
		mcont = int(data['mcont'])
		try:
			sentinel = Sentinel([('10.14.0.12', 26379), ('10.14.0.13', 26379), ('10.14.0.14', 26379) ], socket_timeout=0.5, password='upc2016')
			r = sentinel.slave_for('mymaster', socket_timeout=0.5)

			total = r.llen(data["sala"])
			if(mcont == total):
				dic = {'status': 'No new msg.'}
			elif(mcont < total):
				lista = r.lrange(data["sala"], mcont, -1)
				dump = []
				for l in lista:
					tmp =  json.loads(l.decode('utf8'))
					dump.append(tmp)
				dic = {'status': 'News: '+str(total - mcont), 'mcont': total, 'lista': dump}
			else:
				dif = _limite_ -  mcont

				msm = Mensaje.objects.all().order_by("-id")[:dif]
				dump = []
				for l in msm:
					tmp =  {'msg': l.mensaje, 'nick': l.usuario.nick}
					dump.append(tmp)

				lista = r.lrange(data["sala"], 0, -1)
				for l in lista:
					tmp =  json.loads(l.decode('utf8'))
					dump.append(tmp)

				mact =  r.llen(data["sala"])
				dic = {'status': 'News: '+str(dif + mact), 'mcont': mact, 'lista': dump}


			return HttpResponse(json.dumps(dic), content_type='application/json')

		except Exception as ex:
			print(ex)
			dic = {'status': str(ex)}
			return HttpResponse(json.dumps(dic), content_type='application/json')

	else:
		dic = {'status': 'then request must be a POST type'}
		return HttpResponse(json.dumps(dic), content_type='application/json')
