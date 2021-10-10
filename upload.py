from flask import * 
from characterExtraction import *
from watson_edited import *
from main4 import *
import os, time
app = Flask(__name__)  

loc = ''

@app.route('/')  
def upload():  
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
	    f.save("ip.txt") 
	    '''fname = "user_"+str(time.time())
	    path = "/home/archanaj/Documents/CAPSTONE PROJECT/capstone/Code/user_sessions/"
	    loc=os.path.join(path, fname)
	    os.mkdir(loc)
	    fpath=os.path.join(loc,"ip.txt")
	    f.save(fpath)'''    #change paths of static file and image and check if the image exists before processing it.
	    return render_template("select.html")  
	#return render_template("select.html")
	
character_name=''
@app.route('/personality_profiling', methods=['POST', 'GET'])
def personality_profiling():
	if request.method == 'POST':
		text = readText()
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
		
		writeToJSON(sentenceAnalysis)
		#print(sentenceAnalysis)
		# writeAnalysis(sentenceAnalysis)
		return render_template("personality_profiling.html", names= majorCharacters)

@app.route("/watson", methods = ['POST'])
def watson():
	filename = "watson_fig"+str(time.time())+".png"
	'''for filename in os.listdir('static/'):
		os.remove('static/' + filename)'''
	character_name=request.form.get('character')
	print("####### ",character_name)
	tone_analyzer = authenticate()
	character_personality_plot(character_name, tone_analyzer, filename)
	return render_template("watson.html", image=filename)
	
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
