from flask import render_template , Flask , request , session , redirect , url_for , send_from_directory
import os
from sqlalchemy import desc , asc
basedir = os.path.abspath(os.path.dirname(__file__))
from werkzeug.security import generate_password_hash as enc
from werkzeug.security import check_password_hash as dec
from werkzeug.utils import secure_filename
from hashlib import sha1
from flask_sqlalchemy import SQLAlchemy
import datetime
import secrets
import string
import random


app = Flask("__main__" , template_folder=basedir+"/templates")

app.config["UPLOAD_FOLDER"] = basedir + "/static/media"
app.config["MAX_CONTENT_PATH"] = 4*1024*1024
def allowed(filename):
	#print(filename)
	return filename.split(".")[len(filename.split("."))-1] in ['jpg','jpeg','png','webm' , 'gif'] , filename.split(".")[len(filename.split("."))-1]

app.config['SECRET_KEY'] = 'thytyhjeyt'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)


def gen(N):
	return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(N))

class Thread(db.Model):
	uni = db.Column(db.String(100) , primary_key = True)
	board = db.Column(db.String(50))
	bump = db.Column(db.Integer , default = 0)
	id = db.Column(db.Integer) #number, not the cookie id
	name = db.Column(db.String(50))
	img_name = db.Column(db.String(200) , default="")
	img_num = db.Column(db.Integer , default = 0)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	bumptime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	body = db.Column(db.String(500))
	img_ext = db.Column(db.String(10))
	password = db.Column(db.String(500))
	pinned = db.Column(db.Integer)  #is it pinned or not?
	subject = db.Column(db.String(100))

class Post(db.Model):
	uni = db.Column(db.String(100), primary_key=True)
	id = db.Column(db.Integer) #number, not the cookie id
	name = db.Column(db.String(50))
	img_name = db.Column(db.String(200) , default="")
	img_num = db.Column(db.Integer , default = 0)
	time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	body = db.Column(db.String(500))
	thread_id = db.Column(db.Integer)
	img_ext = db.Column(db.String(10))
	password = db.Column(db.String(500))
	options = db.Column(db.String(50)) #noko sage
	board = db.Column(db.String(50))
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Boards(db.Model):
	name = db.Column(db.String(50), primary_key=True)
	desc = db.Column(db.String(500))
	last_id = db.Column(db.Integer , default = 0) #to generate new id
	max_posts_displayed = db.Column(db.Integer , default = 2) #maximum number of posts displayed under a thread when browsing /board
	bump_limit = db.Column(db.Integer , default = 500)
	theme = db.Column(db.String(100) , default = "futaba.css")

class User(db.Model):
	username = db.Column(db.String(50), primary_key=True)
	password = db.Column(db.String(500))
	email = db.Column(db.String(500))
	#rank 0 = janny
	#rank 1 = mod
	#rank 2 = admin
	rank = db.Column(db.Integer, default=0)
	board_name = db.Column(db.String(50))

class Media(db.Model):
	board = db.Column(db.String(50), primary_key=True)
	jpg = db.Column(db.Integer, default=0)
	jpeg = db.Column(db.Integer, default=0)
	png = db.Column(db.Integer, default=0)
	gif = db.Column(db.Integer, default=0)
	webm = db.Column(db.Integer, default=0)

class refer(db.Model):
	uni = db.Column(db.String(500), primary_key=True)
	board = db.Column(db.String(50))
	replied_to = db.Column(db.Integer)
	own_id = db.Column(db.Integer)

def tripcodegen(thing):
	return sha1(thing.encode("utf-8")).hexdigest()[:8]
#Create the schema
def trip(name):
	li = name.split("#")
	try:
		if User.query.filter_by(username=li[0].strip()).all()[0]:
			u = User.query.filter_by(username=li[0].strip()).all()[0]
			if dec(u.password ,li[1].strip()) and session["username"]==u.username:
				if u.rank == 1:
					if len(li) == 2:
						return li[0].strip()+" # "+"moderator"
					else:
						return li[2].strip()+" # "+"moderator"
				if u.rank ==2:
					if len(li) == 2:
						return li[0].strip()+" # "+"admin"
					else:
						return li[2].strip()+" # "+"admin"
			else:
				return li[0].strip()+" !"+tripcodegen(li[0].strip()+li[1].strip())
	except:
		if len(li)==1:
			return name
		else:
			return li[0].strip()+" !"+tripcodegen(li[0].strip()+li[1].strip())


def green(text , board):
	i = 0
	green_text=False
	link_=False
	link=""
	res=""

	while i<len(text):
		if text[i]==">":
			if i==len(text)-1:
				if green_text:
					res+="&gt;"+"</font>"
				else:
					res+='<font color="green">'+"&gt;"+"</font>"
				pass


			try:

				if text[i-1]==">" and  not green_text:
					link_=True
					#link+=text[i]

				elif text[i+1]!=">" and not green_text and text[i-1]=="\n":
					green_text=True
					res+='<font color="green">'+"&gt;"

				elif text[i+1]!=">" and not green_text and text[i-1]=="\n":
					green_text=True
					res+='<font color="green">'+"&gt;"
				elif text[i+1]!=">" and not green_text:
					green_text=True
					res+="&gt;"

				else:
					if text[i+1]!=">" and i==len(text)-1:
						res+="&gt;"
			except:
				if i!=len(text)-1:
					res+="&gt;"

		elif text[i]==" ":
			if link_:
				link_=False
				#print("LINK" , link)
				try:
					#res+="<a href=\""+url_maker(link , board)+"\">"+"&gt;&gt;"+link+"</a>&nbsp;"
					res+="<a href=\""+url_maker(link , board)+"\">"+"&gt;&gt;"+link+"</a> "
				except:
					pass
				link=""
			else:
				#res+="&nbsp;"
				res+=" "
		elif text[i]=="\n":
			if link_:
				link_=False
				#print("LINK" , link)
				try:
					res+="<a href=\""+url_maker(link , board)+"\">"+"&gt;&gt;"+link+"</a></br>"
				except:
					pass
				link=""
			elif green_text:
				green_text=False
				res+="</br></font>"
			else:
				res+="</br>"
		elif link_:
			link+=text[i]
			if i == len(text)-1:
				res+="<a href=\""+url_maker(link , board)+"\">"+"&gt;&gt;"+link+"</a></br>"
				link=""
				link_=False
		elif text[i] == "<":
			res += "&lt;"
		elif text[i] == "\"":
			res+="&quot;"
		elif text[i] == "\'":
			res+="&apos;"
		elif text[i] == "&":
			res+="&amp;"
		elif i == len(text)-1:

			if green_text:
				green_text=False
				res+=text[i]+"</font>"

			elif link_:
				link_=False
				res+="<a href=\""+url_maker(link+text[i] , board)+"\">"+"&gt;&gt;"+link+text[i]+"&nbsp;</a>"
			else:
				res+=text[i]
		else:
			res+=text[i]

		i+=1
	#print(res)
	return res.strip()




def reply_finder(text , id , board):
	i = 0
	link=""
	link_=0
	links=[]
	while i<len(text):
		if text[i]==">":
			if not link_:
				try:
					if text[i+1]==">":
						link_=1
				except:
					pass
		elif text[i]==" " or i == len(text)-1 or text[i]=="\n":
			if link_:
				link_=0
				links.append(link+text[i])
				link=""
		elif link_:
			link+=text[i]

		i+=1
	#print("LINKS" , links)
	for stuff in links:
		#db.session.add(refer(uni=board+" "+str(id)+" "+stuff.strip() , board = board , replied_to = int(stuff) , own_id = id))
		if not refer.query.filter_by(uni=board+" "+str(id)+" "+stuff.strip()).filter_by(board=board).all():
			db.session.add(refer(uni=board+" "+str(id)+" "+stuff.strip() , board = board , replied_to = int(stuff) , own_id = id))
			db.session.commit()
		else:
			pass

def url_maker(number , board):
	number=str(number).strip()
	if number.isdigit():
		number=int(number)
		if Thread.query.filter_by(board=board , id=number).all():
			#print(url_for("board_thread" ,board=board , thread_id=number))
			return url_for("board_thread" ,board=board , thread_id=number)
		elif Post.query.filter_by(board=board , id=number).all():
			a = Post.query.filter_by(board=board , id=number).all()[0]
			#print(url_for("board_thread" ,board=board , thread_id = a.thread_id , _anchor = a.id))
			return url_for("board_thread" ,board=board , thread_id = a.thread_id , _anchor = a.id)
		else:
			return ""
	else:
		b = number.split("/")
		while "" in b:
			b.remove("")
		if len(b)>=2:
			return url_maker(b[1],b[0])
		else:
			return number
		#return number
def random_banner():
	p=[]
	for i in os.listdir(basedir+"/static/banners"):
		if not i.startswith("."):
			p.append(i)
	return random.choice(p)

def log(board , post , ip):
	if os.path.exists("log.txt"):
		a = open(basedir+"/log.txt", "a")
	else:
		a = open(basedir+"/log.txt" , "w")
	a.write(str(board)+" " + str(post) +" "+ str(ip) +"\n")
	a.close()

def is_banned(ip):
	a = open(basedir+"/ban.txt" , "r")
	b = a.read()
	a.close()
	b = b.split("\n")
	ips=[]
	for i in b:
		if i!="":
			ips.append(i)
	for i in ips:
		if ip.startswith(i):
			return 1
	return 0

def boards_list():
	board_list = []
	for b in Boards.query.all():
		board_list.append("<a href="+url_for("board_home",board=b.name)+">" + b.name + "</a>")
	string = "[ "
	for b in board_list:
		string+=b+" / "
	if string!="[ ":
		string = string[0:len(string)-2]
	string+="]"
	return string

def themes():
	theme = []
	for i in os.listdir(basedir+"/static/scripts"):
		if i.endswith(".css"):
			theme.append(i)
	return theme

#db.create_all()


@app.route("/")
def index():
	if "name" not in session:
		session["name"]="anon"
	board_list = []
	for b in Boards.query.all():
		board_list.append("<a href="+url_for("board_home",board=b.name)+">" + b.name + "</a>")
	string = "[ "
	for b in board_list:
		string+=b+" / "
	if string!="[ ":
		string = string[0:len(string)-2]
	string+="]"
	return render_template("main.html",boards=string)


@app.route("/rules")
def rules():
	if "name" not in session:
		session["name"]="anon"
	return render_template("rules.html")

@app.route("/login", methods=["GET" , "POST"])
@app.route("/login/", methods=["GET" , "POST"])
def login():
	if "name" not in session:
		session["name"]="anon"
	if request.method == "POST":
		u = User.query.filter_by(username = request.form["username"]).all()[0]
		if dec(u.password , request.form["password"]):
			session["username"] = u.username
			session["rank"] = u.rank
			#print(session["username"] , session["rank"])
	if "username" in session:
		return redirect(url_for("index"))
	return render_template("login.html")

@app.route("/logout")
@app.route("/logout/")
def logout():
	if "name" not in session:
		session["name"]="anon"
	if "username" in session:
		session.pop("username")
		session.pop("rank")

@app.route("/media/<path:p>")
@app.route("/media/<path:p>/")
def serve(p):
	return send_from_directory(app.config["UPLOAD_FOLDER"] , p)

@app.route("/_banner/<path:p>",methods=["GET" , "POST"])
@app.route("/_banner/<path:p>/",methods=["GET" , "POST"])
def serve_banner(p):
	#p=[]
	#print("22")
	#for i in os.listdir("static/banners"):
	#	if not i.startswith("."):
	#		p.append(i)
	#a=random.choice(p)
	#print(a)
	return send_from_directory(basedir + "/static/banners", p)
	#return "yay"

@app.route("/_scripts/<path:p>")
@app.route("/_scripts/<path:p>/")
def serve_scripts(p):
	return send_from_directory(basedir + "/static/scripts", p)

@app.route("/favicon.ico")
@app.route("/favicon.ico/")
def favicon():
	return send_from_directory(basedir , "favicon.ico")


@app.route("/_ct_", methods=["GET" , "POST"])
@app.route("/_ct_/", methods=["GET" , "POST"])
def ct():
	if "name" not in session:
		session["name"]="anon"
	if "rank" in session:
		if session["rank"] == 2:
			if request.method == "POST":
				#print(request.form)
				db.session.add(Boards(name = request.form["board"] , desc = request.form["desc"]))
				db.session.commit()
				#print("Created MEDIA")
				db.session.add(Media(board = request.form["board"]))
				db.session.commit()
				return redirect(url_for("board_home" , board=request.form["board"]))
			return render_template("ct.html")
		else:
			return "stfu"
	else:
		return "lol go away"


@app.route("/<board>/_del_" , methods=["POST"])
@app.route("/<board>/_del_/" ,  methods=["POST"])
def d(board):
	if "name" not in session:
		session["name"]="anon"
	#print(request.form)
	password = request.form["password"]
	li = list(request.form.items())
	#print(li)
	for i in li:
		if i[1] =="THREAD":
			a = Thread.query.filter_by(board=board).filter_by(id=i[0]).all()[0]
			if dec(a.password , password) or session["rank"] == 2:
				if a.img_ext:
					fi = a.board + str(a.img_num) + "." + a.img_ext
					os.remove(basedir+"/static/media/"+fi)
				b = Post.query.filter_by(board=board).filter_by(thread_id=i[0]).all()
				for post in b:
					if post.img_ext:
						fi = post.board + str(post.img_num) + "." + post.img_ext
						os.remove(basedir+"/static/media/"+fi)
					db.session.delete(post)
				for i in refer.query.filter_by(own_id=a.id).all():
					db.session.delete(i)
				db.session.delete(a)
				db.session.commit()

		elif i[1] == "POST":
			a = Post.query.filter_by(board=board).filter_by(id=i[0]).all()[0]
			if dec(a.password , password) or session["rank"] == 2:
				if a.img_ext:
					fi = a.board + str(a.img_num) + "." + a.img_ext
					os.remove(basedir+"/static/media/"+fi)
				for i in refer.query.filter_by(own_id=a.id).all():
					db.session.delete(i)
				db.session.delete(a)
				db.session.commit()

	return redirect(url_for("board_home" , board=board))


@app.route("/<board>" , methods=["GET" , "POST"])
@app.route("/<board>/", methods=["GET" , "POST"])
def board_home(board):
	if "name" not in session:
		session["name"]="anon"
	#Thread.query.filter_by(board="meta").all()
	#from sqlalchemy import desc
	#Thread.query.order_by(desc(Thread.timestamp)).all() order by time from timestamp
	bo = None
	boards = Boards.query.all()
	for b in boards:
		if b.name == board:
			exists = True
			bo = b

	ip=""
	if "X-Real-IP" in request.headers:
		ip = request.headers['X-Real-IP']
	else:
		ip = request.remote_addr

	if request.method == "POST" and not is_banned(ip):
		#print(request.files)
		#if request.form["body"]=="":
		#	return redirect(url_for("index"))
		print(request.form["subject"])
		f = None
		if bo:
			t = None
			log(board , bo.last_id + 1 , ip)
			if "file" in request.files:
				file = request.files["file"]
				file_name = secure_filename(file.filename)
				#print("FILE FOUND")
				#print(file_name)
				if not allowed(file_name)[0]:
					if request.form["body"]=="":
						return redirect(url_for("index"))
				if allowed(file_name)[0]:
					if allowed(file_name)[1] == "gif":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'],board + str(med.gif+1)+".gif"))
						med.gif = med.gif + 1
						db.session.commit()
						f = "gif"
					elif allowed(file_name)[1] == "jpeg":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'],board + str(med.jpeg+1) + ".jpeg"))
						med.jpeg = med.jpeg + 1
						db.session.commit()
						f = "jpeg"
					elif allowed(file_name)[1] == "png":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'],board + str(med.png+1) + ".png"))
						med.png = med.png + 1
						db.session.commit()
						f = "png"
					elif allowed(file_name)[1] == "jpg":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'],board + str(med.jpg+1) + ".jpg"))
						med.jpg = med.jpg + 1
						db.session.commit()
						f = "jpg"
					elif allowed(file_name)[1] == "webm":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'],board + str(med.webm+1) + ".webm"))
						med.webm = med.webm + 1
						db.session.commit()
						f = "webm"
			#else:
			if not f:
				session["name"]=request.form["name"]
				reply_finder(request.form["body"] , bo.last_id+1 , board)
				t = Thread(uni = bo.name + str(bo.last_id+1),subject=request.form["subject"],id = bo.last_id+1 , name = trip(request.form["name"]) , body=request.form["body"] , password = enc(request.form["password"]), board = board)
			else:
				#print(f , "f")
				session["name"]=request.form["name"]
				med = Media.query.filter_by(board=board).all()[0]
				file_name = secure_filename(file.filename)
				reply_finder(request.form["body"] , bo.last_id+1 , board)
				if f == "gif":
					t = Thread(img_ext = f ,subject=request.form["subject"], img_num = med.gif, img_name=file_name, uni = bo.name + str(bo.last_id+1),id=bo.last_id + 1, name=trip(request.form["name"]), body=request.form["body"],
							   password=enc(request.form["password"]), board=board)
				elif f == "jpg":
					t = Thread(img_ext=f,subject=request.form["subject"], img_num=med.jpg,uni = bo.name + str(bo.last_id+1), img_name=file_name, id=bo.last_id + 1,
							   name=trip(request.form["name"]), body=request.form["body"],
							   password=enc(request.form["password"]), board=board)
				elif f == "jpeg":
					t = Thread(img_ext=f,subject=request.form["subject"], img_num=med.jpeg, uni = bo.name + str(bo.last_id+1), img_name=file_name, id=bo.last_id + 1,
							   name=trip(request.form["name"]), body=request.form["body"],
							   password=enc(request.form["password"]), board=board)
				elif f == "png":
					t = Thread(img_ext=f,subject=request.form["subject"], img_num=med.png, uni = bo.name + str(bo.last_id+1), img_name=file_name, id=bo.last_id + 1,
							   name=trip(request.form["name"]), body=request.form["body"],
							   password=enc(request.form["password"]), board=board)
				elif f == "webm":
					t = Thread(img_ext=f,subject=request.form["subject"], img_num=med.webm ,uni = bo.name + str(bo.last_id+1), img_name=file_name, id=bo.last_id + 1,
							   name=trip(request.form["name"]), body=request.form["body"],
							   password=enc(request.form["password"]), board=board)



			#print(bo.last_id)
			bo.last_id = bo.last_id + 1
			db.session.commit()
			#print(bo.last_id)
			db.session.add(t)
			db.session.commit()

			return render_template("board.html" ,theme=bo.theme,themes=themes,board_list=boards_list,len=len,random=random_banner,green=green,url_maker=url_maker,anon=session["name"],refer=refer,bo=bo, gen=gen , Post = Post, board = board , desc = bo.desc , threads = Thread.query.filter_by(board=board).order_by(desc(Thread.bumptime)).all())

	if bo:
		return render_template("board.html" ,theme=bo.theme,themes=themes,board_list=boards_list,len=len,random=random_banner,green=green,url_maker=url_maker,anon=session["name"],refer=refer,bo=bo,gen=gen ,Post = Post, board = board , desc = bo.desc , threads = Thread.query.filter_by(board=board).order_by(desc(Thread.bumptime)).all())
	else:
		return "There exists no board like that" , 404

@app.route("/<board>/<int:thread_id>/" , methods=["GET" , "POST"])
@app.route("/<board>/<int:thread_id>", methods=["GET" , "POST"])
def board_thread(board , thread_id):
	if "name" not in session:
		session["name"]="anon"
	#Thread.query.filter_by(board="meta").all()
	#from sqlalchemy import desc
	#Thread.query.order_by(desc(Thread.timestamp)).all() order by time from timestamp
	#try:
	thread = Thread.query.filter_by(board=board).filter_by(id=thread_id).all()[0]
	bo = Boards.query.filter_by(name=board).all()[0]
	#except:
	#	thread = None
	ip=""
	if "X-Real-IP" in request.headers:
		ip = request.headers['X-Real-IP']
	else:
		ip = request.remote_addr

	if request.method == "POST" and not is_banned(ip):
		#print(request.files)
		#if request.form["body"]=="":
		#	return redirect(url_for("index"))
		f = None
		if thread:
			log(board , bo.last_id + 1 ,ip)
			if "file" in request.files:
				file = request.files["file"]
				file_name = secure_filename(file.filename)
				#print("FILE FOUND")
				#print(file_name)
				if not allowed(file_name)[0]:
					if request.form["body"]=="":
						return redirect(url_for("index"))
				if allowed(file_name)[0]:
					if allowed(file_name)[1] == "gif":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'], board + str(med.gif + 1) + ".gif"))
						med.gif = med.gif + 1
						db.session.commit()
						f = "gif"
					elif allowed(file_name)[1] == "jpeg":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'], board + str(med.jpeg + 1) + ".jpeg"))
						med.jpeg = med.jpeg + 1
						db.session.commit()
						f = "jpeg"
					elif allowed(file_name)[1] == "png":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'], board + str(med.png + 1) + ".png"))
						med.png = med.png + 1
						db.session.commit()
						f = "png"
					elif allowed(file_name)[1] == "jpg":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'], board + str(med.jpg + 1) + ".jpg"))
						med.jpg = med.jpg + 1
						db.session.commit()
						f = "jpg"
					elif allowed(file_name)[1] == "webm":
						med = Media.query.filter_by(board=board).all()[0]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'], board + str(med.webm + 1) + ".webm"))
						med.webm = med.webm + 1
						db.session.commit()
						f = "webm"
			# else:
			if not f:
				reply_finder(request.form["body"] , bo.last_id+1 , bo.name)
				session["name"]=request.form["name"]
				p = Post(uni=bo.name + str(bo.last_id + 1), thread_id = thread_id, id=bo.last_id + 1, name=trip(request.form["name"]),
						   body=request.form["body"], password=enc(request.form["password"]), board=board)
			else:
				#print(f, "f")
				reply_finder(request.form["body"] , bo.last_id+1 , bo.name)
				session["name"]=request.form["name"]
				med = Media.query.filter_by(board=board).all()[0]
				file_name = secure_filename(file.filename)
				if f == "gif":
					p = Post(img_ext=f, thread_id = thread_id, img_num=med.gif, img_name=file_name, uni=bo.name + str(bo.last_id + 1),
							   id=bo.last_id + 1, name=trip(request.form["name"]),body=request.form["body"],
							   password=enc(request.form["password"]), board=board)
				elif f == "jpg":
					p = Post(img_ext=f, thread_id = thread_id, img_num=med.jpg, uni=bo.name + str(bo.last_id + 1), img_name=file_name,
							   id=bo.last_id + 1,
							   name=trip(request.form["name"]), body=request.form["body"],
							   password=enc(request.form["password"]), board=board)
				elif f == "jpeg":
					p = Post(img_ext=f, thread_id = thread_id, img_num=med.jpeg, uni=bo.name + str(bo.last_id + 1), img_name=file_name,
							   id=bo.last_id + 1,
							   name=trip(request.form["name"]), body=request.form["body"],
							   password=enc(request.form["password"]), board=board)
				elif f == "png":
					p = Post(img_ext=f, thread_id = thread_id, img_num=med.png, uni=bo.name + str(bo.last_id + 1), img_name=file_name,
							   id=bo.last_id + 1,
							   name=trip(request.form["name"]), body=request.form["body"],
							   password=enc(request.form["password"]), board=board)
				elif f == "webm":
					p = Post(img_ext=f, thread_id = thread_id, img_num=med.webm, uni=bo.name + str(bo.last_id + 1), img_name=file_name,
							   id=bo.last_id + 1,
							   name=trip(request.form["name"]),body=request.form["body"],
							   password=enc(request.form["password"]), board=board)

			#print(bo.last_id)
			#bo.last_id = bo.last_id + 1
			#db.session.commit()
			#print(bo.last_id)
			#db.session.add(t)
			#db.session.commit()


			#p = Post(uni = bo.name + str(bo.last_id+1),id = bo.last_id+1 , name = request.form["name"] , body = request.form["body"] , password = enc(request.form["password"]), board = board , thread_id = thread_id)
			#print(bo.last_id)
			bo.last_id = bo.last_id + 1
			db.session.commit()
			if request.form["options"].lower() != "sage" or thread.bump==bo.bump_limit:
				thread.bumptime = datetime.datetime.utcnow()
				db.session.commit()
				thread.bump = thread.bump+1
				db.session.commit()
			#print(bo.last_id)
			db.session.add(p)
			db.session.commit()
			reply = request.args.get('r')
			if not reply:
				reply=""
			else:
				reply = ">>"+reply+" "
			return render_template("thread.html" ,len=len,theme=bo.theme,themes=themes,board_list=boards_list, reply=reply,random=random_banner,green=green,url_maker=url_maker,anon=session["name"],refer=refer,gen=gen , board = board , thread_id = thread_id , thread=thread, posts = Post.query.filter_by(board=board).filter_by(thread_id = thread_id).order_by(asc(Post.timestamp)).all())

	if thread:
		reply = request.args.get('r')
		if not reply:
			reply=""
		else:
			reply = ">>"+reply+" "
		return render_template("thread.html" ,len=len,theme=bo.theme,themes=themes,board_list=boards_list,reply=reply,random=random_banner,green=green,url_maker=url_maker,anon=session["name"],refer=refer,gen=gen , board = board , thread_id = thread_id , thread=thread, posts = Post.query.filter_by(board=board).filter_by(thread_id = thread_id).order_by(asc(Post.timestamp)).all())
	else:
		return "There exists no thread like that" , 404



if __name__ == "__main__":
	app.debug = True
	app.run()
