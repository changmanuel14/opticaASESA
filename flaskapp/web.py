from flask import Flask, render_template, request, url_for, redirect, session, make_response
import pymysql
from datetime import date, timedelta
import datetime
import pdfkit
import cryptography

from werkzeug.utils import send_file

app = Flask(__name__)
app.secret_key = 'd589d3d0d15d764ed0a98ff5a37af547'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
@app.route('/home')
def home():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	return render_template('inicio.html', title="Inicio", logeado = logeado)

@app.route('/citas', methods=['GET', 'POST'])
def citas():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	fecha = datetime.datetime.now()
	d4 = fecha.strftime("%Y-%m-%d")
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT c.nombre, c.apellido, DATE_FORMAT(c.fecha,'%d/%m/%Y'), h.hora, c.telefono, c.idcitas from citas c inner join hora h on c.idhora = h.idhora where fecha >= '" + str(d4) + "' order by c.fecha asc, c.idhora asc;"
				cursor.execute(consulta)
				data = cursor.fetchall()
				consulta = "SELECT idhora, hora from hora;"
				cursor.execute(consulta)
				horas = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		fecha = request.form["fecha"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT c.nombre, c.apellido, DATE_FORMAT(c.fecha,'%d/%m/%Y'), h.hora, c.telefono, c.idcitas from citas c inner join hora h on c.idhora = h.idhora where fecha = '" + str(fecha) + "' order by c.idhora asc;"
					cursor.execute(consulta)
					data = cursor.fetchall()
					consulta = "SELECT idhora, hora from hora;"
					cursor.execute(consulta)
					horas = cursor.fetchall()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return render_template('citas.html', title="Citas", logeado = logeado, data=data, horas=horas)
	return render_template('citas.html', title="Citas", logeado = logeado, data=data, horas=horas)

@app.route('/nuevacita', methods=['GET', 'POST'])
def nuevacita():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idhora, hora from hora;"
				cursor.execute(consulta)
				horas = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		nombre = request.form["nombre"]
		apellido = request.form["apellido"]
		telefono = request.form["telefono"]
		fecha = request.form["fecha"]
		hora = request.form["hora"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "insert into citas(nombre, apellido, telefono, fecha, idhora) values(%s,%s,%s,%s,%s)"
					cursor.execute(consulta, (nombre, apellido, telefono, fecha,hora))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('citas'))
	return render_template('nuevacita.html', title="Nueva Cita", logeado = logeado, horas=horas)

@app.route('/ceditar/<idcita>', methods=['GET', 'POST'])
def ceditar(idcita):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idhora, hora from hora;"
				cursor.execute(consulta)
				horas = cursor.fetchall()
				consulta = "select nombre, apellido, telefono, fecha, idhora from citas where idcitas = "+idcita+";"
				print(consulta)
				cursor.execute(consulta)
				datacita = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		nombre = request.form["nombre"]
		apellido = request.form["apellido"]
		telefono = request.form["telefono"]
		fecha = request.form["fecha"]
		hora = request.form["hora"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "update citas set nombre = %s, apellido = %s, telefono = %s, fecha = %s, idhora = %s where idcitas = %s"
					cursor.execute(consulta, (nombre, apellido, telefono, fecha,hora, idcita))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('citas'))
	return render_template('ceditar.html', title="Editar Cita", logeado = logeado, horas=horas, datacita=datacita)

@app.route('/celiminar/<idcita>', methods=['GET', 'POST'])
def celiminar(idcita):
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "delete from citas where idcitas = "+idcita+";"
				cursor.execute(consulta)
			conexion.commit()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return redirect(url_for('citas'))

@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)

@app.route('/nuevaconsulta', methods=['GET', 'POST'])
def nuevaconsulta():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	dateac = date.today()
	year = dateac.strftime("%Y")
	year = int(year)
	new_date = dateac + timedelta(days=183)
	anios = []
	nervos = []
	nervo = 1
	for i in range(11):
		nervos.append(nervo*i)
	for i in range(80):
		anios.append(year)
		year = year - 1
	numeros = []
	numero = 0
	for i in range(36):
		numeros.append(numero)
		numero = numero + 1
	mms = []
	mm = 0
	for i in range(8):
		mms.append(mm)
		mm = mm + 5
	cincos = []
	cinco = 0
	for i in range(15):
		cincos.append(cinco)
		cinco = cinco + 5
	meses = [[1, "Enero"],[2, "Febrero"],[3, "Marzo"],[4, "Abril"],[5, "Mayo"],[6, "Junio"],[7, "Julio"],[8, "Agosto"],[9, "Septiembre"],[10, "Octubre"],[11, "Noviembre"],[12, "Diciembre"]]
	enfermedades = [['Diabetes Mellitus'],['Hipertensión Arterial'],['Artritis Reumatoidea'],['Virus Inmunodeficiencia Humana'],['Hipertrigliceridemia'],['Colesterolemia']]
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "select idsexo, sexo from sexo;"
				cursor.execute(consulta)
				sexo = cursor.fetchall()
				consulta = "select idusolen, uso from usolen;"
				cursor.execute(consulta)
				usolen = cursor.fetchall()
				consulta = "select idtipolen, tipo from tipolen;"
				cursor.execute(consulta)
				tipolen = cursor.fetchall()
				consulta = "select idmateriallen, material from materiallen;"
				cursor.execute(consulta)
				materiallen = cursor.fetchall()
				consulta = "select idfiltrolen, filtro from filtrolen order by filtro asc;"
				cursor.execute(consulta)
				filtrolen = cursor.fetchall()
				consulta = "select idcolorlen, color from colorlen;"
				cursor.execute(consulta)
				colorlen = cursor.fetchall()
				consulta = "select idrelacionvenaarteria, relacion from relacionvenaarteria;"
				cursor.execute(consulta)
				relva = cursor.fetchall()
				consulta = "select idojo, ojo from ojo;"
				cursor.execute(consulta)
				dataojo = cursor.fetchall()
				consulta = "select idtipoametropia, tipo from tipoametropia;"
				cursor.execute(consulta)
				dataametropia = cursor.fetchall()
				consulta = "select nombre1, nombre2, apellido1, apellido2, DATE_FORMAT(fechanac,'%Y-%m-%d'), idsexo, profesion, direccion, cui, telefono, telefono2 from paciente;"
				cursor.execute(consulta)
				datapac = cursor.fetchall()
				consulta = "select nombre, apellido, carnet from estudiante;"
				cursor.execute(consulta)
				dataest = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		exicui = 0
		exicarnet = 0
		#panel0
		carnet = request.form["carnet"]
		nombre = request.form["nombre"]
		apellido = request.form["apellido"]
		#panel1
		cui = request.form["cui"]
		telefono = request.form["telefono"]
		telefono1 = request.form["telefono1"]
		if len(telefono1) < 1:
			telefono1 = 0
		nombre1 = request.form["nombre1"]
		nombre2 = request.form["nombre2"]
		apellido1 = request.form["apellido1"]
		apellido2 = request.form["apellido2"]
		if len(nombre2) < 1:
			nombre2 = 0
		if len(apellido2) < 1:
			apellido2 = 0
		se = request.form["sexo"]
		fechanac = request.form["fechanac"]
		profesion = request.form["profesion"]
		direccion = request.form["direccion"]
		#ingreso paciente y estudiante
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "select idpaciente from paciente where cui = %s and cui!= '0';"
					cursor.execute(consulta, cui)
					paciente = cursor.fetchall()
					if len(paciente) > 0:
						idpaciente = paciente[0][0]
						exicui = 1
					else:
						print('entró paciente')
						consulta = "insert into paciente(nombre1, nombre2, apellido1, apellido2, fechanac, idsexo, profesion, direccion, cui, telefono, telefono2, ultimaev) values(%s, %s, %s, %s, %s, %s,%s, %s, %s,%s, %s, %s);"
						cursor.execute(consulta,(nombre1, nombre2,apellido1, apellido2, fechanac, se, profesion, direccion, cui, telefono, telefono1, date.today()))
					
					consulta = "select idestudiante, pacientes from estudiante where carnet = %s;"
					cursor.execute(consulta, carnet)
					estudiante = cursor.fetchall()
					if len(estudiante) > 0:
						idestudiante = estudiante[0][0]
						exicarnet = 1
						consulta = "update estudiante set pacientes = %s where idestudiante = %s"
						cursor.execute(consulta, (int(estudiante[0][1]) + 1, idestudiante))
					else:
						print('entró estudiante')
						consulta = "insert into estudiante(nombre, apellido, carnet,pacientes) values(%s, %s, %s,1);"
						cursor.execute(consulta,(nombre, apellido,carnet))
				conexion.commit()
				if exicui == 0:
					with conexion.cursor() as cursor:
						consulta = "select max(idpaciente) from paciente;"
						cursor.execute(consulta)
						paciente = cursor.fetchall()
						idpaciente = paciente[0][0]
				if exicarnet == 0:
					with conexion.cursor() as cursor:
						consulta = "select max(idestudiante) from estudiante;"
						cursor.execute(consulta)
						estudiante = cursor.fetchall()
						idestudiante = estudiante[0][0]
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		#inserción de consulta a bd
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "insert into consulta(fecha, idpaciente, idestudiante, idusolen, proximacita, dnp, dnp1, dnp2, dnp3, ultimaevmes, ultimaevanio, tiempolen, add1, add2, add3, add11, add22, add33, ojoambliopia, emetropia, antimetropia, tipoametropia, anisometropia, patologiaocular, lentesoftalmicos, lentescontacto, refoftalmologica, farmaco, aprobado,motivoconsulta) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0, %s);"
					cursor.execute(consulta, (date.today(), idpaciente, idestudiante, 0, '0000-00-00', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		#insercion demas campos
		return redirect(url_for('home'))
	return render_template('nuevaconsulta.html', title="Nueva consulta", logeado = logeado, sexo = sexo, anios = anios, cincos=cincos, 
	proxcita = new_date, usolen = usolen, meses = meses, numeros=numeros, mms=mms, tipolen=tipolen, materiallen = materiallen, filtrolen=filtrolen, 
	colorlen=colorlen, relva = relva, nervos=nervos, dataojo=dataojo, dataametropia=dataametropia, enfermedades=enfermedades, datapac=datapac, dataest=dataest)

@app.route('/verventas', methods=['GET', 'POST'])
def verventas():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = '''
				select h.nombrecliente, h.apellidocliente, h.nit, h.preciogen, 
				h.descuento, h.total,  DATE_FORMAT(h.fecha,'%d/%m/%Y'), u.nombre, u.apellido, h.idfacturaheader, h.terminado
				from facturaheader h inner join facturadesc d on h.idfacturaheader = d.idfacturaheader
				inner join consulta c on c.idconsulta = h.idconsulta
				inner join user u on u.iduser = h.iduser order by h.fecha desc
				'''
				cursor.execute(consulta)
				pagos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('verventas.html', title='Ventas', logeado=logeado, pagos=pagos)

@app.route('/aros', methods=['GET', 'POST'])
def aros():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT a.codigo, a.color, m.marca, a.cantidad, a.precio, a.precio * 3, a.consignacion, a.idaro, TIMESTAMPDIFF(MONTH, a.fechaingreso, CURDATE())  from aro a inner join marca m on a.idmarca = m.idmarca order by a.cantidad, m.marca asc, a.codigo asc"
				cursor.execute(consulta)
				aros = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('aros.html', title='Aros', logeado=logeado, aros=aros)

@app.route('/marcas', methods=['GET', 'POST'])
def marcas():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idmarca, marca from marca order by marca asc"
				cursor.execute(consulta)
				marcas = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('marcas.html', title='Marcas', logeado=logeado, marcas=marcas)

@app.route('/nuevamarca', methods=['GET', 'POST'])
def nuevamarca():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	if request.method == 'POST':
		marca = request.form["marca"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO marca(marca) values (%s)"
					cursor.execute(consulta, marca)
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('marcas'))
	return render_template('nuevamarca.html', title='Nueva Marca', logeado=logeado)

@app.route('/editarmarca/<id>', methods=['GET', 'POST'])
def editarmarca(id):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT marca from marca where idmarca = %s"
				cursor.execute(consulta, id)
				marca = cursor.fetchone()
				marca = marca[0]
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		marcaedit = request.form["marca"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "UPDATE marca set marca = %s where idmarca = %s"
					cursor.execute(consulta, (marcaedit, id))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('marcas'))
	return render_template('editarmarca.html', title='Editar Marca', logeado=logeado, marca=marca)

@app.route('/ingresoaros', methods=['GET', 'POST'])
def ingresoaros():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idmarca, marca from marca order by marca asc"
				cursor.execute(consulta)
				marcas = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		codigo = request.form["codigo"]
		color = request.form["color"]
		marca = request.form["marca"]
		cantidad = request.form["cantidad"]
		precio = request.form["precio"]
		try:
			consignacion = request.form["consignacion"]
		except:
			consignacion = 0
		try:
			descmarca = request.form["descmarca"]
		except:
			descmarca = 0
		if consignacion != 0:
			precio = float(precio) * 1.2
		else:
			precio = float(precio)
		if descmarca != 0:
			precio = precio * 2 / 3
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO aro(codigo, color, idmarca, cantidad, precio, consignacion, fechaingreso) values(%s,%s,%s,%s,%s,%s, CURDATE())"
					cursor.execute(consulta, (codigo, color, marca, cantidad, precio, consignacion))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('ingresoaros'))
	return render_template('ingresoaros.html', title='Ingreso de Aros', logeado=logeado, marcas=marcas)

@app.route("/login", methods=['GET', 'POST'])
def login():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado != 0:
		return redirect(url_for('home'))
	if request.method == 'POST':
		user = request.form["user"]
		pwd = request.form["pwd"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT iduser, nombre, apellido FROM user WHERE user = %s and pwd = md5(%s)"
					cursor.execute(consulta, (user, pwd))
					data = cursor.fetchall()
					if len(data) == 0:
						return render_template('login.html', title='Iniciar sesión', logeado=logeado, mensaje="Datos inválidos, intente nuevamente")
					else:
						session['logeado1'] = 1
						session['iduser1'] = data[0][0]
						session['nombreuser1'] = data[0][1]
						session['apellidouser1'] = data[0][2]
						session['user1'] = user
						return redirect(url_for('home'))
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
	return render_template('login.html', title='Iniciar sesión', logeado=logeado, mensaje="")

@app.route("/logout")
def logout():
	session['logeado1'] = 0
	session['nombreuser1'] = ""
	session['apellidouser1'] = ""
	session['user1'] = ""
	session['iduser1'] = ""
	return redirect(url_for('home'))

@app.route("/penddatosclinicos", methods=['GET', 'POST'])
def penddatosclinicos():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('home'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT c.idconsulta, e.nombre, e.apellido, p.nombre1, p.apellido1 from consulta c inner join estudiante e on c.idestudiante = e.idestudiante inner join paciente p on p.idpaciente = c.idpaciente where aprobado = 0 and ingdata = 0"
				cursor.execute(consulta)
				consultas = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('penddatosclinicos.html', title='Datos Clínicos', logeado=logeado, consultas=consultas)

@app.route("/datosclinicos/<idconsulta>", methods=['GET', 'POST'])
def datosclinicos(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('home'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "select idusolen, uso from usolen;"
				cursor.execute(consulta)
				usolen = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	dateac = date.today()
	year = dateac.strftime("%Y")
	year = int(year)
	new_date = dateac + timedelta(days=183)
	nervos = []
	nervo = 1
	for i in range(11):
		nervos.append(nervo*i)
	numeros = []
	numero = 0
	for i in range(36):
		numeros.append(numero)
		numero = numero + 1
	mms = []
	mm = 0
	for i in range(8):
		mms.append(mm)
		mm = mm + 5
	anios = []
	for i in range(80):
		anios.append(year)
		year = year - 1
	cincos = []
	cinco = 0
	for i in range(15):
		cincos.append(cinco)
		cinco = cinco + 5
	meses = [[1, "Enero"],[2, "Febrero"],[3, "Marzo"],[4, "Abril"],[5, "Mayo"],[6, "Junio"],[7, "Julio"],[8, "Agosto"],[9, "Septiembre"],[10, "Octubre"],[11, "Noviembre"],[12, "Diciembre"]]
	enfermedades = [['Diabetes Mellitus'],['Hipertensión Arterial'],['Artritis Reumatoidea'],['Virus Inmunodeficiencia Humana'],['Hipertrigliceridemia'],['Colesterolemia']]
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idpaciente, ojoambliopia, tipoametropia, idusolen, proximacita, dnp, dnp1, dnp2, dnp3, ultimaevmes, ultimaevanio, tiempolen, add1, add2, add3, add11, add22, add33, emetropia, antimetropia, anisometropia, patologiaocular, lentesoftalmicos, lentescontacto, refoftalmologica, farmaco, DATE_FORMAT(fecha,'%d%m%Y'), motivoconsulta, idestudiante from consulta where idconsulta = "+ str(idconsulta) + ";"
				cursor.execute(consulta)
				dataconsulta = cursor.fetchall()
				idpaciente = dataconsulta[0][0]
				idestudiante = dataconsulta[0][28]
				
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "select idrelacionvenaarteria, relacion from relacionvenaarteria;"
				cursor.execute(consulta)
				relva = cursor.fetchall()
				consulta = "select idtipolen, tipo from tipolen;"
				cursor.execute(consulta)
				tipolen = cursor.fetchall()
				consulta = "select idmateriallen, material from materiallen;"
				cursor.execute(consulta)
				materiallen = cursor.fetchall()
				consulta = "select idfiltrolen, filtro from filtrolen order by filtro asc;"
				cursor.execute(consulta)
				filtrolen = cursor.fetchall()
				consulta = "select idlentedetallado, lentedetallado from lentedetallado order by lentedetallado asc;"
				cursor.execute(consulta)
				lentedetalladolen = cursor.fetchall()
				consulta = "select idcolorlen, color from colorlen;"
				cursor.execute(consulta)
				colorlen = cursor.fetchall()
				consulta = "select idojo, ojo from ojo;"
				cursor.execute(consulta)
				dataojo = cursor.fetchall()
				consulta = "select idtipoametropia, tipo from tipoametropia;"
				cursor.execute(consulta)
				dataametropia = cursor.fetchall()
				consulta = "SELECT p.nombre1, p.nombre2, p.apellido1, p.apellido2, p.fechanac, s.sexo, p.profesion, p.direccion, p.cui, p.telefono, p.telefono2 from paciente p inner join sexo s on p.idsexo = s.idsexo where idpaciente = %s"
				cursor.execute(consulta, (idpaciente))
				paciente = cursor.fetchall()
				paciente = paciente[0]
				consulta = "SELECT nombre, apellido, carnet from estudiante where idestudiante = %s"
				cursor.execute(consulta, (idestudiante))
				estudiante = cursor.fetchall()
				estudiante = estudiante[0]
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		#panel2
		motivoconsulta = request.form["motivoconsulta"]
		if len(motivoconsulta) < 1:
			motivoconsulta = 0
		ultimaevmes = request.form["ultimaevmes"]
		ultimaevanio = request.form["ultimaevanio"]
		tiempolentes = request.form["tiempolentes"]
		if len(ultimaevmes) < 1:
			ultimaevmes = 0
		if len(ultimaevanio) < 1:
			ultimaevanio = 0
		if len(tiempolentes) < 1:
			tiempolentes = 0
		antoftal = request.form["antoftal"]
		if len(antoftal) < 1:
			antoftal = 0
		antfam = request.form["antfam"]
		antaler = request.form["antaler"]
		antgla = request.form["antgla"]
		if len(antfam) < 1:
			antfam = 0
		if len(antaler) < 1:
			antaler = 0
		if len(antgla) < 1:
			antgla = 0
		numantmed = request.form["numantmed"]
		numantqui = request.form["numantqui"]
		numantmed = int(numantmed)
		numantqui = int(numantqui)
		antmed = []
		antqui = []
		for i in range(numantmed):
			aux = 'enfermedad' + str(i+1)
			enfermedad = request.form[aux]
			if len(enfermedad) < 1:
				enfermedad = 0
			try:
				aux = 'medotro' + str(i+1)
				otro = request.form[aux]
				if len(otro) < 1:
					otro = 0
			except:
				otro = 0
			aux = 'tiempoevolucionm' + str(i+1)
			tiempoev = request.form[aux]
			if len(tiempoev) < 1:
				tiempoev = 0
			aux = 'controlm' + str(i+1)
			control = request.form[aux]
			if len(control) < 1:
				control = 0
			aux = [enfermedad, otro, tiempoev, control]
			antmed.append(aux)
		for i in range(numantqui):
			aux = 'cirugia' + str(i+1)
			cirugia = request.form[aux]
			if len(cirugia) < 1:
				cirugia = 0
			aux = 'tiempoevolucionq' + str(i+1)
			tiempoev = request.form[aux]
			if len(tiempoev) < 1:
				tiempoev = 0
			aux = 'controlq' + str(i+1)
			control = request.form[aux]
			if len(control) < 1:
				control = 0
			aux = [cirugia, tiempoev, control]
			antqui.append(aux)
		#panel3
		avlod = request.form["avlod"]
		avloi = request.form["avloi"]
		aeod = request.form["aeod"]
		aeoi = request.form["aeoi"]
		avcod = request.form["avcod"]
		avcoi = request.form["avcoi"]
		if len(avcod) < 1:
			avcod = 0
		if len(avcoi) < 1:
			avcoi = 0
		if len(avlod) < 1:
			avlod = 0
		if len(avloi) < 1:
			avloi = 0
		if len(aeod) < 1:
			aeod = 0
		if len(aeoi) < 1:
			aeoi = 0
		#panel4
		raeod = request.form["raeod"]
		racod = request.form["racod"]
		if len(raeod) < 1:
			raeod = 0
		if len(racod) < 1:
			racod = 0
		racod = float(racod)
		if racod > 0:
			racod = racod * -1
		raejod = request.form["raejod"]
		if len(raejod) < 1:
			raejod = 0
		rapod = request.form["rapod"]
		if len(rapod) < 1:
			rapod = 0
		raavcc1od = request.form["raavcc1od"]
		if len(str(raavcc1od)) < 1:
			raavcc1od = 0
		raeoi = request.form["raeoi"]
		racoi = request.form["racoi"]
		if len(raeoi) < 1:
			raeoi = 0
		if len(racoi) < 1:
			racoi = 0
		racoi = float(racoi)
		if racoi > 0:
			racoi = racoi * -1
		raejoi = request.form["raejoi"]
		if len(raejoi) < 1:
			raejoi = 0
		rapoi = request.form["rapoi"]
		if len(rapoi) < 1:
			rapoi = 0
		raavcc1oi = request.form["raavcc1oi"]
		if len(raavcc1oi) < 1:
			raavcc1oi = 0
		add1 = request.form["add1"]
		if len(add1) < 1:
			add1 = 0
		add2 = request.form["add2"]
		if len(add2) < 1:
			add2 = 0
		add3 = request.form["add3"]
		if len(add3) < 1:
			add3 = 0
		dnp1 = request.form["dnp1"]
		if len(dnp1) < 1:
			dnp1 = 0
		vceod = request.form["vceod"]
		vccod = request.form["vccod"]
		if len(vceod) < 1:
			vceod = 0
		if len(vccod) < 1:
			vccod = 0
		vccod = float(vccod)
		if vccod > 0:
			vccod = vccod * -1
		vcejod = request.form["vcejod"]
		if len(vcejod) < 1:
			vcejod = 0
		vcpod = request.form["vcpod"]
		if len(vcpod) < 1:
			vcpod = 0
		vcavccod = request.form["vcavccod"]
		vceoi = request.form["vceoi"]
		vccoi = request.form["vccoi"]
		if len(vcavccod) < 1:
			vcavccod = 0
		if len(vceoi) < 1:
			vceoi = 0
		if len(vccoi) < 1:
			vccoi = 0
		vccoi = float(vccoi)
		if vccoi > 0:
			vccoi = vccoi * -1
		vcejoi = request.form["vcejoi"]
		if len(vcejoi) < 1:
			vcejoi = 0
		vcpoi = request.form["vcpoi"]
		if len(vcpoi) < 1:
			vcpoi = 0
		vcavccoi = request.form["vcavccoi"]
		if len(vcavccoi) < 1:
			vcavccoi = 0
		#panel5
		roaeod = request.form["roaeod"]
		roacod = request.form["roacod"]
		if len(roaeod) < 1:
			roaeod = 0
		if len(roacod) < 1:
			roacod = 0
		roacod = float(roacod)
		if roacod > 0:
			roacod = roacod * -1
		roaejod = request.form["roaejod"]
		if len(roaejod) < 1:
			roaejod = 0
		roapod = request.form["roapod"]
		if len(roapod) < 1:
			roapod = 0
		roavod = request.form["roavod"]
		if len(roavod) < 1:
			roavod = 0
		roaavccod = request.form["roaavccod"]
		if len(roaavccod) < 1:
			roaavccod = 0
		roaeoi = request.form["roaeoi"]
		roacoi = request.form["roacoi"]
		if len(roaeoi) < 1:
			roaeoi = 0
		if len(roacoi) < 1:
			roacoi = 0
		roacoi = float(roacoi)
		if roacoi > 0:
			roacoi = roacoi * -1
		roaejoi = request.form["roaejoi"]
		if len(roaejoi) < 1:
			roaejoi = 0
		roapoi = request.form["roapoi"]
		if len(roapoi) < 1:
			roapoi = 0
		roavoi = request.form["roavoi"]
		if len(roavoi) < 1:
			roavoi = 0
		roaavccoi = request.form["roaavccoi"]
		if len(roaavccoi) < 1:
			roaavccoi = 0
		
		roreod = request.form["roreod"]
		rorcod = request.form["rorcod"]
		if len(roreod) < 1:
			roreod = 0
		if len(rorcod) < 1:
			rorcod = 0
		rorcod = float(rorcod)
		if rorcod > 0:
			rorcod = rorcod * -1
		rorejod = request.form["rorejod"]
		if len(rorejod) < 1:
			rorejod = 0
		rorpod = request.form["rorpod"]
		if len(rorpod) < 1:
			rorpod = 0
		rorvod = request.form["rorvod"]
		if len(rorvod) < 1:
			rorvod = 0
		roravccod = request.form["roravccod"]
		if len(roravccod) < 1:
			roravccod = 0
		roreoi = request.form["roreoi"]
		rorcoi = request.form["rorcoi"]
		if len(roreoi) < 1:
			roreoi = 0
		if len(rorcoi) < 1:
			rorcoi = 0
		rorcoi = float(rorcoi)
		if rorcoi > 0:
			rorcoi = rorcoi * -1
		rorejoi = request.form["rorejoi"]
		if len(rorejoi) < 1:
			rorejoi = 0
		rorpoi = request.form["rorpoi"]
		if len(rorpoi) < 1:
			rorpoi = 0
		rorvoi = request.form["rorvoi"]
		if len(rorvoi) < 1:
			rorvoi = 0
		roravccoi = request.form["roravccoi"]
		if len(roravccoi) < 1:
			roravccoi = 0
		#panel6
		rseod = request.form["rseod"]
		rscod = request.form["rscod"]
		if len(rseod) < 1:
			rseod = 0
		if len(rscod) < 1:
			rscod = 0
		rscod = float(rscod)
		if rscod > 0:
			rscod = rscod * -1
		rsejod = request.form["rsejod"]
		rspod = request.form["rspod"]
		if len(rsejod) < 1:
			rsejod = 0
		if len(rspod) < 1:
			rspod = 0
		rsavccod = request.form["rsavccod"]
		rseoi = request.form["rseoi"]
		rscoi = request.form["rscoi"]
		if len(rsavccod) < 1:
			rsavccod = 0
		if len(rseoi) < 1:
			rseoi = 0
		if len(rscoi) < 1:
			rscoi = 0
		rscoi = float(rscoi)
		if rscoi > 0:
			rscoi = rscoi * -1
		rsejoi = request.form["rsejoi"]
		rspoi = request.form["rspoi"]
		if len(rsejoi) < 1:
			rsejoi = 0
		if len(rspoi) < 1:
			rspoi = 0
		rsavccoi = request.form["rsavccoi"]
		if len(rsavccoi) < 1:
			rsavccoi = 0
		try:
			pruamb = request.form["pruamb"]
		except:
			pruamb = 0
		try:
			pruest = request.form["pruest"]
		except:
			pruest = 0
		try:
			testbi = request.form["testbi"]
		except:
			testbi = 0
		try:
			equibino = request.form["equibino"]
		except:
			equibino = 0
		try:
			ciljackson = request.form["ciljackson"]
		except:
			ciljackson = 0
		#panel7
		rfe1od = request.form["rfe1od"]
		rfe2od = request.form["rfe2od"]
		rfe3od = request.form["rfe3od"]
		if len(rfe1od) < 1:
			rfe1od = 0
		if len(rfe2od) < 1:
			rfe2od = 0
		if len(rfe3od) < 1:
			rfe3od = 0
		rfc1od = request.form["rfc1od"]
		if len(rfc1od) < 1:
			rfc1od = 0
		rfc1od = float(rfc1od)
		if rfc1od > 0:
			rfc1od = rfc1od * -1
		rfc2od = request.form["rfc2od"]
		if len(rfc2od) < 1:
			rfc2od = 0
		rfc2od = float(rfc2od)
		if rfc2od > 0:
			rfc2od = rfc2od * -1
		rfc3od = request.form["rfc3od"]
		if len(rfc3od) < 1:
			rfc3od = 0
		rfc3od = float(rfc3od)
		if rfc3od > 0:
			rfc3od = rfc3od * -1
		rfej1od = request.form["rfej1od"]
		rfej2od = request.form["rfej2od"]
		rfej3od = request.form["rfej3od"]
		if len(rfej1od) < 1:
			rfej1od = 0
		if len(rfej2od) < 1:
			rfej2od = 0
		if len(rfej3od) < 1:
			rfej3od = 0
		rfp1od = request.form["rfp1od"]
		rfp2od = request.form["rfp2od"]
		rfp3od = request.form["rfp3od"]
		if len(rfp1od) < 1:
			rfp1od = 0
		if len(rfp2od) < 1:
			rfp2od = 0
		if len(rfp3od) < 1:
			rfp3od = 0
		rfavcc1od = request.form["rfavcc1od"]
		rfavcc2od = request.form["rfavcc2od"]
		rfavcc3od = request.form["rfavcc3od"]
		if len(rfavcc3od) < 1:
			rfavcc3od = 0
		if len(rfavcc2od) < 1:
			rfavcc2od = 0
		if len(rfavcc3od) < 1:
			rfavcc3od = 0
		rfe1oi = request.form["rfe1oi"]
		rfe2oi = request.form["rfe2oi"]
		rfe3oi = request.form["rfe3oi"]
		if len(rfe1oi) < 1:
			rfe1oi = 0
		if len(rfe2oi) < 1:
			rfe2oi = 0
		if len(rfe3oi) < 1:
			rfe3oi = 0
		rfc1oi = request.form["rfc1oi"]
		if len(rfc1oi) < 1:
			rfc1oi = 0
		rfc1oi = float(rfc1oi)
		if rfc1oi > 0:
			rfc1oi = rfc1oi * -1
		rfc2oi = request.form["rfc2oi"]
		if len(rfc2oi) < 1:
			rfc2oi = 0
		rfc2oi = float(rfc2oi)
		if rfc2oi > 0:
			rfc2oi = rfc2oi * -1
		rfc3oi = request.form["rfc3oi"]
		if len(rfc3oi) < 1:
			rfc3oi = 0
		rfc3oi = float(rfc3oi)
		if rfc3oi > 0:
			rfc3oi = rfc3oi * -1
		rfej1oi = request.form["rfej1oi"]
		rfej2oi = request.form["rfej2oi"]
		rfej3oi = request.form["rfej3oi"]
		if len(rfej1oi) < 1:
			rfej1oi = 0
		if len(rfej2oi) < 1:
			rfej2oi = 0
		if len(rfej3oi) < 1:
			rfej3oi = 0
		rfp1oi = request.form["rfp1oi"]
		rfp2oi = request.form["rfp2oi"]
		rfp3oi = request.form["rfp3oi"]
		if len(rfp1oi) < 1:
			rfp1oi = 0
		if len(rfp2oi) < 1:
			rfp2oi = 0
		if len(rfp3oi) < 1:
			rfp3oi = 0
		rfavcc1oi = request.form["rfavcc1oi"]
		rfavcc2oi = request.form["rfavcc2oi"]
		rfavcc3oi = request.form["rfavcc3oi"]
		if len(rfavcc1oi) < 1:
			rfavcc1oi = 0
		if len(rfavcc2oi) < 1:
			rfavcc2oi = 0
		if len(rfavcc3oi) < 1:
			rfavcc3oi = 0
		dnp = request.form["dnp"]
		dnp2 = request.form["dnp2"]
		dnp3 = request.form["dnp3"]
		if len(dnp) < 1:
			dnp = 0
		if len(dnp2) < 1:
			dnp2 = 0
		if len(dnp3) < 1:
			dnp3 = 0
		add11 = request.form["add11"]
		add22 = request.form["add22"]
		add33 = request.form["add33"]
		if len(add11) < 1:
			add11 = 0
		if len(add22) < 1:
			add22 = 0
		if len(add33) < 1:
			add33 = 0
		#panel8
		mmfod = request.form["mmfod"]
		mmfoi = request.form["mmfoi"]
		forod = request.form["forod"]
		foroi = request.form["foroi"]
		trood = request.form["trood"]
		trooi = request.form["trooi"]
		duccod = request.form["duccod"]
		duccoi = request.form["duccoi"]
		versiones = request.form["versiones"]
		convergencia = request.form["convergencia"]
		if len(mmfod) < 1:
			mmfod = 0
		if len(mmfoi) < 1:
			mmfoi = 0
		if len(forod) < 1:
			forod = 0
		if len(foroi) < 1:
			foroi = 0
		if len(trood) < 1:
			trood = 0
		if len(trooi) < 1:
			trooi = 0
		if len(duccod) < 1:
			duccod = 0
		if len(duccoi) < 1:
			duccoi = 0
		if len(versiones) < 1:
			versiones = 0
		if len(convergencia) < 1:
			convergencia = 0	
		try:
			ortoforico = request.form["ortoforico"]
		except:
			ortoforico = 0
		#panel9
		try:
			ojsal = request.form["ojsal"]
		except:
			ojsal = 0
		orbod = request.form["orbod"]
		orboi = request.form["orboi"]
		cejod = request.form["cejod"]
		cejoi = request.form["cejoi"]
		lagod = request.form["lagod"]
		lagoi = request.form["lagoi"]
		schod = request.form["schod"]
		schoi = request.form["schoi"]
		butod = request.form["butod"]
		butoi = request.form["butoi"]
		if len(orbod) < 1:
			orbod = 0
		if len(orboi) < 1:
			orboi = 0
		if len(cejod) < 1:
			cejod = 0
		if len(cejoi) < 1:
			cejoi = 0
		if len(lagod) < 1:
			lagod = 0
		if len(lagoi) < 1:
			lagoi = 0
		if len(schod) < 1:
			schod = 0
		if len(schoi) < 1:
			schoi = 0
		if len(butod) < 1:
			butod = 0
		if len(butoi) < 1:
			butoi = 0	
		vilagod = request.form["vilagod"]
		vilagoi = request.form["vilagoi"]
		pypod = request.form["pypod"]
		pypoi = request.form["pypoi"]
		conjod = request.form["conjod"]
		conjoi = request.form["conjoi"]
		esclod = request.form["esclod"]
		escloi = request.form["escloi"]
		cornod = request.form["cornod"]
		cornoi = request.form["cornoi"]
		if len(vilagod) < 1:
			vilagod = 0
		if len(vilagoi) < 1:
			vilagoi = 0
		if len(pypod) < 1:
			pypod = 0
		if len(pypoi) < 1:
			pypoi = 0
		if len(conjod) < 1:
			conjod = 0
		if len(conjoi) < 1:
			conjoi = 0
		if len(esclod) < 1:
			esclod = 0
		if len(escloi) < 1:
			escloi = 0
		if len(cornod) < 1:
			cornod = 0
		if len(cornoi) < 1:
			cornoi = 0	
		camaod = request.form["camaod"]
		camaoi = request.form["camaoi"]
		iriod = request.form["iriod"]
		irioi = request.form["irioi"]
		pupiod = request.form["pupiod"]
		pupioi = request.form["pupioi"]
		crisod = request.form["crisod"]
		crisoi = request.form["crisoi"]
		vitod = request.form["vitod"]
		vitoi = request.form["vitoi"]
		if len(camaod) < 1:
			camaod = 0
		if len(camaoi) < 1:
			camaoi = 0
		if len(iriod) < 1:
			iriod = 0
		if len(irioi) < 1:
			irioi = 0
		if len(pupiod) < 1:
			pupiod = 0
		if len(pupioi) < 1:
			pupioi = 0
		if len(crisod) < 1:
			crisod = 0
		if len(crisoi) < 1:
			crisoi = 0
		if len(vitod) < 1:
			vitod = 0
		if len(vitoi) < 1:
			vitoi = 0
		nervood = request.form["nervood"]
		nervooi = request.form["nervooi"]
		retppod = request.form["retppod"]
		retppoi = request.form["retppoi"]
		retpeod = request.form["retpeod"]
		retpeoi = request.form["retpeoi"]
		retmacod = request.form["retmacod"]
		retmacoi = request.form["retmacoi"]
		if len(nervood) < 1:
			nervood = 0
		if len(nervooi) < 1:
			nervooi = 0
		if len(retppod) < 1:
			retppod = 0
		if len(retppoi) < 1:
			retppoi = 0
		if len(retpeod) < 1:
			retpeod = 0
		if len(retpeoi) < 1:
			retpeoi = 0
		if len(retmacod) < 1:
			retmacod = 0
		if len(retmacoi) < 1:
			retmacoi = 0
		
		#panel10
		proxicita = request.form["proxicita"]
		usolent = request.form["usolent"]
		tipolent = request.form["tipolent"]
		materiallent = request.form["materiallent"]
		filtrolent = request.form["filtrolent"]
		colorlent = request.form["colorlent"]
		try:
			ambliopiaoi = request.form["ambliopiaoi"]
		except:
			ambliopiaoi = 0
		try:
			ambliopiaod = request.form["ambliopiaod"]
		except:
			ambliopiaod = 0
		ametropiaoi = request.form["ametropiaoi"]
		if len(ametropiaoi) < 1:
			ametropiaoi = 0
		if len(usolent) < 1:
			usolent = 6
		if len(tipolent) < 1:
			tipolent = 7
		if len(materiallent) < 1:
			materiallent = 5
		if len(filtrolent) < 1:
			filtrolent = 10
		if len(colorlent) < 1:
			colorlent = 10
		ambliopia = request.form["ambliopia"]
		ametropia = request.form["ametropia"]
		if len(ambliopia) < 1:
			ambliopia = 0
		if len(ametropia) < 1:
			ametropia = 0
		lentedetalladolent = request.form["lentedetalladolent"]
		if len(lentedetalladolent) < 1:
			lentedetalladolent = 15
		try:
			emetropia = request.form["emetropia"]
		except:
			emetropia = 0
		try:
			antimetropia = request.form["antimetropia"]
		except:
			antimetropia = 0
		try:
			anisometropia = request.form["anisometropia"]
		except:
			anisometropia = 0
		try:
			patologiaocular = request.form["patologiaocular"]
			patologiaoculartext = request.form["patologiaoculartext"]
		except:
			patologiaocular = 0
			patologiaoculartext = 0
		try:
			lentesoftalmicos = request.form["lentesoftalmicos"]
		except:
			lentesoftalmicos = 0
		try:
			lentescontacto = request.form["lentescontacto"]
		except:
			lentescontacto = 0
		try:
			refoftalmologica = request.form["refoftalmologica"]
		except:
			refoftalmologica = 0
		try:
			farmaco = request.form["farmaco"]
		except:
			farmaco = 0
		gmed1 = request.form["gmed1"]
		gdesc1 = request.form["gdesc1"]
		gmed2 = request.form["gmed2"]
		gdesc2 = request.form["gdesc2"]
		if len(gmed1) < 1:
			gmed1 = 0
		if len(gdesc1) < 1:
			gdesc1 = 0
		if len(gmed2) < 1:
			gmed2 = 0
		if len(gdesc2) < 1:
			gdesc2 = 0
		lugarref = request.form["lugarref"]
		descref = request.form["descref"]
		if len(lugarref) < 1:
			lugarref = 0
		if len(descref) < 1:
			descref = 0
		notas = request.form["notas"]
		if len(notas) < 1:
			notas = 0
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					#agudeza visual
					consulta = "insert into agudezavisual(idconsulta, idojo, avl, phae, avc) values (%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, avloi, aeoi, avcoi))
					consulta = "insert into agudezavisual(idconsulta, idojo, avl, phae, avc) values (%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, avlod, aeod, avcod))
					
					#refraccion actual
					consulta = "insert into refact(idconsulta, idojo, esfera, cilindro, eje, avcc1, prisma) values (%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, raeoi, racoi, raejoi, raavcc1oi, rapoi))
					consulta = "insert into refact(idconsulta, idojo, esfera, cilindro, eje, avcc1, prisma) values (%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, raeod, racod, raejod, raavcc1od, rapod))
					
					#Vision cercana
					consulta = "insert into ravc(idconsulta, idojo, esfera, cilindo, eje, avcc, prisma) values (%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, vceoi, vccoi, vcejoi, vcavccoi, vcpoi))
					consulta = "insert into ravc(idconsulta, idojo, esfera, cilindo, eje, avcc, prisma) values (%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, vceod, vccod, vcejod, vcavccod, vcpod))
					
					#Refraccion objetiva alumno
					consulta = "insert into refobjal(idconsulta, idojo, esfera, cilindro, eje, avcc, prisma, dvertice) values (%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, roaeoi, roacoi, roaejoi, roaavccoi, roapoi, roavoi))
					consulta = "insert into refobjal(idconsulta, idojo, esfera, cilindro, eje, avcc, prisma, dvertice) values (%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, roaeod, roacod, roaejod, roaavccod, roapod, roavod))
					
					#Refraccion objetiva referencia
					consulta = "insert into refobjref(idconsulta, idojo, esfera, cilindro, eje, avcc, prisma, dvertice) values (%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, roreoi, rorcoi, rorejoi, roravccoi, rorpoi, rorvoi))
					consulta = "insert into refobjref(idconsulta, idojo, esfera, cilindro, eje, avcc, prisma, dvertice) values (%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, roreod, rorcod, rorejod, roravccod, rorpod, rorvod))
					
					#Refraccion subjetiva
					consulta = "insert into refsub(idconsulta, idojo, esfera, cilindro, eje, avcc, prisma, pruamb, testbi, equibino, pruest,ciljackson) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, rseoi, rscoi, rsejoi, rsavccoi, rspoi, pruamb, testbi, equibino, pruest, ciljackson))
					consulta = "insert into refsub(idconsulta, idojo, esfera, cilindro, eje, avcc, prisma, pruamb, testbi, equibino, pruest,ciljackson) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, rseod, rscod, rsejod, rsavccod, rspod, pruamb, testbi, equibino, pruest, ciljackson))
					
					#Refraccion final
					consulta = "insert into reffin(idconsulta, idojo, esfera1, esfera2, esfera3, cilindro1, cilindro2, cilindro3, eje1, eje2, eje3, avcc1, avcc2, avcc3, prisma1, prisma2, prisma3) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, rfe1oi, rfe2oi, rfe3oi, rfc1oi, rfc2oi, rfc3oi, rfej1oi, rfej2oi, rfej3oi, rfavcc1oi, rfavcc2oi, rfavcc3oi, rfp1oi, rfp2oi, rfp3oi))
					consulta = "insert into reffin(idconsulta, idojo, esfera1, esfera2, esfera3, cilindro1, cilindro2, cilindro3, eje1, eje2, eje3, avcc1, avcc2, avcc3, prisma1, prisma2, prisma3) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, rfe1od, rfe2od, rfe3od, rfc1od, rfc2od, rfc3od, rfej1od, rfej2od, rfej3od, rfavcc1od, rfavcc2od, rfavcc3od, rfp1od, rfp2od, rfp3od))
					
					#Motilidad Ocular
					consulta = "insert into motocu(idconsulta, idojo, mmf, forias, tropias, ducciones, versiones, convergencia, ortoforico) values (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, mmfoi, foroi, trooi, duccoi, versiones, convergencia, ortoforico))
					consulta = "insert into motocu(idconsulta, idojo, mmf, forias, tropias, ducciones, versiones, convergencia, ortoforico) values (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, mmfod, forod, trood, duccod, versiones, convergencia, ortoforico))
					
					#observaciones
					consulta = "insert into observaciones(idconsulta, idojo, valnormales, orbita, cejas, lagrima, viaslag, parpados, conjuntiva, esclera, cornea, camara, iris, pupila, cristalino, vitreo, nervioop, retinapp, retinape, retinamac, schirmer, but) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 1, ojsal, orboi, cejoi, lagoi, vilagoi, pypoi, conjoi, escloi, cornoi, camaoi, irioi, pupioi, crisoi, vitoi, nervooi, retppoi, retpeoi, retmacoi, schoi, butoi))
					consulta = "insert into observaciones(idconsulta, idojo, valnormales, orbita, cejas, lagrima, viaslag, parpados, conjuntiva, esclera, cornea, camara, iris, pupila, cristalino, vitreo, nervioop, retinapp, retinape, retinamac, schirmer, but) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, 2, ojsal, orbod, cejod, lagod, vilagod, pypod, conjod, esclod, cornod, camaod, iriod, pupiod, crisod, vitod, nervood, retppod, retpeod, retmacod, schod, butod))

					#Lente recomendado
					consulta = "insert into lenterecomendado(idconsulta, tipo, material, filtro, color, lentedetallado) values (%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idconsulta, tipolent, materiallent, filtrolent, colorlent, lentedetalladolent))

					#consulta
					consulta = "update consulta set idusolen=%s, proximacita=%s, dnp=%s,dnp1=%s, add1=%s, add2=%s, add3=%s, add11=%s, add22=%s, add33=%s, ingdata=1, dnp2=%s, dnp3=%s, ojoambliopia=%s, emetropia=%s, antimetropia=%s, tipoametropia=%s, anisometropia=%s, patologiaocular=%s, lentesoftalmicos=%s, lentescontacto=%s, refoftalmologica=%s, farmaco=%s, motivoconsulta=%s, ultimaevmes=%s, ultimaevanio=%s, tiempolen=%s, nota=%s, ambliopiaoi=%s, ambliopiaod=%s, ametropiaoi=%s where idconsulta = %s;"
					cursor.execute(consulta, (usolent, proxicita, dnp, dnp1, add1, add2, add3, add11, add22, add33, dnp2, dnp3, ambliopia, emetropia, antimetropia, ametropia, anisometropia, patologiaoculartext, lentesoftalmicos, lentescontacto, refoftalmologica, farmaco, motivoconsulta, ultimaevmes, ultimaevanio, tiempolentes, notas,ambliopiaoi, ambliopiaod, ametropiaoi, idconsulta))

					#gotas
					consulta = "insert into recetagotero(idconsulta, medicamento1, descripcion1, medicamento2, descripcion2) values(%s,%s,%s,%s,%s)"
					cursor.execute(consulta, (idconsulta, gmed1, gdesc1,gmed2, gdesc2))

					#referencia
					consulta = "insert into recetareferencia(idconsulta, lugar, descripcion) values(%s,%s,%s)"
					cursor.execute(consulta, (idconsulta, lugarref, descref))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "select idantecedentes from antecedentes where idpaciente = %s;"
					cursor.execute(consulta, idpaciente)
					antecedentes = cursor.fetchall()
					exicui = len(antecedentes)
					print(exicui)
					#antecedentes
					if exicui == 0:
						consulta = "insert into antecedentes(idpaciente, oftalmologicos, familiares, glaucoma, alergicas) values (%s,%s,%s,%s,%s);"
						cursor.execute(consulta, (idpaciente, antoftal, antfam, antgla, antaler))
					else:
						consulta = "update antecedentes set oftalmologicos = %s, familiares = %s, glaucoma = %s, alergicas = %s where idpaciente = %s;"
						cursor.execute(consulta, (antoftal, antfam, antgla, antaler, idpaciente))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "select idantecedentes from antecedentes where idpaciente = %s;"
					cursor.execute(consulta, idpaciente)
					dataantecedentes = cursor.fetchall()
					idantecedentes = dataantecedentes[0][0]
					for i in range(numantmed):
						consulta = "insert into antmed(idantecedentes, enfermedad, tiempoevolucion, control, otro) values (%s,%s,%s,%s,%s);"
						cursor.execute(consulta, (idantecedentes, antmed[i][0], antmed[i][2],antmed[i][3],antmed[i][1]))
					for i in range(numantqui):
						consulta = "insert into antquir(idantecedentes, cirugia, tiempoevolucion, control) values (%s,%s,%s,%s);"
						cursor.execute(consulta, (idantecedentes, antqui[i][0], antqui[i][1],antqui[i][2]))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('home'))
	return render_template('datosclinicos.html', title='Pendiente de ingreso de datos', logeado=logeado, paciente = paciente, 
		dataconsulta=dataconsulta, anios=anios, cincos=cincos, meses=meses, usolen=usolen, 
		enfermedades=enfermedades,nervos=nervos, mms=mms, numeros=numeros, relva=relva, 
		tipolen=tipolen, materiallen=materiallen, filtrolen=filtrolen, colorlen=colorlen, 
		dataojo=dataojo, dataametropia=dataametropia, new_date=new_date, estudiante=estudiante,
		lentedetalladolen=lentedetalladolen)

@app.route("/pendaprobar", methods=['GET', 'POST'])
def pendaprobar():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('home'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT c.idconsulta, e.nombre, e.apellido, p.nombre1, p.apellido1 from consulta c inner join estudiante e on c.idestudiante = e.idestudiante inner join paciente p on p.idpaciente = c.idpaciente where aprobado = 0 and ingdata = 1"
				cursor.execute(consulta)
				consultas = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('pendaprobar.html', title='Datos Clínicos', logeado=logeado, consultas=consultas)

@app.route("/aprobados", methods=['GET', 'POST'])
def aprobados():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT c.idconsulta, e.nombre, e.apellido, p.nombre1, p.apellido1, DATE_FORMAT(c.fecha,'%d/%m/%Y'), p.nombre2, p.apellido2 from consulta c inner join estudiante e on c.idestudiante = e.idestudiante inner join paciente p on p.idpaciente = c.idpaciente where aprobado = 1"
				cursor.execute(consulta)
				consultas = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('aprobados.html', title='Aprobados', logeado=logeado, consultas=consultas)

@app.route("/recetas/<idconsulta>", methods=['GET', 'POST'])
def recetas(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	rf = []
	lencons = []
	existe = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT esfera1, cilindro1, eje1, prisma1, avcc1 from reffin where idconsulta = %s and idojo = 2;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rf.append(aux)
				consulta = "SELECT esfera1, cilindro1, eje1, prisma1, avcc1 from reffin where idconsulta = %s and idojo = 1;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rf.append(aux)
				consulta = "SELECT DATE_FORMAT(fechacaducidad,'%d/%m/%Y'), poder, cb, dia, cil, eje, agregar, color, tipo from recetacontacto where idconsulta = " + str(idconsulta) + " and idojo = 2;"
				cursor.execute(consulta)
				aux = cursor.fetchall()
				if len(aux) < 1:
					lencons.append([0,0,0,0,0,0,0,0,0])
				else:
					lencons.append(aux[0])
					existe = existe + 1
				consulta = "SELECT DATE_FORMAT(fechacaducidad,'%d/%m/%Y'), poder, cb, dia, cil, eje, agregar, color, tipo from recetacontacto where idconsulta = " + str(idconsulta) + " and idojo = 1;"
				cursor.execute(consulta)
				aux = cursor.fetchall()
				if len(aux) < 1:
					lencons.append([0,0,0,0,0,0,0,0,0])
				else:
					lencons.append(aux[0])
					existe = existe + 1
				consulta = "SELECT medicamento1, descripcion1, medicamento2, descripcion2 from recetagotero where idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchall()
				if len(aux) < 1:
					datagotero = [0,0,0,0]
				else:
					datagotero = aux[0]
				consulta = "SELECT p.nombre1, p.nombre2, p.apellido1, p.apellido2, DATE_FORMAT(c.fecha,'%d/%m/%Y'), u.uso, DATE_FORMAT(c.proximacita,'%d/%m/%Y'), c.dnp, c.add11, c.add22, c.add33, o.nombre, o.apellido from paciente p inner join consulta c on p.idpaciente = c.idpaciente inner join usolen u on u.idusolen = c.idusolen inner join user o ON o.iduser = c.iduser where idconsulta = " + str(idconsulta) + ";"
				cursor.execute(consulta)
				dataconsulta = cursor.fetchall()
				consulta = "SELECT t.tipo, m.material, f.filtro, c.color, d.lentedetallado from lenterecomendado l inner join tipolen t on t.idtipolen=l.tipo inner join materiallen m on m.idmateriallen=l.material inner join filtrolen f on f.idfiltrolen=l.filtro inner join colorlen c on c.idcolorlen=l.color inner join lentedetallado d on d.idlentedetallado = l.lentedetallado where l.idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				lenterecomendado = cursor.fetchall()
				consulta = "SELECT lugar, descripcion from recetareferencia  where idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				recetaref = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		#lente de contacto
		lcfechacad = request.form["lcfechacad"]
		lcpoderod = request.form["lcpoderod"]
		lcpoderoi = request.form["lcpoderoi"]
		lccbod = request.form["lccbod"]
		lccboi = request.form["lccboi"]
		lcdiaod = request.form["lcdiaod"]
		lcdiaoi = request.form["lcdiaoi"]
		lccilod = request.form["lccilod"]
		lcciloi = request.form["lcciloi"]
		lcejeod = request.form["lcejeod"]
		lcejeoi = request.form["lcejeoi"]
		lcagregarod = request.form["lcagregarod"]
		lcagregaroi = request.form["lcagregaroi"]
		lccolorod = request.form["lccolorod"]
		lccoloroi = request.form["lccoloroi"]
		lctipood = request.form["lctipood"]
		lctipooi = request.form["lctipooi"]
		if len(lcfechacad) < 1:
			lcfechacad = 0
		else:
			datos=lcfechacad.split('/')
			try:
				lcfechacad = datos[2] + '-' + datos[1] + '-' + datos[0]
			except:
				lcfechacad = '0000-00-00'
		if len(lcpoderod) < 1:
			lcpoderod = 0
		if len(lcpoderoi) < 1:
			lcpoderoi = 0
		if len(lccbod) < 1:
			lccbod = 0
		if len(lccboi) < 1:
			lccboi = 0
		if len(lcdiaod) < 1:
			lcdiaod = 0
		if len(lcdiaoi) < 1:
			lcdiaoi = 0
		if len(lccilod) < 1:
			lccilod = 0
		if len(lcciloi) < 1:
			lcciloi = 0
		if len(lcejeod) < 1:
			lcejeod = 0
		if len(lcejeoi) < 1:
			lcejeoi = 0
		if len(lcagregarod) < 1:
			lcagregarod = 0
		if len(lcagregaroi) < 1:
			lcagregaroi = 0
		if len(lccolorod) < 1:
			lccolorod = 0
		if len(lccoloroi) < 1:
			lccoloroi = 0
		if len(lctipood) < 1:
			lctipood = 0
		if len(lctipooi) < 1:
			lctipooi = 0
		#gotas
		gfechacad = request.form["gfechacad"]
		datos=gfechacad.split('/')
		try:
			gfechacad = datos[2] + '-' + datos[1] + '-' + datos[0]
		except:
			gfechacad = '0000-00-00'
		gmed1 = request.form["gmed1"]
		gdesc1 = request.form["gdesc1"]
		gmed2 = request.form["gmed2"]
		gdesc2 = request.form["gdesc2"]
		if len(gmed1) < 1:
			gmed1 = 0
		if len(gdesc1) < 1:
			gdesc1 = 0
		if len(gmed2) < 1:
			gmed2 = 0
		if len(gdesc2) < 1:
			gdesc2 = 0
		lugar = request.form["lugar"]
		descripcion = request.form["descripcion"]
		if len(lugar) < 1:
			lugar = 0
		if len(descripcion) < 1:
			descripcion = 0
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					if existe == 0:
						consulta = "insert into recetacontacto(idconsulta, idojo,fechacaducidad, poder, cb, dia, cil, eje, agregar, color, tipo) values(%s,1,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						cursor.execute(consulta, (idconsulta, lcfechacad, lcpoderoi,lccboi, lcdiaoi, lcciloi, lcejeoi, lcagregaroi, lccoloroi, lctipooi))
						consulta = "insert into recetacontacto(idconsulta, idojo,fechacaducidad, poder, cb, dia, cil, eje, agregar, color, tipo) values(%s,2,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						cursor.execute(consulta, (idconsulta, lcfechacad, lcpoderod,lccbod, lcdiaod, lccilod, lcejeod, lcagregarod, lccolorod, lctipood))
						consulta = "insert into recetagotero(idconsulta, medicamento1, descripcion1, medicamento2,  descripcion2) values(%s,%s,%s,%s,%s)"
						cursor.execute(consulta, (idconsulta, gmed1, gdesc1,gmed2, gdesc2))
					else:
						consulta = "update recetacontacto set fechacaducidad = %s, poder = %s, cb = %s, dia = %s, cil = %s, eje = %s, agregar = %s, color = %s, tipo = %s where idconsulta = %s and idojo = 1;"
						cursor.execute(consulta, (lcfechacad, lcpoderoi, lccboi, lcdiaoi, lcciloi, lcejeoi, lcagregaroi, lccoloroi, lctipooi, idconsulta))
						consulta = "update recetacontacto set fechacaducidad = %s, poder = %s, cb = %s, dia = %s, cil = %s, eje = %s, agregar = %s, color = %s, tipo = %s where idconsulta = %s and idojo = 2;"
						cursor.execute(consulta, (lcfechacad, lcpoderod, lccbod, lcdiaod, lccilod, lcejeod, lcagregarod, lccolorod, lctipood, idconsulta))
						consulta = "update recetagotero set medicamento1 = %s, descripcion1 = %s, medicamento2 = %s, descripcion2 = %s where idconsulta = %s;"
						cursor.execute(consulta, (gmed1, gdesc1, gmed2, gdesc2, idconsulta))
					consulta = "update consulta set proximacita = %s where idconsulta = %s"
					cursor.execute(consulta, (gfechacad, idconsulta))
					consulta = "update recetareferencia set lugar = %s, descripcion = %s where idconsulta = %s"
					cursor.execute(consulta, (lugar, descripcion, idconsulta))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('recetas', idconsulta=idconsulta))
	return render_template('recetas.html', title='Recetas', logeado=logeado, dataconsulta=dataconsulta, rf = rf, 
	lenterecomendado=lenterecomendado, lencons=lencons, datagotero=datagotero, recetaref=recetaref, idconsulta=idconsulta)

@app.route("/venta/<idconsulta>", methods=['GET', 'POST'])
def venta(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idservicios, servicio, precio from servicios;"
				cursor.execute(consulta)
				servicios = cursor.fetchall()
				consulta = "SELECT idlenteheader, nombre, idlaboratorio from lenteheader;"
				cursor.execute(consulta)
				lenteheader = cursor.fetchall()
				consulta = "SELECT idlaboratorio, nombre from laboratorio;"
				cursor.execute(consulta)
				laboratorios = cursor.fetchall()
				consulta = "SELECT idlentedesc, idlenteheader, nombre, precio, preciosug from lentedesc;"
				cursor.execute(consulta)
				lentedesc = cursor.fetchall()
				consulta = "select a.idaro, m.marca, a.codigo, a.color, a.precio from aro a inner join marca m on a.idmarca = m.idmarca where a.cantidad > 0 order by m.marca asc;"
				cursor.execute(consulta)
				aros = cursor.fetchall()
				consulta = "select nombrecliente, apellidocliente, nit, coddesc from facturaheader group by nit order by fecha desc;"
				cursor.execute(consulta)
				datafacturas = cursor.fetchall()
				consulta = "select p.nombre1, p.nombre2, p.apellido1, p.apellido2 from paciente p inner join consulta c on c.idpaciente = p.idpaciente where c.idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				datapaciente = cursor.fetchone()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		try:
			referido = request.form["referido"]
			nombreref = request.form["referidonombre"]
		except:
			referido = ""
			nombreref = ""
		nomcliente = request.form["nomcliente"]
		apecliente = request.form["apecliente"]
		nit = request.form["nit"]
		coddesc = request.form["coddesc"]
		if len(coddesc) < 1:
			coddesc = 0
		restotgen = float(request.form["restotgen"])
		resdesc = float(request.form["resdesc"])
		restotcan = float(request.form["restotcan"])
		compraro = request.form["aro"]
		if(compraro != '0'):
			idaro = request.form["idaro"]
			if len(idaro) < 1:
				idaro = 0
			precioaro = float(compraro)
		else:
			idaro = 0
			precioaro = 0
		
		comprlen = request.form["lente"]
		lab = request.form['lab']
		if len(lab) < 1:
			lab = 0
		if(comprlen != '0'):
			preciolente = float(comprlen)
			if lab == 1 or lab == '1':
				try:
					antireflejo = request.form['antireflejo']
				except:
					antireflejo = '-'
				try:
					montaje = request.form['montaje1']
				except:
					montaje = '-'
				try:
					tinte = request.form['tinte']
				except:
					tinte = '-'
				try:
					perforado = request.form['perforado1']
					perforado = request.form['cantperf']
				except:
					perforado = '0'
				try:
					ranurado = request.form['ranurado1']
				except:
					ranurado = '-'
				try:
					facetado = request.form['facetado']
				except:
					facetado = '-'
				try:
					solo1ojo = request.form['solo1ojo']
				except:
					solo1ojo = '-'
				try:
					prismas = request.form['prismas']
				except:
					prismas = '-'
				try:
					doscaras = request.form['doscaras']
				except:
					doscaras = '-'
				try:
					moldes = request.form['moldes']
				except:
					moldes = '-'
				idlenteoi = request.form["ld"]
				idlenteod = request.form["ld"]
				filtro = '0'
			elif lab == 2 or lab == '2':
				antireflejo = '-'
				try:
					montaje = request.form['montaje']
				except:
					montaje = '-'
				try:
					perforado = request.form['perforado']
				except:
					perforado = '0'
				try:
					ranurado = request.form['ranurado']
				except:
					ranurado = '-'
				idlenteoi = request.form["lenteoloi"]
				idlenteod = request.form["lenteolod"]
				filtro = request.form["filtrool"]
				tinte = '-'
				facetado = '-'
				solo1ojo = '-'
				prismas = '-'
				doscaras = '-'
				moldes = '-'
		else:
			idlenteoi = 0
			idlenteod = 0
			preciolente = 0
			tinte = '-'
			facetado = '-'
			solo1ojo = '-'
			prismas = '-'
			doscaras = '-'
			moldes = '-'
			montaje = '-'
			antireflejo = '-'
			perforado = '0'
			ranurado = '-'
			filtro = '0'
		try:
			cons = request.form["precons"]
			cons = 1
		except:
			cons = 0
		totalaux = float(restotcan)
		topes = request.form["topes"]
		colgadores = request.form["colgadores"]
		if cons == 1:
			totalaux = totalaux - 50
		if precioaro == 0:
			preciolente = totalaux
		elif preciolente == 0:
			precioaro = totalaux
		else:
			precioaro = totalaux - preciolente
		today = date.today()
		d1 = today.strftime("%d/%m/%Y")
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT nombre, cantidad FROM accesorios ORDER BY idaccesorios"
					cursor.execute(consulta)
					accesorios = cursor.fetchall()
					tottopes = int(accesorios[0][1]) - int(topes)
					totcolgadores = int(accesorios[1][1]) - int(colgadores)
					consulta = "UPDATE accesorios set cantidad = " + str(tottopes) + " WHERE idaccesorios = 1"
					cursor.execute(consulta)
					consulta = "UPDATE accesorios set cantidad = " + str(totcolgadores) + " WHERE idaccesorios = 2"
					cursor.execute(consulta)
					consulta = "insert into facturaheader(nombrecliente, apellidocliente, nit, preciogen, descuento, total, coddesc, fecha, idconsulta, idlaboratorio, iduser) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
					cursor.execute(consulta, (nomcliente, apecliente, nit, restotgen, resdesc, restotcan, coddesc, date.today(),idconsulta, lab, session['iduser1']))
				conexion.commit()
				with conexion.cursor() as cursor:
					consulta = "select max(idfacturaheader) from facturaheader;"
					cursor.execute(consulta)
					idfh = cursor.fetchall()
					idfh = idfh[0][0]
					consulta = "insert into facturadesc(idaro, idlenteoi, idlenteod, consulta, idfacturaheader, precioaro, preciolente, antireflejo, montaje, tinte, perforado, ranurado, facetado, solo1ojo, prismas, doscaras, moldes, filtro) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (idaro, idlenteoi, idlenteod, cons, idfh, precioaro, preciolente, antireflejo, montaje, tinte, perforado, ranurado, facetado, solo1ojo, prismas, doscaras, moldes, filtro))
					if session['iduser1'] == '3' or session['iduser1'] == 3:
						if nombreref == "":
							cantcomision = round(float(restotcan * 0.03), 2)
							consulta = 'insert into comisiones(nombreliquidacion, totalventa, comision, idfacturaheader) values (%s, %s, %s, %s);'
							cursor.execute(consulta, ('Kevin Avendaño', restotcan, cantcomision, idfh))
						else:
							consulta = 'insert into comisiones(nombreliquidacion, totalventa, comision, idfacturaheader) values (%s, %s, %s, %s);'
							cantcomision = round(float(restotcan * 0.025), 2)
							cursor.execute(consulta, ('Kevin Avendaño', restotcan, cantcomision, idfh))
							cantcomision = round(float(restotcan * 0.005), 2)
							cursor.execute(consulta, (nombreref, restotcan, cantcomision, idfh))
					else:
						consulta = 'insert into comisiones(nombreliquidacion, totalventa, comision, idfacturaheader) values (%s, %s, %s, %s);'
						nombreopto = session['nombreuser1'] + ' ' + session['apellidouser1']
						if nombreref == "":
							cantcomision = round(float(restotcan * 0.02), 2)
							cantcomision1 = round(float(restotcan * 0.01), 2)
							cursor.execute(consulta, (nombreopto, restotcan, cantcomision, idfh))
							cursor.execute(consulta, ('Kevin Avendaño', restotcan, cantcomision1, idfh))
						else:
							cantcomision = round(float(restotcan * 0.0175), 2)
							cantcomision1 = round(float(restotcan * 0.0075), 2)
							cantcomision2 = round(float(restotcan * 0.005), 2)
							cursor.execute(consulta, (nombreopto, restotcan, cantcomision, idfh))
							cursor.execute(consulta, ('Kevin Avendaño', restotcan, cantcomision1, idfh))
							cursor.execute(consulta, (nombreref, restotcan, cantcomision2, idfh))
					if idaro != 0 and idaro != '0':
						consulta = "select cantidad from aro where idaro = %s;"
						cursor.execute(consulta, idaro)
						cantidadaro = cursor.fetchall()
						cantidadaro = int(cantidadaro[0][0]) - 1
						consulta = "Update aro set cantidad = %s where idaro = %s;"
						cursor.execute(consulta, (cantidadaro, idaro))
					conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('aprobados'))
	return render_template('venta.html', title='Venta', logeado=logeado, lenteheader=lenteheader, lentedesc=lentedesc, aros=aros, 
	datafacturas=datafacturas, laboratorios=laboratorios, servicios=servicios, datapaciente = datapaciente)

@app.route('/comisionliquidar', methods=['GET', 'POST'])
def comisionliquidar():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = 'select f.nombrecliente, f.apellidocliente, f.nit, DATE_FORMAT(f.fecha, "%d/%m/%Y"), c.totalventa, c.comision, c.nombreliquidacion, c.idcomisiones from facturaheader f inner join comisiones c on c.idfacturaheader = f.idfacturaheader where c.liquidado = 0 and c.activo = 1 ORDER BY f.fecha desc, f.nombrecliente asc;'
				cursor.execute(consulta)
				comisiones = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('comisionliquidar.html', title='Comisiones por Liquidar', logeado=logeado, comisiones=comisiones)

@app.route('/comision', methods=['GET', 'POST'])
def comision():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = 'select f.nombrecliente, f.apellidocliente, f.nit, DATE_FORMAT(f.fecha, "%d/%m/%Y"), c.totalventa, c.comision, c.nombreliquidacion, DATE_FORMAT(c.fechaliquidado, "%d/%m/%Y") from facturaheader f inner join comisiones c on c.idfacturaheader = f.idfacturaheader where c.liquidado = 1 ORDER BY f.fecha desc, f.nombrecliente asc;'
				cursor.execute(consulta)
				comisiones = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('comision.html', title='Comisiones Liquidadas', logeado=logeado, comisiones=comisiones)

@app.route('/liquidarcomision/<idcomision>', methods=['GET', 'POST'])
def liquidarcomision(idcomision):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = 'update comisiones set liquidado = 1, fechaliquidado = %s where idcomisiones = %s;'
				cursor.execute(consulta, (date.today(), idcomision))
			conexion.commit()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return redirect(url_for('comisionliquidar'))

@app.route("/factura/<idfacturaheader>", methods=['GET', 'POST'])
def factura(idfacturaheader):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "Select h.nombrecliente, h.apellidocliente, h.nit, h.preciogen, h.descuento, h.total, DATE_FORMAT(h.fecha, '%d/%m/%Y'), d.idaro, d.idlenteoi, d.idlenteod, d.precioaro, d.preciolente, d.antireflejo, d.montaje, d.tinte, d.perforado, d.ranurado, d.facetado, d.solo1ojo, d.prismas, d.doscaras, d.moldes, d.filtro, h.coddesc, d.consulta from facturaheader h inner join facturadesc d on h.idfacturaheader = d.idfacturaheader where h.idfacturaheader = " + str(idfacturaheader) + ";"
				cursor.execute(consulta)
				dataventa = cursor.fetchall()
				try:
					consulta = "select a.idaro, m.marca, a.codigo, a.color from aro a inner join marca m on a.idmarca = m.idmarca where a.idaro = %s;"
					cursor.execute(consulta, dataventa[0][7])
					dataaro = cursor.fetchall()
					dataaro = dataaro[0]
				except:
					dataaro = [0,'None','None', 'None']
				datalente = []
				try:
					consulta = 'select nombre from lentedesc where idlentedesc = %s'
					cursor.execute(consulta, dataventa[0][8])
					datalente.append(cursor.fetchone())
				except:
					datalente.append(['None'])
				try:
					consulta = 'select nombre from lentedesc where idlentedesc = %s'
					cursor.execute(consulta, dataventa[0][9])
					datalente.append(cursor.fetchone())
				except:
					datalente.append(['None'])
				datalente.append(cursor.fetchone())

		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('factura.html', title='Factura', logeado=logeado, dataventa=dataventa, dataaro=dataaro, datalente=datalente, idfacturaheader=idfacturaheader)

@app.route("/segventas/<idfacturaheader>", methods=['GET', 'POST'])
def segventas(idfacturaheader):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "Select h.nombrecliente, h.apellidocliente, h.nit, h.preciogen, h.descuento, h.total, DATE_FORMAT(h.fecha, '%d/%m/%Y'), d.idaro, d.idlenteoi, d.idlenteod, d.precioaro, d.preciolente, d.antireflejo, d.montaje, d.tinte, d.perforado, d.ranurado, d.facetado, d.solo1ojo, d.prismas, d.doscaras, d.moldes, d.filtro, h.coddesc, d.consulta from facturaheader h inner join facturadesc d on h.idfacturaheader = d.idfacturaheader where h.idfacturaheader = " + str(idfacturaheader) + ";"
				print(consulta)
				cursor.execute(consulta)
				dataventa = cursor.fetchall()
				consulta = "select terminado from facturaheader where idfacturaheader = " + str(idfacturaheader)
				print(consulta)
				cursor.execute(consulta)
				terminado = cursor.fetchone()
				try:
					consulta = "select a.idaro, m.marca, a.codigo, a.color from aro a inner join marca m on a.idmarca = m.idmarca where a.idaro = %s;"
					cursor.execute(consulta, dataventa[0][7])
					dataaro = cursor.fetchall()
					dataaro = dataaro[0]
				except:
					dataaro = [0,'None','None', 'None']
				datalente = []
				try:
					consulta = 'select nombre from lentedesc where idlentedesc = %s'
					cursor.execute(consulta, dataventa[0][8])
					datalente.append(cursor.fetchone())
				except:
					datalente.append(['None'])
				try:
					consulta = 'select nombre from lentedesc where idlentedesc = %s'
					cursor.execute(consulta, dataventa[0][9])
					datalente.append(cursor.fetchone())
				except:
					datalente.append(['None'])
				consulta = 'select s.comentario, s.fecha, u.nombre, u.apellido from segventas s inner join user u on s.iduser = u.iduser where idfacturaheader = %s order by s.fecha desc'
				cursor.execute(consulta, idfacturaheader)
				comentarios = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		comentario = request.form['comentario']
		fechaact = datetime.datetime.now()
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = 'INSERT INTO segventas(comentario, fecha, iduser, idfacturaheader) values (%s, %s, %s, %s);'
					cursor.execute(consulta, (comentario, fechaact, session['iduser1'], idfacturaheader))
					if request.form['accion'] == 'fin':
						consulta = 'UPDATE facturaheader set terminado = 1 where idfacturaheader = ' + str(idfacturaheader)
						cursor.execute(consulta)
						consulta = 'UPDATE comisiones set activo = 1 where idfacturaheader = ' + str(idfacturaheader)
						cursor.execute(consulta)
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('verventas'))
	return render_template('segventas.html', title='Seguimiento', logeado=logeado, dataventa=dataventa, dataaro=dataaro, datalente=datalente, idfacturaheader=idfacturaheader, comentarios=comentarios, terminado=terminado)

@app.route('/imprimir/<idfacturaheader>')
def imprimir(idfacturaheader):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "Select h.nombrecliente, h.apellidocliente, h.nit, h.preciogen, h.descuento, h.total, DATE_FORMAT(h.fecha, '%d/%m/%Y'), d.idaro, d.idlenteoi, d.idlenteod, d.precioaro, d.preciolente, d.antireflejo, d.montaje, d.tinte, d.perforado, d.ranurado, d.facetado, d.solo1ojo, d.prismas, d.doscaras, d.moldes, d.filtro, h.coddesc, d.consulta from facturaheader h inner join facturadesc d on h.idfacturaheader = d.idfacturaheader where h.idfacturaheader = " + str(idfacturaheader) + ";"
				print(consulta)
				cursor.execute(consulta)
				dataventa = cursor.fetchall()
				try:
					consulta = "select a.idaro, m.marca, a.codigo, a.color from aro a inner join marca m on a.idmarca = m.idmarca where a.idaro = %s;"
					cursor.execute(consulta, dataventa[0][7])
					dataaro = cursor.fetchall()
					dataaro = dataaro[0]
				except:
					dataaro = [0,'None','None', 'None']
				datalente = []
				consulta = 'select nombre from lentedesc where idlentedesc = %s'
				cursor.execute(consulta, dataventa[0][8])
				datalente.append(cursor.fetchone())
				consulta = 'select nombre from lentedesc where idlentedesc = %s'
				cursor.execute(consulta, dataventa[0][9])
				datalente.append(cursor.fetchone())

		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	
	rendered = render_template('descventa.html', title='Factura', logeado=logeado, dataventa=dataventa, dataaro=dataaro, datalente=datalente)
	options = {'enable-local-file-access': None, 'page-size': 'A8', 'orientation': 'Portrait', 'margin-left': '0', 'margin-right': '0', 'margin-top': '0', 'margin-bottom': '5', 'encoding': 'utf-8', 'zoom': '0.8'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=reportediario.pdf'
	print(response)
	return response

@app.route("/pendaprobarc/<idconsulta>", methods=['GET', 'POST'])
def pendaprobarc(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('home'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "select idusolen, uso from usolen;"
				cursor.execute(consulta)
				usolen = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	dateac = datetime.date.today()
	year = dateac.strftime("%Y")
	year = int(year)
	nervos = []
	nervo = 1
	for i in range(11):
		nervos.append(nervo*i)
	numeros = []
	numero = 0
	for i in range(36):
		numeros.append(numero)
		numero = numero + 1
	mms = []
	mm = 0
	for i in range(8):
		mms.append(mm)
		mm = mm + 5
	anios = []
	for i in range(80):
		anios.append(year)
		year = year - 1
	cincos = []
	cinco = 0
	for i in range(15):
		cincos.append(cinco)
		cinco = cinco + 5
	meses = [[1, "Enero"],[2, "Febrero"],[3, "Marzo"],[4, "Abril"],[5, "Mayo"],[6, "Junio"],[7, "Julio"],[8, "Agosto"],[9, "Septiembre"],[10, "Octubre"],[11, "Noviembre"],[12, "Diciembre"]]
	enfermedades = [['Diabetes Mellitus'],['Hipertensión Arterial'],['Artritis Reumatoidea'],['Virus Inmunodeficiencia Humana']]
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idpaciente, idestudiante, ojoambliopia, tipoametropia, idusolen, proximacita, dnp, dnp1, dnp2, dnp3, ultimaevmes, ultimaevanio, tiempolen, add1, add2, add3, add11, add22, add33, emetropia, antimetropia, anisometropia, patologiaocular, lentesoftalmicos, lentescontacto, refoftalmologica, farmaco, motivoconsulta, nota, ambliopiaoi, ambliopiaod, ametropiaoi from consulta where idconsulta = "+ str(idconsulta) + ";"
				cursor.execute(consulta)
				dataconsulta = cursor.fetchall()
				idpaciente = dataconsulta[0][0]
				idestudiante = dataconsulta[0][1]
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT nombre, apellido, carnet from estudiante where idestudiante = %s"
				cursor.execute(consulta, (idestudiante))
				estudiante = cursor.fetchall()
				estudiante = estudiante[0]
				consulta = "select idrelacionvenaarteria, relacion from relacionvenaarteria;"
				cursor.execute(consulta)
				relva = cursor.fetchall()
				consulta = "select idtipolen, tipo from tipolen;"
				cursor.execute(consulta)
				tipolen = cursor.fetchall()
				consulta = "select idmateriallen, material from materiallen;"
				cursor.execute(consulta)
				materiallen = cursor.fetchall()
				consulta = "select idfiltrolen, filtro from filtrolen order by filtro asc;"
				cursor.execute(consulta)
				filtrolen = cursor.fetchall()
				consulta = "select idcolorlen, color from colorlen;"
				cursor.execute(consulta)
				colorlen = cursor.fetchall()
				consulta = "select idlentedetallado, lentedetallado from lentedetallado;"
				cursor.execute(consulta)
				lentedetalladolen = cursor.fetchall()
				consulta = "select idojo, ojo from ojo;"
				cursor.execute(consulta)
				dataojo = cursor.fetchall()
				consulta = "select idtipoametropia, tipo from tipoametropia;"
				cursor.execute(consulta)
				dataametropia = cursor.fetchall()
				consulta = "SELECT p.nombre1, p.nombre2, p.apellido1, p.apellido2, p.fechanac, s.sexo, p.profesion, p.direccion, p.cui, p.telefono, p.telefono2 from paciente p inner join sexo s on p.idsexo = s.idsexo where idpaciente = %s"
				cursor.execute(consulta, (idpaciente))
				paciente = cursor.fetchall()
				paciente = paciente[0]
				consulta = "SELECT oftalmologicos, familiares, glaucoma, alergicas, idantecedentes from antecedentes where idpaciente = %s;"
				cursor.execute(consulta, idpaciente)
				antecedentes = cursor.fetchone()
				idantecedentes = antecedentes[4]
				consulta = "SELECT enfermedad, tiempoevolucion, control from antmed where idantecedentes = %s;"
				cursor.execute(consulta, idantecedentes)
				antmed = cursor.fetchall()
				numantmed = len(antmed)
				consulta = "SELECT cirugia, tiempoevolucion, control from antquir where idantecedentes = %s;"
				cursor.execute(consulta, idantecedentes)
				antqui = cursor.fetchall()
				numantqui = len(antqui)
				consulta = "SELECT tipo, material, filtro, color, lentedetallado from lenterecomendado where idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				lenterecomendado = cursor.fetchall()
				av = []
				consulta = "SELECT avl, phae, avc from agudezavisual where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				av.append(aux)
				consulta = "SELECT avl, phae, avc from agudezavisual where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				av.append(aux)
				ra = []
				consulta = "SELECT esfera, cilindro, eje, prisma, avcc1 from refact where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				ra.append(aux)
				consulta = "SELECT esfera, cilindro, eje, prisma, avcc1 from refact where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				ra.append(aux)
				vc = []
				consulta = "SELECT esfera, cilindo, eje, prisma, avcc from ravc where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				vc.append(aux)
				consulta = "SELECT esfera, cilindo, eje, prisma, avcc from ravc where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				vc.append(aux)
				roa = []
				consulta = "SELECT esfera, cilindro, eje, prisma, dvertice, avcc from refobjal where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				roa.append(aux)
				consulta = "SELECT esfera, cilindro, eje, prisma, dvertice, avcc from refobjal where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				roa.append(aux)
				ror = []
				consulta = "SELECT esfera, cilindro, eje, prisma, dvertice, avcc from refobjref where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				ror.append(aux)
				consulta = "SELECT esfera, cilindro, eje, prisma, dvertice, avcc from refobjref where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				ror.append(aux)
				rs = []
				consulta = "SELECT esfera, cilindro, eje, prisma, avcc, pruamb, testbi, equibino, pruest, ciljackson from refsub where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rs.append(aux)
				consulta = "SELECT esfera, cilindro, eje, prisma, avcc, pruamb, testbi, equibino from refsub where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rs.append(aux)
				rf = []
				consulta = "SELECT esfera1, esfera2, esfera3, cilindro1, cilindro2, cilindro3, eje1, eje2, eje3, prisma1, prisma2, prisma3, avcc1, avcc2, avcc3 from reffin where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rf.append(aux)
				consulta = "SELECT esfera1, esfera2, esfera3, cilindro1, cilindro2, cilindro3, eje1, eje2, eje3, prisma1, prisma2, prisma3, avcc1, avcc2, avcc3 from reffin where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rf.append(aux)
				mo = []
				consulta = "SELECT mmf, forias, tropias, ducciones, versiones, convergencia, ortoforico from motocu where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				mo.append(aux)
				consulta = "SELECT mmf, forias, tropias, ducciones, versiones, convergencia, ortoforico from motocu where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				mo.append(aux)
				obs = []
				consulta = "SELECT valnormales, orbita, cejas, lagrima, viaslag, parpados, conjuntiva, esclera, cornea, camara, iris, pupila, cristalino, vitreo, nervioop, retinapp, retinape,retinamac, schirmer, but from observaciones where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				obs.append(aux)
				consulta = "SELECT valnormales, orbita, cejas, lagrima, viaslag, parpados, conjuntiva, esclera, cornea, camara, iris, pupila, cristalino, vitreo, nervioop, retinapp, retinape,retinamac, schirmer, but from observaciones where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				obs.append(aux)
				consulta = "select medicamento1, descripcion1, medicamento2, descripcion2 from recetagotero where idconsulta = %s"
				cursor.execute(consulta,idconsulta)
				gotero = cursor.fetchone()
				consulta = "select lugar, descripcion from recetareferencia where idconsulta = %s"
				cursor.execute(consulta,idconsulta)
				referencia = cursor.fetchone()
				
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		#panel2
		"""
		ultimaevmes = request.form["ultimaevmes"]
		ultimaevanio = request.form["ultimaevanio"]
		tiempolentes = request.form["tiempolentes"]
		antoftal = request.form["antoftal"]
		antfam = request.form["antfam"]
		antaler = request.form["antaler"]
		antgla = request.form["antgla"]
		numantmed = request.form["numantmed"]
		numantqui = request.form["numantqui"]
		numantmed = int(numantmed)
		numantqui = int(numantqui)
		antmed = []
		antqui = []
		
		for i in range(numantmed):
			aux = 'enfermedad' + str(i+1)
			enfermedad = request.form[aux]
			aux = 'tiempoevolucionm' + str(i+1)
			tiempoev = request.form[aux]
			aux = 'controlm' + str(i+1)
			control = request.form[aux]
			aux = [enfermedad, tiempoev, control]
			antmed.append(aux)
		for i in range(numantqui):
			aux = 'cirugia' + str(i+1)
			cirugia = request.form[aux]
			aux = 'tiempoevolucionq' + str(i+1)
			tiempoev = request.form[aux]
			aux = 'controlq' + str(i+1)
			control = request.form[aux]
			aux = [cirugia, tiempoev, control]
			antqui.append(aux)
		"""
		#panel3
		avlod = request.form["avlod"]
		avloi = request.form["avloi"]
		aeod = request.form["aeod"]
		aeoi = request.form["aeoi"]
		avcod = request.form["avcod"]
		avcoi = request.form["avcoi"]
		#panel4
		raeod = request.form["raeod"]
		racod = request.form["racod"]
		racod = float(racod)
		if racod > 0:
			racod = racod * -1
		raejod = request.form["raejod"]
		rapod = request.form["rapod"]
		if len(rapod) < 1:
			rapod = 0
		raavcc1od = request.form["raavcc1od"]
		raeoi = request.form["raeoi"]
		racoi = request.form["racoi"]
		racoi = float(racoi)
		if racoi > 0:
			racoi = racoi * -1
		raejoi = request.form["raejoi"]
		rapoi = request.form["rapoi"]
		if len(rapoi) < 1:
			rapoi = 0
		raavcc1oi = request.form["raavcc1oi"]
		add1 = request.form["add1"]
		if len(add1) < 1:
			add1 = 0
		add2 = request.form["add2"]
		if len(add2) < 1:
			add2 = 0
		add3 = request.form["add3"]
		if len(add3) < 1:
			add3 = 0
		dnp1 = request.form["dnp1"]
		if len(dnp1) < 1:
			dnp1 = 0
		vceod = request.form["vceod"]
		vccod = request.form["vccod"]
		vccod = float(vccod)
		if vccod > 0:
			vccod = vccod * -1
		vcejod = request.form["vcejod"]
		vcpod = request.form["vcpod"]
		if len(vcpod) < 1:
			vcpod = 0
		vcavccod = request.form["vcavccod"]
		vceoi = request.form["vceoi"]
		vccoi = request.form["vccoi"]
		vccoi = float(vccoi)
		if vccoi > 0:
			vccoi = vccoi * -1
		vcejoi = request.form["vcejoi"]
		vcpoi = request.form["vcpoi"]
		if len(vcpoi) < 1:
			vcpoi = 0
		vcavccoi = request.form["vcavccoi"]
		#panel5
		roaeod = request.form["roaeod"]
		roacod = request.form["roacod"]
		roacod = float(roacod)
		if roacod > 0:
			roacod = roacod * -1
		roaejod = request.form["roaejod"]
		roapod = request.form["roapod"]
		if len(roapod) < 1:
			roapod = 0
		roavod = request.form["roavod"]
		roaavccod = request.form["roaavccod"]
		roaeoi = request.form["roaeoi"]
		roacoi = request.form["roacoi"]
		roacoi = float(roacoi)
		if roacoi > 0:
			roacoi = roacoi * -1
		roaejoi = request.form["roaejoi"]
		roapoi = request.form["roapoi"]
		if len(roapoi) < 1:
			roapoi = 0
		roavoi = request.form["roavoi"]
		roaavccoi = request.form["roaavccoi"]
		roreod = request.form["roreod"]
		rorcod = request.form["rorcod"]
		rorcod = float(rorcod)
		if rorcod > 0:
			rorcod = rorcod * -1
		rorejod = request.form["rorejod"]
		rorpod = request.form["rorpod"]
		if len(rorpod) < 1:
			rorpod = 0
		rorvod = request.form["rorvod"]
		roravccod = request.form["roravccod"]
		roreoi = request.form["roreoi"]
		rorcoi = request.form["rorcoi"]
		rorcoi = float(rorcoi)
		if rorcoi > 0:
			rorcoi = rorcoi * -1
		rorejoi = request.form["rorejoi"]
		rorpoi = request.form["rorpoi"]
		if len(rorpoi) < 1:
			rorpoi = 0
		rorvoi = request.form["rorvoi"]
		roravccoi = request.form["roravccoi"]
		#panel6
		rseod = request.form["rseod"]
		rscod = request.form["rscod"]
		rscod = float(rscod)
		if rscod > 0:
			rscod = rscod * -1
		rsejod = request.form["rsejod"]
		rspod = request.form["rspod"]
		if len(rspod) < 1:
			rspod = 0
		rsavccod = request.form["rsavccod"]
		rseoi = request.form["rseoi"]
		rscoi = request.form["rscoi"]
		rscoi = float(rscoi)
		if rscoi > 0:
			rscoi = rscoi * -1
		rsejoi = request.form["rsejoi"]
		rspoi = request.form["rspoi"]
		if len(rspoi) < 1:
			rspoi = 0
		rsavccoi = request.form["rsavccoi"]
		try:
			pruamb = request.form["pruamb"]
		except:
			pruamb = 0
		try:
			pruest = request.form["pruest"]
		except:
			pruest = 0
		try:
			testbi = request.form["testbi"]
		except:
			testbi = 0
		try:
			equibino = request.form["equibino"]
		except:
			equibino = 0
		try:
			ciljackson = request.form["ciljackson"]
		except:
			ciljackson = 0
		#panel7
		rfe1od = request.form["rfe1od"]
		rfe2od = request.form["rfe2od"]
		rfe3od = request.form["rfe3od"]
		if len(rfe2od) < 1:
			rfe2od = 0
		if len(rfe3od) < 1:
			rfe3od = 0
		rfc1od = request.form["rfc1od"]
		rfc1od = float(rfc1od)
		if rfc1od > 0:
			rfc1od = rfc1od * -1
		rfc2od = request.form["rfc2od"]
		rfc2od = float(rfc2od)
		if rfc2od > 0:
			rfc2od = rfc2od * -1
		rfc3od = request.form["rfc3od"]
		rfc3od = float(rfc3od)
		if rfc3od > 0:
			rfc3od = rfc3od * -1
		rfej1od = request.form["rfej1od"]
		rfej2od = request.form["rfej2od"]
		rfej3od = request.form["rfej3od"]
		if len(rfej2od) < 1:
			rfej2od = 0
		if len(rfej3od) < 1:
			rfej3od = 0
		rfp1od = request.form["rfp1od"]
		rfp2od = request.form["rfp2od"]
		rfp3od = request.form["rfp3od"]
		if len(rfp1od) < 1:
			rfp1od = 0
		if len(rfp2od) < 1:
			rfp2od = 0
		if len(rfp3od) < 1:
			rfp3od = 0
		rfavcc1od = request.form["rfavcc1od"]
		rfavcc2od = request.form["rfavcc2od"]
		rfavcc3od = request.form["rfavcc3od"]
		if len(rfavcc2od) < 1:
			rfavcc2od = 0
		if len(rfavcc3od) < 1:
			rfavcc3od = 0
		rfe1oi = request.form["rfe1oi"]
		rfe2oi = request.form["rfe2oi"]
		rfe3oi = request.form["rfe3oi"]
		if len(rfe1oi) < 1:
			rfe1oi = 0
		if len(rfe2oi) < 1:
			rfe2oi = 0
		if len(rfe3oi) < 1:
			rfe3oi = 0
		rfc1oi = request.form["rfc1oi"]
		if len(rfc1oi) < 1:
			rfc1oi = 0
		rfc1oi = float(rfc1oi)
		if rfc1oi > 0:
			rfc1oi = rfc1oi * -1
		rfc2oi = request.form["rfc2oi"]
		rfc2oi = float(rfc2oi)
		if rfc2oi > 0:
			rfc2oi = rfc2oi * -1
		rfc3oi = request.form["rfc3oi"]
		rfc3oi = float(rfc3oi)
		if rfc3oi > 0:
			rfc3oi = rfc3oi * -1
		rfej1oi = request.form["rfej1oi"]
		rfej2oi = request.form["rfej2oi"]
		rfej3oi = request.form["rfej3oi"]
		if len(rfej2oi) < 1:
			rfej2oi = 0
		if len(rfej3oi) < 1:
			rfej3oi = 0
		rfp1oi = request.form["rfp1oi"]
		rfp2oi = request.form["rfp2oi"]
		rfp3oi = request.form["rfp3oi"]
		if len(rfp1oi) < 1:
			rfp1oi = 0
		if len(rfp2oi) < 1:
			rfp2oi = 0
		if len(rfp3oi) < 1:
			rfp3oi = 0
		rfavcc1oi = request.form["rfavcc1oi"]
		rfavcc2oi = request.form["rfavcc2oi"]
		rfavcc3oi = request.form["rfavcc3oi"]
		if len(rfavcc2oi) < 1:
			rfavcc2oi = 0
		if len(rfavcc3oi) < 1:
			rfavcc3oi = 0
		dnp = request.form["dnp"]
		dnp2 = request.form["dnp2"]
		dnp3 = request.form["dnp3"]
		if len(dnp) < 1:
			dnp = 0
		if len(dnp2) < 1:
			dnp2 = 0
		if len(dnp3) < 1:
			dnp3 = 0
		add11 = request.form["add11"]
		add22 = request.form["add22"]
		add33 = request.form["add33"]
		if len(add11) < 1:
			add11 = 0
		if len(add22) < 1:
			add22 = 0
		if len(add33) < 1:
			add33 = 0
		#panel8
		mmfod = request.form["mmfod"]
		mmfoi = request.form["mmfoi"]
		forod = request.form["forod"]
		foroi = request.form["foroi"]
		trood = request.form["trood"]
		trooi = request.form["trooi"]
		duccod = request.form["duccod"]
		duccoi = request.form["duccoi"]
		versiones = request.form["versiones"]
		convergencia = request.form["convergencia"]
		if len(mmfod) < 1:
			mmfod = 0
		if len(mmfoi) < 1:
			mmfoi = 0
		if len(forod) < 1:
			forod = 0
		if len(foroi) < 1:
			foroi = 0
		if len(trood) < 1:
			trood = 0
		if len(trooi) < 1:
			trooi = 0
		if len(duccod) < 1:
			duccod = 0
		if len(duccoi) < 1:
			duccoi = 0
		if len(versiones) < 1:
			versiones = 0
		if len(convergencia) < 1:
			convergencia = 0	
		try:
			ortoforico = request.form["ortoforico"]
		except:
			ortoforico = 0
		#panel9
		try:
			ojsal = request.form["ojsal"]
		except:
			ojsal = 0
		orbod = request.form["orbod"]
		orboi = request.form["orboi"]
		cejod = request.form["cejod"]
		cejoi = request.form["cejoi"]
		lagod = request.form["lagod"]
		lagoi = request.form["lagoi"]
		schod = request.form["schod"]
		schoi = request.form["schoi"]
		butod = request.form["butod"]
		butoi = request.form["butoi"]
		if len(orbod) < 1:
			orbod = 0
		if len(orboi) < 1:
			orboi = 0
		if len(cejod) < 1:
			cejod = 0
		if len(cejoi) < 1:
			cejoi = 0
		if len(lagod) < 1:
			lagod = 0
		if len(lagoi) < 1:
			lagoi = 0
		if len(schod) < 1:
			schod = 0
		if len(schoi) < 1:
			schoi = 0
		if len(butod) < 1:
			butod = 0
		if len(butoi) < 1:
			butoi = 0	
		vilagod = request.form["vilagod"]
		vilagoi = request.form["vilagoi"]
		pypod = request.form["pypod"]
		pypoi = request.form["pypoi"]
		conjod = request.form["conjod"]
		conjoi = request.form["conjoi"]
		esclod = request.form["esclod"]
		escloi = request.form["escloi"]
		cornod = request.form["cornod"]
		cornoi = request.form["cornoi"]
		if len(vilagod) < 1:
			vilagod = 0
		if len(vilagoi) < 1:
			vilagoi = 0
		if len(pypod) < 1:
			pypod = 0
		if len(pypoi) < 1:
			pypoi = 0
		if len(conjod) < 1:
			conjod = 0
		if len(conjoi) < 1:
			conjoi = 0
		if len(esclod) < 1:
			esclod = 0
		if len(escloi) < 1:
			escloi = 0
		if len(cornod) < 1:
			cornod = 0
		if len(cornoi) < 1:
			cornoi = 0	
		camaod = request.form["camaod"]
		camaoi = request.form["camaoi"]
		iriod = request.form["iriod"]
		irioi = request.form["irioi"]
		pupiod = request.form["pupiod"]
		pupioi = request.form["pupioi"]
		crisod = request.form["crisod"]
		crisoi = request.form["crisoi"]
		vitod = request.form["vitod"]
		vitoi = request.form["vitoi"]
		if len(camaod) < 1:
			camaod = 0
		if len(camaoi) < 1:
			camaoi = 0
		if len(iriod) < 1:
			iriod = 0
		if len(irioi) < 1:
			irioi = 0
		if len(pupiod) < 1:
			pupiod = 0
		if len(pupioi) < 1:
			pupioi = 0
		if len(crisod) < 1:
			crisod = 0
		if len(crisoi) < 1:
			crisoi = 0
		if len(vitod) < 1:
			vitod = 0
		if len(vitoi) < 1:
			vitoi = 0
		nervood = request.form["nervood"]
		nervooi = request.form["nervooi"]
		retppod = request.form["retppod"]
		retppoi = request.form["retppoi"]
		retpeod = request.form["retpeod"]
		retpeoi = request.form["retpeoi"]
		retmacod = request.form["retmacod"]
		retmacoi = request.form["retmacoi"]
		if len(nervood) < 1:
			nervood = 0
		if len(nervooi) < 1:
			nervooi = 0
		if len(retppod) < 1:
			retppod = 0
		if len(retppoi) < 1:
			retppoi = 0
		if len(retpeod) < 1:
			retpeod = 0
		if len(retpeoi) < 1:
			retpeoi = 0
		if len(retmacod) < 1:
			retmacod = 0
		if len(retmacoi) < 1:
			retmacoi = 0
		
		#panel10
		proxicita = request.form["proxicita"]
		usolent = request.form["usolent"]
		tipolent = request.form["tipolent"]
		materiallent = request.form["materiallent"]
		filtrolent = request.form["filtrolent"]
		colorlent = request.form["colorlent"]
		lentedetalladolent = request.form["lentedetalladolent"]
		ambliopia = request.form["ambliopia"]
		ametropia = request.form["ametropia"]
		notas = request.form["notas"]
		try:
			ambliopiaoi = request.form["ambliopiaoi"]
		except:
			ambliopiaoi = 0
		try:
			ambliopiaod = request.form["ambliopiaod"]
		except:
			ambliopiaod = 0
		ametropiaoi = request.form["ametropiaoi"]
		if len(ametropiaoi) < 1:
			ametropiaoi = 0
		try:
			emetropia = request.form["emetropia"]
		except:
			emetropia = 0
		try:
			antimetropia = request.form["antimetropia"]
		except:
			antimetropia = 0
		try:
			anisometropia = request.form["anisometropia"]
		except:
			anisometropia = 0
		try:
			patologiaocular = request.form["patologiaocular"]
			patologiaoculartext = request.form["patologiaoculartext"]
		except:
			patologiaocular = 0
			patologiaoculartext = 0
		try:
			lentesoftalmicos = request.form["lentesoftalmicos"]
		except:
			lentesoftalmicos = 0
		try:
			lentescontacto = request.form["lentescontacto"]
		except:
			lentescontacto = 0
		try:
			refoftalmologica = request.form["refoftalmologica"]
		except:
			refoftalmologica = 0
		try:
			farmaco = request.form["farmaco"]
		except:
			farmaco = 0
		gmed1 = request.form["gmed1"]
		gdesc1 = request.form["gdesc1"]
		gmed2 = request.form["gmed2"]
		gdesc2 = request.form["gdesc2"]
		if len(gmed1) < 1:
			gmed1 = 0
		if len(gdesc1) < 1:
			gdesc1 = 0
		if len(gmed2) < 1:
			gmed2 = 0
		if len(gdesc2) < 1:
			gdesc2 = 0
		lugarref = request.form["lugarref"]
		descref = request.form["descref"]
		if len(lugarref) < 1:
			lugarref = 0
		if len(descref) < 1:
			descref = 0
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					"""
					#antecedentes
					consulta = "update antecedentes set oftalmologicos=%s, familiares=%s, glaucoma=%s, alergicas=%s where idpaciente=%s;"
					cursor.execute(consulta, (antoftal, antfam, antgla, antaler, idpaciente))
					for i in range(numantmed):
						consulta = "update antmed set enfermedad=%s, tiempoevolucion=%s, control=%s where idantecedentes=%s;"
						cursor.execute(consulta, (antmed[i][0], antmed[i][1], antmed[i][2], idantecedentes))
					for i in range(numantqui):
						consulta = "update antquir set cirugia=%s, tiempoevolucion=%s, control=%s where idantecedentes=%s;"
						cursor.execute(consulta, (antqui[i][0], antqui[i][1], antqui[i][2], idantecedentes))
					"""
					#agudeza visual
					consulta = "update agudezavisual set avl=%s, phae=%s, avc=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (avlod, aeod, avcod, idconsulta, 2))
					consulta = "update agudezavisual set avl=%s, phae=%s, avc=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (avloi, aeoi, avcoi, idconsulta, 1))
					#refraccion actual
					consulta = "update refact set esfera=%s, cilindro=%s, eje=%s, prisma=%s, avcc1=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (raeod, racod, raejod, rapod, raavcc1od, idconsulta, 2))
					consulta = "update refact set esfera=%s, cilindro=%s, eje=%s, prisma=%s, avcc1=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (raeoi, racoi, raejoi, rapoi, raavcc1oi, idconsulta, 1))
					consulta = "update ravc set esfera=%s, cilindo=%s, eje=%s, prisma=%s, avcc=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (vceod, vccod, vcejod, vcpod, vcavccod, idconsulta, 2))
					consulta = "update ravc set esfera=%s, cilindo=%s, eje=%s, prisma=%s, avcc=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (vceoi, vccoi, vcejoi, vcpoi, vcavccoi, idconsulta, 1))
					#refraccion objetiva
					consulta = "update refobjal set esfera=%s, cilindro=%s, eje=%s, prisma=%s, dvertice=%s, avcc=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (roaeod, roacod, roaejod,roapod, roavod, roaavccod, idconsulta, 2))
					consulta = "update refobjal set esfera=%s, cilindro=%s, eje=%s, prisma=%s, dvertice=%s, avcc=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (roaeoi, roacoi, roaejoi,roapoi, roavoi, roaavccoi, idconsulta, 1))
					consulta = "update refobjref set esfera=%s, cilindro=%s, eje=%s, prisma=%s, dvertice=%s, avcc=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (roreod, rorcod, rorejod,rorpod, rorvod, roravccod, idconsulta, 2))
					consulta = "update refobjref set esfera=%s, cilindro=%s, eje=%s, prisma=%s, dvertice=%s, avcc=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (roreoi, rorcoi, rorejoi,rorpoi, rorvoi, roravccoi, idconsulta, 1))
					#refraccion subjetiva
					consulta = "update refsub set esfera=%s, cilindro=%s, eje=%s, prisma=%s, avcc=%s, pruamb=%s, testbi=%s, equibino=%s, pruest=%s, ciljackson=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (rseod, rscod, rsejod, rspod, rsavccod, pruamb, testbi, equibino, pruest, ciljackson, idconsulta, 2))
					consulta = "update refsub set esfera=%s, cilindro=%s, eje=%s, prisma=%s, avcc=%s, pruamb=%s, testbi=%s, equibino=%s, pruest=%s, ciljackson=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (rseoi, rscoi, rsejoi, rspoi, rsavccoi, pruamb, testbi, equibino, pruest, ciljackson, idconsulta, 1))
					#refraccion final
					consulta = "update reffin set esfera1=%s, esfera2=%s, cilindro1=%s, cilindro2=%s, eje1=%s, eje2=%s, prisma1=%s, prisma2=%s, avcc1=%s, avcc2=%s, esfera3=%s, cilindro3=%s, eje3=%s, prisma3=%s, avcc3=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (rfe1od, rfe2od, rfc1od, rfc2od, rfej1od, rfej2od, rfp1od, rfp2od, rfavcc1od, rfavcc2od, rfe3od, rfc3od, rfej3od, rfp3od, rfavcc3od, idconsulta, 2))
					consulta = "update reffin set esfera1=%s, esfera2=%s, cilindro1=%s, cilindro2=%s, eje1=%s, eje2=%s, prisma1=%s, prisma2=%s, avcc1=%s, avcc2=%s, esfera3=%s, cilindro3=%s, eje3=%s, prisma3=%s, avcc3=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (rfe1oi, rfe2oi, rfc1oi, rfc2oi, rfej1oi, rfej2oi, rfp1oi, rfp2oi, rfavcc1oi, rfavcc2oi, rfe3oi, rfc3oi, rfej3oi, rfp3oi, rfavcc3oi, idconsulta, 1))
					#Motilidad Ocular
					consulta = "update motocu set mmf=%s, forias=%s, tropias=%s, ducciones=%s, versiones=%s, convergencia=%s, ortoforico=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (mmfod, forod, trood, duccod, versiones, convergencia, ortoforico, idconsulta, 2))
					consulta = "update motocu set mmf=%s, forias=%s, tropias=%s, ducciones=%s, versiones=%s, convergencia=%s, ortoforico=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (mmfoi, foroi, trooi, duccoi, versiones, convergencia, ortoforico, idconsulta, 1))
					#salud ocular
					consulta = "update observaciones set valnormales=%s, orbita=%s, cejas=%s, lagrima=%s, viaslag=%s, parpados=%s, conjuntiva=%s, esclera=%s, cornea=%s, camara=%s, iris=%s, pupila=%s, cristalino=%s, vitreo=%s, nervioop=%s, retinapp=%s, retinape=%s, retinamac=%s, schirmer=%s, but=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (ojsal, orbod, cejod, lagod, vilagod, pypod, conjod, esclod, cornod, camaod, iriod, pupiod, crisod, vitod, nervood, retppod, retpeod, retmacod, schod, butod, idconsulta, 2))
					consulta = "update observaciones set valnormales=%s, orbita=%s, cejas=%s, lagrima=%s, viaslag=%s, parpados=%s, conjuntiva=%s, esclera=%s, cornea=%s, camara=%s, iris=%s, pupila=%s, cristalino=%s, vitreo=%s, nervioop=%s, retinapp=%s, retinape=%s, retinamac=%s, schirmer=%s, but=%s where idconsulta=%s and idojo=%s;"
					cursor.execute(consulta, (ojsal, orboi, cejoi, lagoi, vilagoi, pypoi, conjoi, escloi, cornoi, camaoi, irioi, pupioi, crisoi, vitoi, nervooi, retppoi, retpeoi, retmacoi, schoi, butoi, idconsulta, 1))
					
					#consulta
					consulta = "update consulta set idusolen=%s, proximacita=%s, dnp=%s,dnp1=%s, add1=%s, add2=%s, add3=%s, add11=%s, add22=%s, add33=%s, aprobado=1, iduser=%s, dnp2=%s, dnp3=%s, ojoambliopia=%s, emetropia=%s, antimetropia=%s, tipoametropia=%s, anisometropia=%s, patologiaocular=%s, lentesoftalmicos=%s, lentescontacto=%s, refoftalmologica=%s, farmaco=%s, nota=%s, ambliopiaoi=%s, ambliopiaod=%s, ametropiaoi=%s where idconsulta = %s;"
					cursor.execute(consulta, (usolent, proxicita, dnp, dnp1, add1, add2, add3, add11, add22, add33, session['iduser1'], dnp2, dnp3, ambliopia, emetropia, antimetropia, ametropia, anisometropia, patologiaoculartext, lentesoftalmicos, lentescontacto, refoftalmologica, farmaco, notas, ambliopiaoi, ambliopiaod, ametropiaoi, idconsulta))
					#Lente Recomendado
					consulta = "update lenterecomendado set tipo = %s, material = %s, filtro = %s, color = %s,lentedetallado = %s where idconsulta = %s;"
					cursor.execute(consulta, (tipolent, materiallent, filtrolent, colorlent, lentedetalladolent, idconsulta))
					#gotero
					consulta = "update recetagotero set medicamento1 = %s, descripcion1 = %s, medicamento2 = %s, descripcion2 = %s where idconsulta = %s;"
					cursor.execute(consulta, (gmed1, gdesc1, gmed2, gdesc2, idconsulta))

					#referencia
					consulta = "update recetareferencia set lugar = %s, descripcion = %s where idconsulta = %s;"
					cursor.execute(consulta, (lugarref, descref, idconsulta))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('home'))
	return render_template('pendaprobarc.html', title='Pendiente de aprobación', logeado=logeado, estudiante=estudiante, paciente = paciente, 
		dataconsulta=dataconsulta, anios=anios, cincos=cincos, meses=meses, antecedentes = antecedentes, av=av, ra=ra, vc=vc, roa=roa, ror=ror, 
		rs=rs, rf=rf, mo=mo, obs=obs, usolen=usolen, numantmed=numantmed, numantqui=numantqui, antmed=antmed, antqui=antqui, enfermedades=enfermedades,
		nervos=nervos, mms=mms, numeros=numeros, relva=relva, tipolen=tipolen, materiallen=materiallen, filtrolen=filtrolen, colorlen=colorlen,
		lenterecomendado=lenterecomendado, dataojo=dataojo, dataametropia=dataametropia, gotero=gotero, lentedetalladolen=lentedetalladolen,referencia=referencia)

@app.route("/ver/<idconsulta>", methods=['GET', 'POST'])
def ver(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	if logeado == 0:
		return redirect(url_for('home'))
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "select idusolen, uso from usolen;"
				cursor.execute(consulta)
				usolen = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	dateac = datetime.date.today()
	year = dateac.strftime("%Y")
	year = int(year)
	nervos = []
	nervo = 1
	for i in range(11):
		nervos.append(nervo*i)
	numeros = []
	numero = 0
	for i in range(36):
		numeros.append(numero)
		numero = numero + 1
	mms = []
	mm = 0
	for i in range(8):
		mms.append(mm)
		mm = mm + 5
	anios = []
	for i in range(80):
		anios.append(year)
		year = year - 1
	cincos = []
	cinco = 0
	for i in range(15):
		cincos.append(cinco)
		cinco = cinco + 5
	meses = [[1, "Enero"],[2, "Febrero"],[3, "Marzo"],[4, "Abril"],[5, "Mayo"],[6, "Junio"],[7, "Julio"],[8, "Agosto"],[9, "Septiembre"],[10, "Octubre"],[11, "Noviembre"],[12, "Diciembre"]]
	enfermedades = [['Diabetes Mellitus'],['Hipertensión Arterial'],['Artritis Reumatoidea'],['Virus Inmunodeficiencia Humana']]
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idpaciente, idestudiante, ojoambliopia, tipoametropia, idusolen, proximacita, dnp, dnp1, dnp2, dnp3, ultimaevmes, ultimaevanio, tiempolen, add1, add2, add3, add11, add22, add33, emetropia, antimetropia, anisometropia, patologiaocular, lentesoftalmicos, lentescontacto, refoftalmologica, farmaco, nota, ambliopiaoi, ambliopiaod, ametropiaoi, motivoconsulta from consulta where idconsulta = "+ str(idconsulta) + ";"
				cursor.execute(consulta)
				dataconsulta = cursor.fetchall()
				idpaciente = dataconsulta[0][0]
				idestudiante = dataconsulta[0][1]
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT nombre, apellido, carnet from estudiante where idestudiante = %s"
				cursor.execute(consulta, (idestudiante))
				estudiante = cursor.fetchall()
				estudiante = estudiante[0]
				consulta = "select idrelacionvenaarteria, relacion from relacionvenaarteria;"
				cursor.execute(consulta)
				relva = cursor.fetchall()
				consulta = "select idtipolen, tipo from tipolen;"
				cursor.execute(consulta)
				tipolen = cursor.fetchall()
				consulta = "select idlentedetallado, lentedetallado from lentedetallado order by lentedetallado asc;"
				cursor.execute(consulta)
				lentedetalladolen = cursor.fetchall()
				consulta = "select idmateriallen, material from materiallen;"
				cursor.execute(consulta)
				materiallen = cursor.fetchall()
				consulta = "select idfiltrolen, filtro from filtrolen order by filtro asc;"
				cursor.execute(consulta)
				filtrolen = cursor.fetchall()
				consulta = "select idlentedetallado, lentedetallado from lentedetallado order by lentedetallado asc;"
				cursor.execute(consulta)
				lentedetalladolen = cursor.fetchall()
				consulta = "select idcolorlen, color from colorlen;"
				cursor.execute(consulta)
				colorlen = cursor.fetchall()
				consulta = "select idojo, ojo from ojo;"
				cursor.execute(consulta)
				dataojo = cursor.fetchall()
				consulta = "select idtipoametropia, tipo from tipoametropia;"
				cursor.execute(consulta)
				dataametropia = cursor.fetchall()
				consulta = "SELECT p.nombre1, p.nombre2, p.apellido1, p.apellido2, p.fechanac, s.sexo, p.profesion, p.direccion, p.cui, p.telefono, p.telefono2 from paciente p inner join sexo s on p.idsexo = s.idsexo where idpaciente = %s"
				cursor.execute(consulta, (idpaciente))
				paciente = cursor.fetchall()
				paciente = paciente[0]
				consulta = "SELECT oftalmologicos, familiares, glaucoma, alergicas, idantecedentes from antecedentes where idpaciente = %s;"
				cursor.execute(consulta, idpaciente)
				antecedentes = cursor.fetchone()
				idantecedentes = antecedentes[4]
				consulta = "SELECT enfermedad, tiempoevolucion, control, otro from antmed where idantecedentes = %s;"
				cursor.execute(consulta, idantecedentes)
				antmed = cursor.fetchall()
				numantmed = len(antmed)
				consulta = "SELECT cirugia, tiempoevolucion, control from antquir where idantecedentes = %s;"
				cursor.execute(consulta, idantecedentes)
				antqui = cursor.fetchall()
				numantqui = len(antqui)
				consulta = "SELECT tipo, material, filtro, color, lentedetallado from lenterecomendado where idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				lenterecomendado = cursor.fetchall()
				av = []
				consulta = "SELECT avl, phae, avc from agudezavisual where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				av.append(aux)
				consulta = "SELECT avl, phae, avc from agudezavisual where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				av.append(aux)
				ra = []
				consulta = "SELECT esfera, cilindro, eje, prisma, avcc1 from refact where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				ra.append(aux)
				consulta = "SELECT esfera, cilindro, eje, prisma, avcc1 from refact where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				ra.append(aux)
				vc = []
				consulta = "SELECT esfera, cilindo, eje, prisma, avcc from ravc where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				vc.append(aux)
				consulta = "SELECT esfera, cilindo, eje, prisma, avcc from ravc where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				vc.append(aux)
				roa = []
				consulta = "SELECT esfera, cilindro, eje, prisma, dvertice, avcc from refobjal where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				roa.append(aux)
				consulta = "SELECT esfera, cilindro, eje, prisma, dvertice, avcc from refobjal where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				roa.append(aux)
				ror = []
				consulta = "SELECT esfera, cilindro, eje, prisma, dvertice, avcc from refobjref where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				ror.append(aux)
				consulta = "SELECT esfera, cilindro, eje, prisma, dvertice, avcc from refobjref where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				ror.append(aux)
				rs = []
				consulta = "SELECT esfera, cilindro, eje, prisma, avcc, pruamb, testbi, equibino, pruest, ciljackson from refsub where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rs.append(aux)
				consulta = "SELECT esfera, cilindro, eje, prisma, avcc, pruamb, testbi, equibino from refsub where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rs.append(aux)
				rf = []
				consulta = "SELECT esfera1, esfera2, esfera3, cilindro1, cilindro2, cilindro3, eje1, eje2, eje3, prisma1, prisma2, prisma3, avcc1, avcc2, avcc3 from reffin where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rf.append(aux)
				consulta = "SELECT esfera1, esfera2, esfera3, cilindro1, cilindro2, cilindro3, eje1, eje2, eje3, prisma1, prisma2, prisma3, avcc1, avcc2, avcc3 from reffin where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rf.append(aux)
				mo = []
				consulta = "SELECT mmf, forias, tropias, ducciones, versiones, convergencia, ortoforico from motocu where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				mo.append(aux)
				consulta = "SELECT mmf, forias, tropias, ducciones, versiones, convergencia, ortoforico from motocu where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				mo.append(aux)
				obs = []
				consulta = "SELECT valnormales, orbita, cejas, lagrima, viaslag, parpados, conjuntiva, esclera, cornea, camara, iris, pupila, cristalino, vitreo, nervioop, retinapp, retinape,retinamac, schirmer, but from observaciones where idojo = 2 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				obs.append(aux)
				consulta = "SELECT valnormales, orbita, cejas, lagrima, viaslag, parpados, conjuntiva, esclera, cornea, camara, iris, pupila, cristalino, vitreo, nervioop, retinapp, retinape,retinamac, schirmer, but from observaciones where idojo = 1 and idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				obs.append(aux)
				consulta = "SELECT medicamento1, descripcion1, medicamento2, descripcion2 from recetagotero where idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				gotas = cursor.fetchone()
				consulta = "select lugar, descripcion from recetareferencia where idconsulta = %s"
				cursor.execute(consulta,idconsulta)
				referencia = cursor.fetchone()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('ver.html', title='Historico', logeado=logeado, estudiante=estudiante, paciente = paciente, 
		dataconsulta=dataconsulta, anios=anios, cincos=cincos, meses=meses, antecedentes = antecedentes, av=av, ra=ra, vc=vc, roa=roa, ror=ror, 
		rs=rs, rf=rf, mo=mo, obs=obs, usolen=usolen, numantmed=numantmed, numantqui=numantqui, antmed=antmed, antqui=antqui, enfermedades=enfermedades,
		nervos=nervos, mms=mms, numeros=numeros, relva=relva, tipolen=tipolen, materiallen=materiallen, filtrolen=filtrolen, colorlen=colorlen,
		lenterecomendado=lenterecomendado, dataojo=dataojo, dataametropia=dataametropia, gotas=gotas, referencia=referencia, lentedetalladolen=lentedetalladolen)

@app.route("/crearusuario", methods=['GET', 'POST'])
def crearusuario():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0

	if request.method == 'POST':
		nombre = request.form["nombre"]
		apellido = request.form["apellido"]
		user = request.form["user"]
		pwd = request.form["pwd"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO user(nombre, apellido, user, pwd) values (%s, %s, %s, MD5(%s));"
					cursor.execute(consulta, (nombre, apellido, user, pwd))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('home'))
	return render_template('crearusuario.html', title='Nuevo Usuario', logeado=logeado)

@app.route("/recetalentespdf/<idconsulta>", methods=['GET', 'POST'])
def recetalentespdf(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	rf = []
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT esfera1, cilindro1, eje1, prisma1, avcc1 from reffin where idconsulta = %s and idojo = 2;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rf.append(aux)
				consulta = "SELECT esfera1, cilindro1, eje1, prisma1, avcc1 from reffin where idconsulta = %s and idojo = 1;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchone()
				rf.append(aux)
				consulta = "SELECT p.nombre1, p.nombre2, p.apellido1, p.apellido2, DATE_FORMAT(c.fecha,'%d/%m/%Y'), u.uso, DATE_FORMAT(c.proximacita,'%d/%m/%Y'), c.dnp, c.add11, c.add22, c.add33, o.nombre, o.apellido from paciente p inner join consulta c on p.idpaciente = c.idpaciente inner join usolen u on u.idusolen = c.idusolen inner join user o ON o.iduser = c.iduser where idconsulta = " + str(idconsulta) + ";"
				print(consulta)
				cursor.execute(consulta)
				dataconsulta = cursor.fetchall()
				consulta = "SELECT t.tipo, m.material, f.filtro, c.color, d.lentedetallado from lenterecomendado l inner join tipolen t on t.idtipolen=l.tipo inner join materiallen m on m.idmateriallen=l.material inner join filtrolen f on f.idfiltrolen=l.filtro inner join colorlen c on c.idcolorlen=l.color inner join lentedetallado d on d.idlentedetallado = l.lentedetallado where l.idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				lenterecomendado = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	rendered = render_template('recetalentespdf.html', title="Receta lente", dataconsulta=dataconsulta, rf = rf, lenterecomendado=lenterecomendado)
	options = {'enable-local-file-access': None, 'page-size': 'A5', 'orientation': 'landscape', 'zoom': '0.6', 'margin-top': '10mm'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=reportediario.pdf'
	print(response)
	return response

@app.route("/recetacontactopdf/<idconsulta>", methods=['GET', 'POST'])
def recetacontactopdf(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	lencons = []
	existe = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT DATE_FORMAT(fechacaducidad,'%d/%m/%Y'), poder, cb, dia, cil, eje, agregar, color, tipo from recetacontacto where idconsulta = " + str(idconsulta) + " and idojo = 2;"
				cursor.execute(consulta)
				aux = cursor.fetchall()
				if len(aux) < 1:
					lencons.append([0,0,0,0,0,0,0,0,0])
				else:
					lencons.append(aux[0])
					existe = existe + 1
				consulta = "SELECT DATE_FORMAT(fechacaducidad,'%d/%m/%Y'), poder, cb, dia, cil, eje, agregar, color, tipo from recetacontacto where idconsulta = " + str(idconsulta) + " and idojo = 1;"
				cursor.execute(consulta)
				aux = cursor.fetchall()
				if len(aux) < 1:
					lencons.append([0,0,0,0,0,0,0,0,0])
				else:
					lencons.append(aux[0])
					existe = existe + 1
				consulta = "SELECT p.nombre1, p.nombre2, p.apellido1, p.apellido2, DATE_FORMAT(c.fecha,'%d/%m/%Y'), u.uso, DATE_FORMAT(c.proximacita,'%d/%m/%Y'), c.dnp, c.add11, c.add22, c.add33, o.nombre, o.apellido from paciente p inner join consulta c on p.idpaciente = c.idpaciente inner join usolen u on u.idusolen = c.idusolen inner join user o ON o.iduser = c.iduser where idconsulta = " + str(idconsulta) + ";"
				cursor.execute(consulta)
				dataconsulta = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	rendered = render_template('recetacontactopdf.html', title="Receta contacto", dataconsulta=dataconsulta, lencons=lencons)
	options = {"enable-local-file-access": "", "page-size": "A5", "orientation": "landscape", "zoom": "0.6", "margin-top": "10mm"}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=reportediario.pdf'
	print(response)
	return response

@app.route("/recetagotaspdf/<idconsulta>", methods=['GET', 'POST'])
def recetagotaspdf(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	lencons = []
	existe = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT medicamento1, descripcion1, medicamento2, descripcion2 from recetagotero where idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				aux = cursor.fetchall()
				if len(aux) < 1:
					datagotero = [0,0,0,0]
				else:
					datagotero = aux[0]
				consulta = "SELECT p.nombre1, p.nombre2, p.apellido1, p.apellido2, DATE_FORMAT(c.fecha,'%d/%m/%Y'), u.uso, DATE_FORMAT(c.proximacita,'%d/%m/%Y'), c.dnp, c.add11, c.add22, c.add33, o.nombre, o.apellido from paciente p inner join consulta c on p.idpaciente = c.idpaciente inner join usolen u on u.idusolen = c.idusolen inner join user o ON o.iduser = c.iduser where idconsulta = " + str(idconsulta) + ";"
				cursor.execute(consulta)
				dataconsulta = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	rendered = render_template('recetagotaspdf.html', title="Receta gotas", dataconsulta=dataconsulta, datagotero=datagotero)
	options = {'enable-local-file-access': None, 'page-size': 'A5', 'orientation': 'landscape', 'zoom': '0.6', 'margin-top': '10mm'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=reportediario.pdf'
	print(response)
	return response

@app.route("/recetarefpdf/<idconsulta>", methods=['GET', 'POST'])
def recetarefpdf(idconsulta):
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='opticadb')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT lugar, descripcion from recetareferencia  where idconsulta = %s;"
				cursor.execute(consulta, idconsulta)
				recetaref = cursor.fetchall()
				consulta = "SELECT p.nombre1, p.nombre2, p.apellido1, p.apellido2, DATE_FORMAT(c.fecha,'%d/%m/%Y'), u.uso, DATE_FORMAT(c.proximacita,'%d/%m/%Y'), c.dnp, c.add11, c.add22, c.add33, o.nombre, o.apellido from paciente p inner join consulta c on p.idpaciente = c.idpaciente inner join usolen u on u.idusolen = c.idusolen inner join user o ON o.iduser = c.iduser where idconsulta = " + str(idconsulta) + ";"
				print(consulta)
				cursor.execute(consulta)
				dataconsulta = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	rendered = render_template('recetarefpdf.html', title="Receta Referencia", dataconsulta=dataconsulta, recetaref=recetaref)
	options = {'enable-local-file-access': None, 'page-size': 'A5', 'orientation': 'landscape', 'zoom': '0.6', 'margin-top': '10mm'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=reportediario.pdf'
	print(response)
	return response

@app.route("/recetalentesblancopdf", methods=['GET', 'POST'])
def recetalentesblancopdf():
	try:
		logeado = session['logeado1']
	except:
		logeado = 0
	x = datetime.datetime.now()
	fecha = x.strftime("%d/%m/%Y")
	rendered = render_template('recetalentesblancopdf.html', title="Receta lente", fecha = fecha)
	options = {'enable-local-file-access': None, 'page-size': 'A5', 'orientation': 'landscape', 'zoom': '0.6', 'margin-top': '10mm'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=reportediario.pdf'
	print(response)
	return response

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5001)