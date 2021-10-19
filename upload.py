from flask import * 
from characterExtraction import *
from watson_edited import *
from main4 import *
import os, time, sqlite3, hashlib
app = Flask(__name__)  

loc = ''
fpath = ''
dir_name=''
uname = ''

class A:
	def is_valid(self, uname, password):
		con = sqlite3.connect('database2.db')
		cur = con.cursor()
		cur.execute('SELECT userId, password FROM users')
		data = cur.fetchall()
		con.close()
		print(data)
		for row in data:
			if row[0] == uname and row[1] == password:
				return True
		return False

@app.route('/')
def home():
	return render_template("home.html")
	
@app.route('/signup', methods = ['POST'])
def signup():
	return render_template("signup.html")
	
@app.route('/signing_up', methods = ['POST'])
def add_user():
	global uname
	uname = request.form.get('Uname')
	pwd = request.form.get('Password')
	name = request.form.get('name')
	email = request.form.get('email')
	c_pwd = request.form.get('c_Password')
	if c_pwd!=pwd:
		return render_template('signup.html')
	else:
		con = sqlite3.connect('database2.db')
		cur = con.cursor()
		user = (uname, pwd, email, name)
		sql = '''INSERT INTO users(userId, password, email, fullName) values(?,?,?,?)'''
		cur.execute(sql, user) 
		con.commit()
		con.close()
		return redirect(url_for('upload'))                                          

@app.route('/login', methods = ['POST'])
def login():
	return render_template("login.html")

@app.route('/upload', methods = ['POST', 'GET'])  
def upload():  
	if request.method == 'POST':
		global uname
		uname = request.form.get('Uname')
		password = request.form.get('Pass')
		a = A()
		valid = a.is_valid(uname, password)
		if valid:
			return render_template("file_upload_form.html")  
		else:
			return render_template("login.html")
	else:
		return render_template("file_upload_form.html")
		
@app.route('/success', methods = ['POST'])  
def success():  
	if request.method == 'POST':  
	    f = request.files['file']  
	    f.save("ip.txt")  
	    return render_template("success.html", name = f.filename)  

@app.route('/select', methods = ['POST'])
def select():
	if request.method == 'POST':  
	    f = request.files['file']  
	    #f.save("ip.txt") 
	    global uname
	    loc1 = "/home/archanaj/Documents/CAPSTONE PROJECT/capstone/Code/static/"
	    if os.path.exists(loc1):
		    for i in os.listdir(loc1):
		    	if i.startswith(uname):
		    		os.remove(loc1+'/'+i)
	    #dir_name = "user_"+str(time.time())
	    #dir_name = "user1"
	    path = "/home/archanaj/Documents/CAPSTONE PROJECT/capstone/Code/user_sessions"
	    global loc
	    loc=os.path.join(path, uname)
	    if os.path.exists(loc):
		    for i in os.listdir(loc):
		    	#print("]]]]]]]]]]]]]]] ",uname)
		    	os.remove(loc+'/'+i)
		    os.rmdir(loc)
	    os.mkdir(loc)
	    global fpath
	    fpath=os.path.join(loc,"ip.txt")
	    f.save(fpath)    #change paths of static file and image and check if the image exists before processing it.
	    return render_template("select.html")  
	#return render_template("select.html")
	
character_name=''
@app.route('/personality_profiling', methods=['POST', 'GET'])
def personality_profiling():
	if request.method == 'POST':
		global fpath
		text = readText(fpath)
		chunkedSentences = chunkSentences(text)
		# print(list(chunkedSentences))
		entityNames = buildDict(chunkedSentences)
		# print(list(entityNames))
		removeStopwords(entityNames)
		majorCharacters = getMajorCharacters(entityNames)
		# print(list(majorCharacters))

		sentenceList = splitIntoSentences(text)
		characterSentences = compareLists(sentenceList, majorCharacters)
		#print("@@@@@@@@@@@@@@@@: ", characterSentences)

		#characterTones = extractTones(characterSentences)

		sentenceAnalysis = defaultdict(list,[(k, [characterSentences[k], 0]) for k in characterSentences])
		#CHANGE THE SENTENCE ANALAYSIS FILE NAME AND PATH
		global loc
		writeToJSON(sentenceAnalysis, loc)
		#print(sentenceAnalysis)
		# writeAnalysis(sentenceAnalysis)
		return render_template("personality_profiling.html", names= majorCharacters)

@app.route("/watson", methods = ['POST'])
def watson():
	global uname
	#filename = "watson_fig"+str(time.time())+".png"
	'''for filename in os.listdir('static/'):
		os.remove('static/' + filename)'''
	character_name=request.form.get('character')
	path = "/home/archanaj/Documents/CAPSTONE PROJECT/capstone/Code/static/"
	image = uname+'_'+character_name+'.png'
	if os.path.exists(path+image)==False:
		print("####### ",image)
		tone_analyzer = authenticate()
		global loc
		character_personality_plot(character_name, tone_analyzer, image, loc)
	
	return render_template("watson.html", image=image)
	
@app.route("/logout", methods = ['POST'])
def logout():
	path = "/home/archanaj/Documents/CAPSTONE PROJECT/capstone/Code/user_sessions/"
	global loc
	global uname
	loc1 = "/home/archanaj/Documents/CAPSTONE PROJECT/capstone/Code/static/"
	if os.path.exists(loc1):
	    for i in os.listdir(loc1):
	    	if i.startswith(uname):
	    		os.remove(loc1+'/'+i)
	loc=os.path.join(path, uname)
	if os.path.exists(loc):
	    for i in os.listdir(loc):
	    	#print("]]]]]]]]]]]]]]] ",uname)
	    	os.remove(loc+'/'+i)
	    os.rmdir(loc)
	return render_template("login.html")
	
@app.route("/choose_characters", methods = ['POST'])
def choose_characters():
	text = readText()
	chunkedSentences = chunkSentences(text)
	# print(list(chunkedSentences))
	entityNames = buildDict(chunkedSentences)
	# print(list(entityNames))
	removeStopwords(entityNames)
	majorCharacters = getMajorCharacters(entityNames)
	return render_template("choose_characters.html", names = majorCharacters)

@app.route("/character_networks", methods = ['POST'])
def character_networks():
	character_name1=request.form.get('character1')
	character_name2=request.form.get('character2')
	character_name3=request.form.get('character3')
	with open("ip.txt", "r") as f:
        	# text = f.read().decode('utf-8-sig')
        	text = f.read()
	pre_processing(text)
	graph_obj = graphs(text, 500)
	entities = [character_name1, character_name2, character_name3]
	img_name="entity_interaction_"+str(time.time())+".png"
	graph_obj.entity_interaction_graph(entities, img_name)
	#graph_obj.char_importance()
	return render_template("character_networks.html", image = img_name)
	
if __name__ == '__main__':  
	app.run(debug = True)  
