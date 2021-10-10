import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.interpolate import make_interp_spline

def authenticate():
	authenticator = IAMAuthenticator('Q_O6H2qcfbYauP2ZJK0loX9hMn5JZRLLqrwFJAkQekDM')
	tone_analyzer = ToneAnalyzerV3(
	    version='2016-05-19',
	    authenticator=authenticator
	)

	tone_analyzer.set_service_url('https://api.au-syd.tone-analyzer.watson.cloud.ibm.com/instances/78368241-41bf-4585-bd43-0e8e7cfc6d48')
	return tone_analyzer
'''
text = "Hermione is very smart. Hermione is beautiful"
text2 = "Hello Ha\nrry.I will kill harry."
print(text)

'''
def character_personality_plot(character, tone_analyzer, image_name):
	f = open("sentenceAnalysis.json",)
	temp = json.load(f)
	sentences = temp[character][0]
	#print(len(sentences))
	#sentences=['I am very pleased with him.', 'I am satisfied with him.', 'I am neutral at him.', 'I am furious at him.', 'melancholy']

	text =''
	sentences = sentences[:10]
	for sentence in sentences:
		sentence = sentence.replace("\n",'') + " "
		text+=sentence
	#print(text)

	tone_analysis = tone_analyzer.tone(
			{'text': text},
			content_type='application/json',
			tones = ['emotion']
		).get_result()

	# print(json.dumps(tone_analysis, indent=2))

	#social_arr={"Openness":[],"Conscientiousness":[],"Extraversion":[],"Agreeableness":[],"Emotional Range":[]}

	emotion_arr={"Anger":[], "Disgust":[], "Fear":[], "Joy":[], "Sadness":[] }

	for i in tone_analysis["sentences_tone"]:
		for j in i["tone_categories"][0]["tones"]:
			emotion_arr[j["tone_name"]].append(j["score"])

	#print(emotion_arr)

	x=np.array([i+1 for i in range(len(emotion_arr["Anger"]))])

	 
	# Returns evenly spaced numbers
	# over a specified interval.
	
	plt.clf()
	for i,key in enumerate(emotion_arr):
		
		X_Y_Spline = make_interp_spline(x, np.array(emotion_arr[key]))
		X_ = np.linspace(x.min(), x.max(), 500)
		Y_ = X_Y_Spline(X_)
		plt.plot(X_,Y_)


	plt.legend(["Anger","Disgust","Fear","Joy","Sadness"])
	plt.title(str(character))
	#plt.show()
	'''static = os.path.join(loc, 'static/')
	os.mkdir(static)
	print("loc = ",loc)
	plt.savefig(static+image_name)'''
	plt.savefig('static/'+image_name)



#character_personality_plot('Mr. Bumble')

'''
tone_analysis = tone_analyzer.tone(
	    {'text': text},
	    content_type='application/json',
	    tones = ['social']
	).get_result()
print(json.dumps(tone_analysis, indent=2))

tone_analysis = tone_analyzer.tone(
	    {'text': text2},
	    content_type='application/json',
	    tones = ['social']
	).get_result()

print(json.dumps(tone_analysis, indent=2))
'''
