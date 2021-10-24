from flask import * 
from characterExtraction_new import *
from watson_edited import *
# from main4 import *
import os, time, sqlite3, hashlib
app = Flask(__name__)  
import PyPDF2
from graph_final import *
import time


loc = ''
fpath = ''
dir_name=''
uname = ''
tone_analyzer=''
characters=''


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



@app.route('/select_new', methods = ['POST'])
def select_new():

	if request.method == 'POST':
		
		f = request.files['file']
		f_name=f.filename
		
		if f_name.endswith(".txt"):
		
			f.save("ip.txt")
		if f_name.endswith(".pdf"):
			
			f.save("ip.pdf")


			pdffileobj=open("ip.pdf",'rb')
			pdfreader=PyPDF2.PdfFileReader(pdffileobj)
			x=pdfreader.numPages
			file1=open("ip.txt","a")
			for page_count in range(x):
				page = pdfreader.getPage(page_count)
				page_data = page.extractText()
				file1.write(page_data)

			# pageobj=pdfreader.getPage(0)
			# text=pageobj.extractText()
			
			
			# file1.writelines(text) 
		return render_template("select.html")  
	#return render_template("select.html")


@app.route('/select', methods = ['POST'])
def select():
	if request.method == 'POST':  
		f = request.files['file']  
	    #f.save("ip.txt") 
		global uname
		loc1 = "/static/"
		if os.path.exists(loc1):
			for i in os.listdir(loc1):
				if i.startswith(uname):
					os.remove(loc1+'/'+i)
	    #dir_name = "user_"+str(time.time())
	    #dir_name = "user1"
		path = "user_sessions"
		global loc
		#loc = path+'/'+uname
		loc=path+'/'+uname
		# loc=os.path.join(path, uname)
		if os.path.exists(loc):
			for i in os.listdir(loc):
		    	#print("]]]]]]]]]]]]]]] ",uname)
				os.remove(loc+'/'+i)
			os.rmdir(loc)
		os.mkdir(loc)
		global fpath

		f_name=f.filename
		if f_name.endswith(".txt"):

			fpath=os.path.join(loc,"ip.txt")
			f.save(fpath)    #change paths of static file and image and check if the image exists before processing it.

		if f_name.endswith(".pdf"):
			fpath_pdf=os.path.join(loc,"ip.pdf")
			f.save(fpath_pdf)
			pdffileobj=open(fpath_pdf,'rb')
			pdfreader=PyPDF2.PdfFileReader(pdffileobj)
			x=pdfreader.numPages
			# pdffileobj.close()

			fpath=os.path.join(loc,"ip.txt")
			file1=open(fpath,"a")

			for page_count in range(x):
				page = pdfreader.getPage(page_count)
				page_data = page.extractText()
				file1.write(page_data)
			
			file1.close()
			pdffileobj.close()

	return render_template("select.html")  
	#return render_template("select.html")
	
character_name=''
@app.route('/personality_profiling', methods=['POST', 'GET'])
def personality_profiling():
	if request.method == 'POST':
		


		# text = readText(fpath)
		# chunkedSentences = chunkSentences(text)
		# # print(list(chunkedSentences))
		# entityNames = buildDict(chunkedSentences)
		# # print(list(entityNames))
		# removeStopwords(entityNames)
		# majorCharacters = getMajorCharacters(entityNames)
		# # print(list(majorCharacters))

		# sentenceList = splitIntoSentences(text)
		# characterSentences = compareLists(sentenceList, majorCharacters)
		# #print("@@@@@@@@@@@@@@@@: ", characterSentences)

		# #characterTones = extractTones(characterSentences)

		# sentenceAnalysis = defaultdict(list,[(k, [characterSentences[k], 0]) for k in characterSentences])
		# #CHANGE THE SENTENCE ANALAYSIS FILE NAME AND PATH

		global fpath
		global loc
		
		#print(sentenceAnalysis)
		# writeAnalysis(sentenceAnalysis)

		
		text = readText(fpath)
		entityNames = getCharacters(text)
		d, mc, tl = mergeNames_count(entityNames)
		sentenceList = splitIntoSentences(text)
		characterSentences = compare_lists_new(sentenceList, mc, d)
		print(list(characterSentences))
		sentenceAnalysis = defaultdict(list,[(k, [characterSentences[k], 0]) for k in characterSentences])
		writeToJSON(sentenceAnalysis, loc)

		global characters
		characters = mc
		global tone_analyzer
		tone_analyzer = authenticate()

		with open("chars.txt", "a") as f:
			f.write("\n".join(characters))

		return render_template("personality_profiling.html", names= mc)

@app.route("/emotion_analysis", methods = ['POST'])
def emotion_analysis():

	
	emotion_ranks={"Anger":[], "Disgust":[], "Fear":[], "Joy":[], "Sadness":[] }
	language_ranks={"Analytical":[], "Confident":[], "Tentative":[]}
	social_ranks={"Openness":[],"Conscientiousness":[],"Extraversion":[],"Agreeableness":[],"Emotional Range":[]}

	for character_name in characters:
		global tone_analyzer
		#print(type(tone_analyzer))
		print(character_name)
		x =character_personality_plot(character_name, tone_analyzer, 'switch', loc)
		#print("1) ",x[0])
		for i in x[0]["tones"]:
			emotion_ranks[i["tone_name"]].append((i["score"],character_name))
		for i in x[1]["tones"]:
			language_ranks[i["tone_name"]].append((i["score"],character_name))
		for i in x[2]["tones"]:
			social_ranks[i["tone_name"]].append((i["score"],character_name))

	print(emotion_ranks,language_ranks, social_ranks)
	for key in emotion_ranks.keys():
		emotion_ranks[key].sort(reverse=True)
	for key in language_ranks.keys():
		language_ranks[key].sort(reverse=True)
	for key in social_ranks.keys():
		social_ranks[key].sort(reverse=True)

	emotion_list={}
	for key in emotion_ranks:
		emotion_list[key]=[]
		for i in emotion_ranks[key][:3]:
			emotion_list[key].append(i[1])

	language_list={}
	for key in language_ranks:
		language_list[key]=[]
		for i in language_ranks[key][:3]:
			language_list[key].append(i[1])

	social_list={}
	for key in social_ranks:
		social_list[key]=[]
		for i in social_ranks[key][:3]:
			social_list[key].append(i[1])



	return render_template("analysis.html", emotion_list =emotion_list, emotion_keys=emotion_list.keys(), language_list =language_list, language_keys=language_list.keys(), social_list =social_list, social_keys=social_list.keys() )

	#print(arr)

@app.route("/watson", methods = ['POST'])
def watson():
	global uname
	#filename = "watson_fig"+str(time.time())+".png"
	'''for filename in os.listdir('static/'):
		os.remove('static/' + filename)'''
	character_name=request.form.get('character')
	path = "/static/"
	image = uname+'_'+character_name+'.png'
	if os.path.exists(path+image)==False:
		#print("####### ",image)
		global tone_analyzer
		global loc
		character_personality_plot(character_name, tone_analyzer, image, loc)

		i2="social_"+image
		i1="emotion_"+image
		i3="language_"+image
		i4="radar_emotion_"+image

	return render_template("watson.html", image1=i1, image2=i2, image3=i3, image4=i4)
	
@app.route("/logout", methods = ['POST'])
def logout():
	path = "user_sessions/"
	global loc
	global uname
	loc1 = "static/"
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


@app.route("/network_graph", methods = ['POST'])
def network_graph():
	iname = uname+str(time.time())+'_network.png'
	degree_centrality_ranks = network_graph_main(loc, iname)
	l = {}
	for i in range(len(degree_centrality_ranks)):
		l[i+1]= degree_centrality_ranks[i]
	print(l)

	return render_template("network_graph.html", ranks = l, i1=iname)



# @app.route("/choose_characters", methods = ['POST'])
# def choose_characters():
# 	text = readText()
# 	chunkedSentences = chunkSentences(text)
# 	# print(list(chunkedSentences))
# 	entityNames = buildDict(chunkedSentences)
# 	# print(list(entityNames))
# 	removeStopwords(entityNames)
# 	majorCharacters = getMajorCharacters(entityNames)
# 	return render_template("choose_characters.html", names = majorCharacters)

# @app.route("/character_networks", methods = ['POST'])
# def character_networks():
# 	character_name1=request.form.get('character1')
# 	character_name2=request.form.get('character2')
# 	character_name3=request.form.get('character3')
# 	with open("ip.txt", "r") as f:
#         	# text = f.read().decode('utf-8-sig')
#         	text = f.read()
# 	pre_processing(text)
# 	graph_obj = graphs(text, 500)
# 	entities = [character_name1, character_name2, character_name3]
# 	img_name="entity_interaction_"+str(time.time())+".png"
# 	graph_obj.entity_interaction_graph(entities, img_name)
# 	#graph_obj.char_importance()
# 	return render_template("character_networks.html", image = img_name)
	
if __name__ == '__main__':  
	app.run(debug = True)  
