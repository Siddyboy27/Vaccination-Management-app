from flask import Flask,render_template,flash,redirect,url_for,session,logging,request 
from flask_mail import Message
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,IntegerField,validators
from passlib.hash import sha256_crypt
from functools import wraps
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
import os
import random
import requests
import youtube_dl
import datetime
from datetime import date

app=Flask(__name__)
app.secret_key='password123'
name1=""
usernname1=""
email1=""
password1=""
username2=""

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='password123'
app.config['MYSQL_DB']='vaccine_tracker'
app.config['MYSQL_CURSORCLASS']='DictCursor'

app.config.from_pyfile('config.cfg')


s=URLSafeTimedSerializer('password123')

mysql=MySQL(app)


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/Citizen')
def Citizen():
	return render_template('Citizen.html')


class RegisterForm(Form):
	name=StringField('Name',[validators.Length(min=1,max=50)])
	Passport_No=StringField('Passport Number',[validators.Length(min=4,max=10)])
	
	password=PasswordField('Password',[validators.DataRequired(),validators.EqualTo('confirm',message='Password do not match')])
	confirm=PasswordField('Confirm your Password')

class SongUpload(Form):
	title=StringField('Title',[validators.Length(min=1,max=50)])
	artist=StringField('Artist',[validators.Length(min=4,max=25)])
	vid_id=StringField('Video ID',[validators.Length(min=6,max=1000)])
	album=StringField('Album (Type "-" if no album is there)',[validators.Length(min=1,max=75)])
	band=StringField('Band (Type "-" if no band is there)',[validators.Length(min=1,max=75)])

class Artist(Form):
	Name=StringField('Name',[validators.Length(min=1,max=50)])
	Role=StringField('Role',[validators.Length(min=4,max=25)])
	Band=StringField('Band (Type "-" if no band is there)',[validators.Length(min=0,max=50)])

class Album(Form):
	name=StringField('Name',[validators.Length(min=1,max=50)])
	year=StringField('Year',[validators.Length(min=4,max=25)])
	artist=StringField('Artists',[validators.Length(min=5,max=50)])
	band=StringField('Band (Type "-" if no band is there)',[validators.Length(min=1,max=50)])

class Band(Form):
	name=StringField('Name',[validators.Length(min=0,max=50)])
	nom=IntegerField('Number of Members')

class make_playlist(Form):
	title=StringField('Name',[validators.Length(min=1,max=25)])


	







#staff login
@app.route('/stafflogin',methods=['GET','POST'])
def Stafflogin():
	if request.method=='POST':
		D_id=request.form['D_id']

		P_id=request.form['P_id']

		cur=mysql.connection.cursor()

		result=cur.execute("SELECT * FROM doctors WHERE Passport_id= %s",[P_id])

		if result==1:
			data=cur.fetchone()
			password=data['Doctor_ID']

			if D_id==password:
				session['logged_in']=True
				session['username']=data['Name']
				session['id']=data['Doctor_ID']

				flash('Login successful','success')
				return redirect(url_for('Staffdashboard'))
			else:
				error='Wrong password'
			return render_template('stafflogin.html',error=error)
			cur.close()
		else:
			error='Not a staff'
			return render_template('stafflogin.html',error=error)

	return render_template('stafflogin.html')

#to prevent using of app without login
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorised! Please login','danger')
			return redirect(url_for('login'))
	return wrap


@app.route('/staffdashboard')
@is_logged_in
def Staffdashboard():
	cur=mysql.connection.cursor()
	cur.execute("SELECT * FROM Vaccine")
	data=cur.fetchall()
	return render_template('staffdashboard.html',data=data)
	cur.close()

@app.route('/ConfirmVaccine',methods=['GET','POST'])
@is_logged_in
def ConfirmVaccine():
	DATE=date.today()
	D=DATE.strftime("%y-%m-%d")
	msg=DATE.strftime("%d-%m-%y")
	cur=mysql.connection.cursor()
	
	cur.execute("SELECT*FROM Appointments WHERE (Dose_1=%s AND dose=0)OR Dose_2=%s",(D,D))
	data=cur.fetchall()
	if(len(data)==0):
		msg="No appointments for today, "+msg
		flash(msg,"danger")
		return redirect(url_for('Staffdashboard'))
	if request.method=='POST':
		P_id=request.form['Key']
		cur.execute("UPDATE Appointments SET dose=dose+1 WHERE P_id=%s",[P_id])

		mysql.connection.commit()
		cur.execute("SELECT*FROM Appointments WHERE P_id=%s",[P_id])
		data=cur.fetchone()
		n=data['Vaccine']
		cur.execute("UPDATE users SET Vaccine_id=%s WHERE Passport_id=%s",(n,P_id))
		
		if data['dose']==1:
			date2=data['Dose_1']+datetime.timedelta(days=28)
			cur.execute("UPDATE Appointments SET Dose_2=%s WHERE P_id=%s",(date2,P_id))
			cur.execute("UPDATE users SET doses=1 WHERE Passport_id=%s",[P_id])
			cur.execute("UPDATE users SET DO2=%s WHERE Passport_id=%s",(date2,P_id))
			mysql.connection.commit()
		elif data['dose']==2:
			cur.execute("UPDATE users SET doses=2 WHERE Passport_id=%s",[P_id])
			cur.execute("DELETE FROM Appointments WHERE P_id=%s",[P_id])
			mysql.connection.commit()

		
		n=data['Vaccine']
		cur.execute("UPDATE  vaccine SET Vials=Vials-1 WHERE Vaccine_id=%s",[n])

		mysql.connection.commit()
		flash("Approved","success")
		return redirect(url_for("ConfirmVaccine"))

			
		
	return render_template('ConfirmVaccine.html',data=data)


@app.route('/Order',methods=['GET','POST'])
def Order():
	if request.method=='POST':
		Vaccine=request.form['Vaccine']
		print(Vaccine)
		dosage=request.form['dosage']
		print(dosage)
		cur=mysql.connection.cursor()

		cur.execute("INSERT INTO Orders(dosage,Vaccine,Doctor_id) VALUES(%s,%s,%s)",(dosage,Vaccine,session['id']))
		mysql.connection.commit()
		flash("Succesfully Requested for Vaccination","success")
		return render_template('Order.html')
		
	return render_template('Order.html')

@app.route('/OrderConfirmation',methods=['POST','GET'])
def OrderConfirmation():
	cur=mysql.connection.cursor()

	cur.execute("SELECT*FROM Orders WHERE Doctor_id=%s",[session['id']])
	data=cur.fetchall()
	if(len(data)==0):
		flash("No orders made","danger")
		return redirect(url_for('Staffdashboard'))
	if(request.method=='POST'):
		key=request.form['Key']
		print(key)
		cur.execute("SELECT * FROM Orders WHERE order_id=%s",[key])
		data2=cur.fetchone()
		cur.execute("UPDATE Vaccine SET Vials=Vials+%s WHERE Vaccine_name=%s",(data2['dosage'],data2['Vaccine']))
		cur.execute("DELETE FROM Orders WHERE order_id=%s",[key])
		mysql.connection.commit()
		flash("Successfully recieved vials",'success')
		return redirect(url_for('OrderConfirmation'))
	return render_template("OrderConfirmation.html",data=data)






#ALL CITIZENS BELOW


#registeration
@app.route('/Register',methods=['GET','POST'])
def register():
	form =RegisterForm(request.form)
	if request.method=='POST' and form.validate():
		name=form.name.data
		
		P_id=form.Passport_No.data
		password=sha256_crypt.encrypt(str(form.password.data))
		global P1,name1,password1
		P1=P_id
		name1=name
		
		password1=password


		cur=mysql.connection.cursor()
		result=cur.execute("SELECT * FROM users WHERE Passport_id= %s",[P_id])
		
		if result>0:
			flash('User already exists','danger')
			return redirect(url_for('login'))
		else:
			cur.execute("INSERT INTO users(name,Passport_id,password) VALUES(%s,%s,%s)",(name1,P1,password1))
			mysql.connection.commit()
			cur.close()
			flash('Successfully verified','success')
			return redirect(url_for('login'))

	return render_template('register.html',form=form)

#login
@app.route('/login',methods=['GET','POST'])
def login():
	if request.method=='POST':
		P=request.form['P_id']

		password_candidate=request.form['Password']

		cur=mysql.connection.cursor()

		result=cur.execute("SELECT * FROM users WHERE Passport_id= %s",[P])

		if result>0:
			data=cur.fetchone()
			password=data['password']

			if sha256_crypt.verify(password_candidate,password):
				session['logged_in']=True
				session['username']=data['name']
				session['id']=data['Passport_id']

				flash('login successful','success')
				return redirect(url_for('CitizenDashboard'))
			else:
				error='wrong password'
				return render_template('login.html',error=error)
			cur.close()
		else:
			flash('User not registered','danger')
			return redirect(url_for('register'))
	return render_template('login.html')




@app.route('/citizendashboard')
@is_logged_in
def CitizenDashboard():
	cur=mysql.connection.cursor()
	ID=session['id']

	cur.execute("SELECT*FROM users WHERE Passport_id=%s",[ID])
	data=cur.fetchone()

	cur.execute("SELECT*FROM Vaccine where Vaccine_id=%s",[data['Vaccine_id']]);
	Vac=cur.fetchone();

	if(data['doses']==0):
		Note='NOT VACCINATED'
		Col='#DA0606'
		BG="background-color:#DA0606 ;"
	elif (data['doses']==1):
		Note='1st DOSE TAKEN'
		Col='#FFC300'
		BG="background-color:#FFC300;"
	elif(data['doses']==2):
		Note='VACCINATED'
		Col='#23D825'
		BG="background-color:#23D825;"

	return render_template('CitizenDashboard.html',Note=Note,Col=Col,BG=BG,data=data,Vac=Vac)


#Appointment
@app.route('/VaccineRegisteration',methods=['GET','POST'])
@is_logged_in
def VaccineRegisteration():
	if request.method=='POST':
		Vaccines=[1,2,3,4]
		D=request.form['DATE']
		cur=mysql.connection.cursor()
		result=cur.execute("SELECT *FROM Appointments WHERE P_id=%s",[session['id']])
		if(result>0):
			flash("Already registered","danger")
			return redirect (url_for('CitizenDashboard'))
		else:
			cur.execute("INSERT INTO Appointments (P_id,Dose_1,Vaccine) VALUES(%s,%s,%s)",(session['id'],D,random.choice(Vaccines)))
			cur.execute("UPDATE users SET DO1=%s WHERE Passport_id=%s",(D,session['id']))
			mysql.connection.commit()
			flash("Registered","success")
			return redirect (url_for('CitizenDashboard'))
	return render_template('VaccineRegisteration.html')


#logout
@app.route('/logout')
def logout():
	session.clear()
	flash('you are now logged out','success')
	return redirect(url_for('index'))


























































































@app.route('/AddArtist', methods = ['GET','POST'])
@is_logged_in
def AddArtist():
	form1 =Artist(request.form)
	if request.method=='POST' and form1.validate():
		Name=form1.Name.data
		Role=form1.Role.data
		Band=form1.Band.data
		
		cur=mysql.connection.cursor()
		result=cur.execute("SELECT * FROM artists WHERE A_name=%s",[Name])
		if result>0:
			error='Artist already exists'
			return render_template('add_artists.html',form=form1,error=error)
		
		else:
			name1=Name
			role1=Role
			cur.execute("SELECT * FROM band WHERE B_name=%s",[Band])
			data=cur.fetchone()
			band1=data['band_id']
			cur.execute("INSERT INTO artists(A_name,A_role,band_id) VALUES(%s,%s,%s)",(name1,role1,band1))
			mysql.connection.commit()
			cur.close()
			flash('Successfully added','success')
			return redirect(url_for('dashboard'))

	return render_template('add_artists.html',form=form1)

@app.route('/AddBand',methods=['GET','POST'])
@is_logged_in
def AddBand():
	form1 =Band(request.form)
	if request.method=='POST' and form1.validate():
		name=form1.name.data
		nom=form1.nom.data
		
		
		cur=mysql.connection.cursor()
		result=cur.execute("SELECT * FROM band WHERE B_name=%s",[name])
		if result>0:
			error='Band already exists'
			return render_template('add_band.html',form=form1,error=error)
		
		else:
			name1=name
			nom1=nom
			
			cur.execute("INSERT INTO band(B_name,NOM) VALUES(%s,%s)",(name1,nom1))
			mysql.connection.commit()
			cur.close()
			flash('Successfully added','success')
			return redirect(url_for('dashboard'))

	return render_template('add_band.html',form=form1)


@app.route('/AddAlbum',methods=['GET','POST'])
@is_logged_in
def AddAlbum():
	form1 =Album(request.form)
	if request.method=='POST' and form1.validate():
		name=form1.name.data
		year=form1.year.data
		artist=form1.artist.data
		band=form1.band.data
		
		cur=mysql.connection.cursor()
		result=cur.execute("SELECT * FROM album WHERE album_name=%s",[name])
		if result>0:
			error='Album already exists'
			return render_template('add_album.html',form=form1,error=error)
		
		else:
			name1=name
			year1=year
			cur.execute("SELECT band_id FROM band WHERE B_name=%s",[band])
			data=cur.fetchone()
			band1=data['band_id']
			cur.execute("SELECT artist_id FROM artists WHERE A_name=%s",[artist])
			data=cur.fetchone()
			artist1=data['artist_id']
			cur.execute("INSERT INTO album(album_name,Release_year,artist_id,band_id) VALUES(%s,%s,%s,%s)",(name1,year1,artist1,band1))
			mysql.connection.commit()
			cur.close()
			flash('Successfully added','success')
			return redirect(url_for('dashboard'))

	return render_template('add_album.html',form=form1)

@app.route('/play/<vid_id>')
@is_logged_in
def Play(vid_id):
	cur=mysql.connection.cursor()
	cur.execute("SELECT *FROM tracks WHERE Vid_id=%s",[vid_id] )
	data=cur.fetchone()
	Name=data['title']
	cur.execute("SELECT *FROM artists WHERE artist_id=%s",[data['artist_id']])
	data1=cur.fetchone()
	Art=data1['A_name']
	cur.execute("SELECT *FROM band WHERE band_id=%s",[data['band_id']])
	data2=cur.fetchone()
	band=data2['B_name']

	
	return render_template("Player.html",Name=Name,Art=Art,band=band)


@app.route('/Search')
@is_logged_in

def Search():
	return render_template("search.html")


@app.route('/SearchSong',methods=['GET','POST'])
@is_logged_in
def SearchSong():
	if request.method=="POST":
		song=request.form['song']
		song='%'+song+'%'
		cur=mysql.connection.cursor()
		cur.execute("SELECT * FROM tracks WHERE title LIKE %s ",[song])
		data=cur.fetchall()
		if(len(data)==0):
			flash("No Song as such found",'danger')
		else:
			return render_template('SearchSong.html',data=data)
	return render_template('SearchSong.html')


@app.route('/SearchBand',methods=['GET','POST'])
@is_logged_in
def SearchBand():
	if request.method=="POST":
		band=request.form['band']
		band='%'+band+'%'
		cur=mysql.connection.cursor()
		cur.execute("SELECT * FROM band WHERE B_name LIKE %s ",[band])
		data=cur.fetchall()
		if(len(data)==0):
			flash("No Band as such found",'danger')
		else:
			return render_template('SearchBand.html',data=data)
	return render_template('SearchBand.html')


@app.route('/SearchArtist',methods=['GET','POST'])
@is_logged_in
def SearchArtist():
	if request.method=="POST":
		artist=request.form['artist']
		artist='%'+artist+'%'
		cur=mysql.connection.cursor()
		cur.execute("SELECT * FROM artists WHERE A_name LIKE %s ",[artist])
		data=cur.fetchall()
		if(len(data)==0):
			flash("No artist as such found",'danger')
		else:
			return render_template('SearchArtist.html',data=data)
	return render_template('SearchArtist.html')


@app.route('/SearchAlbum',methods=['GET','POST'])
@is_logged_in
def SearchAlbum():
	if request.method=="POST":
		album=request.form['album']
		album='%'+album+'%'
		cur=mysql.connection.cursor()
		cur.execute("SELECT * FROM album WHERE Album_name LIKE %s ",[album])
		data=cur.fetchall()
		if(len(data)==0):
			flash("No album as such found",'danger')
		else:
			return render_template('SearchAlbum.html',data=data)
	return render_template('SearchAlbum.html')


@app.route('/playlists',methods=['GET','POSt'])
@is_logged_in
def playlist():
	cur=mysql.connection.cursor()
	username=session['username']
	cur.execute("SELECT * FROM users WHERE username = %s",[username])
	result=cur.fetchone()
	idd=result['id']
	cur.execute("SELECT*FROM playlist WHERE user_id=%s",[idd])
	result=cur.fetchall()
	if len(result)==0:
		msg="No playlist"
	else:
		msg="Your playlists"
	mysql.connection.commit()
	return render_template("playlist.html",msg1=msg,result=result)





@app.route('/create_playlist',methods=['GET','POST'])
@is_logged_in
def createplaylist():
	form=make_playlist(request.form)
	if request.method=='POST' and form.validate():
		title=form.title.data

		cur=mysql.connection.cursor()

		
		username=session['username']

		row=cur.execute("SELECT * FROM users WHERE username = %s",[username])
		result=cur.fetchone()
		idd=result['id']
		cur.execute("INSERT INTO playlist(title,user_id) VALUES (%s,%s)",([title],idd))
		mysql.connection.commit()
		cur.close()

		flash("Succesfully created",'success')

		return redirect(url_for('dashboard'))
	return render_template('add_playlist.html',form=form)

@app.route('/play_list/<play_id>',methods=['GET','POST'])
@is_logged_in
def play_list(play_id):
	cur=mysql.connection.cursor()
	username=session['username']
	cur.execute("SELECT * FROM users WHERE username = %s",[username])
	result=cur.fetchone()
	idd=result['id']
	cur.execute("SELECT*FROM playlist WHERE playlist_id=%s",[play_id])
	Name=cur.fetchone()
	Name=Name['title']
	cur.execute("SELECT *FROM tracks WHERE song_id IN(SELECT song_id FROM track_listing WHERE playlist_id=%s)",[play_id])
	data=cur.fetchall()
	P=play_id
	return render_template("play_list.html",Name=Name,play_id=P,data=data)

@app.route('/addplay/<play_id>',methods=['GET','POST'])
@is_logged_in
def add_play_list(play_id):
	P=play_id
	if request.method=="POST":
		song=request.form['song']
		song='%'+song+'%'
		cur=mysql.connection.cursor()
		cur.execute("SELECT * FROM tracks WHERE title LIKE %s ",[song])
		S=cur.fetchall()
		if(len(S)==0):
			flash("No Song as such found",'danger')
		return render_template("add_play_list.html",data=S,play_id=P)
	return render_template("add_play_list.html")

@app.route('/add/<play_id>/<Sid>',methods=['GET','POST'])
@is_logged_in
def add(play_id,Sid):
	cur=mysql.connection.cursor()
	check=cur.execute("SELECT *FROM track_listing WHERE playlist_id=%s AND song_id=%s",(play_id,Sid))
	if check==1:
		flash("Song already in playlist",'danger')
	else:
		cur.execute("INSERT into track_listing (playlist_id,song_id) VALUES(%s,%s)",(play_id,Sid))
		flash("Song successfully added to playlist",'success')
	P=play_id
	mysql.connection.commit()
	return redirect(url_for('add_play_list',play_id=P))
	return render_template('add_play_list.html')


if __name__=='__main__':
	
	app.run(debug=True)