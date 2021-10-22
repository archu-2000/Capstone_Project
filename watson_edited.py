import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.interpolate import make_interp_spline

import plotly.graph_objects as go
import plotly.offline as pyo


def authenticate():
	authenticator = IAMAuthenticator('Q_O6H2qcfbYauP2ZJK0loX9hMn5JZRLLqrwFJAkQekDM')
	tone_analyzer = ToneAnalyzerV3(
	    version='2016-05-19',
	    authenticator=authenticator
	)

	tone_analyzer.set_service_url('https://api.au-syd.tone-analyzer.watson.cloud.ibm.com/instances/78368241-41bf-4585-bd43-0e8e7cfc6d48')
	return tone_analyzer

def character_personality_plot(character, tone_analyzer, image_name, loc):
	#print(loc)
	f = open(loc+"/sentenceAnalysis.json",)
	temp = json.load(f)
	sentences = temp[character][0]
	#print(len(sentences))
	#sentences=['I am very pleased with him.', 'I am satisfied with him.', 'I am neutral at him.', 'I am furious at him.', 'melancholy']

	text =''
	#sentences = sentences[:10]
	for sentence in sentences:
		sentence = sentence.replace("\n",'') + " "
		text+=sentence
	#print(text)

	tone_analysis = tone_analyzer.tone(
			{'text': text},
			content_type='application/json',
			tones = ['emotion', 'social', 'language']
		).get_result()

	#print(json.dumps(tone_analysis, indent=2))

	doc_tones= tone_analysis["document_tone"]["tone_categories"]

	if image_name == 'switch':
		return doc_tones


	social_arr={"Openness":[],"Conscientiousness":[],"Extraversion":[],"Agreeableness":[],"Emotional Range":[]}
	emotion_arr={"Anger":[], "Disgust":[], "Fear":[], "Joy":[], "Sadness":[] }
	language_arr={"Analytical":[], "Confident":[], "Tentative":[]}

	# print(tone_analysis)

	for i in tone_analysis["sentences_tone"]:
		for j in i["tone_categories"][0]["tones"]:
			emotion_arr[j["tone_name"]].append(j["score"])

		for j in i["tone_categories"][2]["tones"]:
			social_arr[j["tone_name"]].append(j["score"])
		
		for j in i["tone_categories"][1]["tones"]:
			language_arr[j["tone_name"]].append(j["score"])


	arr=[]
	for i in doc_tones[0]["tones"]:
		arr.append(i["score"])
	arr=[*arr,arr[0]]

	legend = ['Anger','Disgust','Fear','Joy','Sadness']
	legend = [*legend, legend[0]]
	
	fig = go.Figure(data=[go.Scatterpolar(r=arr, theta=legend, name='Emotion')],layout=go.Layout(title=go.layout.Title(text=str(character)+" emotions"),polar={'radialaxis': {'visible': True}},showlegend=True))

	#pyo.plot(fig)
	fig.write_image("static/radar_emotion_"+image_name)

	######################################################################################################################
	#print(emotion_arr)
	emotion_arr_2={"Anger":[], "Disgust":[], "Fear":[], "Joy":[], "Sadness":[] }
	social_arr_2={"Openness":[],"Conscientiousness":[],"Extraversion":[],"Agreeableness":[],"Emotional Range":[]}
	language_arr_2={"Analytical":[], "Confident":[], "Tentative":[]}
	# print(len(emotion_arr["Anger"]))

	for i in emotion_arr:
		j=0
		#k =int(len(emotion_arr[i])/10)
		k =int(len(emotion_arr[i])/5)
		while j<len(emotion_arr[i]):
			#print(j,k)
			avg_temp = sum(emotion_arr[i][j:j+k])/k
			emotion_arr_2[i].append(avg_temp)
			j+=k

	#print(emotion_arr_2)

	x=np.array([i+1 for i in range(len(emotion_arr_2["Anger"]))])

	 
	# Returns evenly spaced numbers
	# over a specified interval.
	
	plt.clf()
	for i,key in enumerate(emotion_arr):
		
		X_Y_Spline = make_interp_spline(x, np.array(emotion_arr_2[key]))
		X_ = np.linspace(x.min(), x.max(), 500)
		Y_ = X_Y_Spline(X_)
		plt.plot(X_,Y_)


	plt.legend(["Anger", "Disgust", "Fear", "Joy", "Sadness"])
	plt.title(str(character))
	#plt.show()
	'''static = os.path.join(loc, 'static/')
	os.mkdir(static)
	print("loc = ",loc)
	plt.savefig(static+image_name)'''
	plt.savefig('static/emotion_'+image_name)


	

	#---------------------------------emotion----------------------------------------------------------
	for i in social_arr:
		j=0
		#k =int(len(emotion_arr[i])/10)
		k =int(len(social_arr[i])/5)
		while j<len(social_arr[i]):
			#print(j,k)
			avg_temp = sum(social_arr[i][j:j+k])/k
			social_arr_2[i].append(avg_temp)
			j+=k

	#print(social_arr_2)

	x=np.array([i+1 for i in range(len(social_arr_2["Openness"]))])

	 
	# Returns evenly spaced numbers
	# over a specified interval.
	
	plt.clf()
	for i,key in enumerate(social_arr):
		
		X_Y_Spline = make_interp_spline(x, np.array(social_arr_2[key]))
		X_ = np.linspace(x.min(), x.max(), 500)
		Y_ = X_Y_Spline(X_)
		plt.plot(X_,Y_)


	plt.legend(["Openness","Conscientiousness","Extraversion","Agreeableness","Emotional Range"])
	plt.title(str(character))
	#plt.show()
	'''static = os.path.join(loc, 'static/')
	os.mkdir(static)
	print("loc = ",loc)
	plt.savefig(static+image_name)'''
	plt.savefig('static/social_'+image_name)



	###-----------------------------------------language---------------------------------------------------------


	for i in language_arr:
		j=0
		#k =int(len(emotion_arr[i])/10)
		k =int(len(language_arr[i])/5)
		while j<len(language_arr[i]):
			#print(j,k)
			avg_temp = sum(language_arr[i][j:j+k])/k
			language_arr_2[i].append(avg_temp)
			j+=k

	#print(language_arr_2)

	x=np.array([i+1 for i in range(len(language_arr_2["Analytical"]))])

	 
	# Returns evenly spaced numbers
	# over a specified interval.
	
	plt.clf()
	for i,key in enumerate(language_arr):
		
		X_Y_Spline = make_interp_spline(x, np.array(language_arr_2[key]))
		X_ = np.linspace(x.min(), x.max(), 500)
		Y_ = X_Y_Spline(X_)
		plt.plot(X_,Y_)


	plt.legend(["Analytical", "Confident", "Tentative"])
	plt.title(str(character))
	#plt.show()
	'''static = os.path.join(loc, 'static/')
	os.mkdir(static)
	print("loc = ",loc)
	plt.savefig(static+image_name)'''
	plt.savefig('static/language_'+image_name)


	return True
