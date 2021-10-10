import argparse
import os
import pickle
import re
from tqdm import tqdm
from nameparser import HumanName
from itertools import product

import matplotlib.pyplot as plt
import networkx as nx


from src.third_party.bert_ner.bert import Ner


class Literature():

	def __init__(self,text):
		self.filename='ip.txt'
		self.text=text
		self.lines=self.text.split('\n')
		self.headings=self.getHeadings()

		self.chapters=self.getChapterContent()

		# print(len(self.chapters))

		self.splitChapters()

	def splitChapters(self):

		numbers = range(1,len(self.chapters)+1)
		maxNum = max(numbers)
		maxDigits = len(str(maxNum))
		chapterNums = [str(number).zfill(maxDigits) for number in numbers]
		
		print("chapterNums: ", chapterNums)

		basename=os.path.basename(self.filename)
		noExt = os.path.splitext(basename)[0]

		outDir = noExt + '_chapters'

		# print(basename,noExt,outDir)

		if not os.path.exists(outDir):
			os.makedirs(outDir)

		for num,chapter in zip(chapterNums,self.chapters):
			path = outDir + '/' + num + '.txt'

			# print("chapter before: ",chapter)
			chapter = '\n'.join(chapter)
			# print("chapter after: ",chapter)

			with open(path,'w') as f:
				f.write(chapter)


	def getChapterContent(self):
		chapters=[]

		lastHeading = len(self.headings) -1
		for i,headingLocation in enumerate(self.headings):
			if i != lastHeading:
				nextHeading = self.headings[i+1]
				chapters.append(self.lines[headingLocation+1:nextHeading])
		return chapters

	def getHeadings(self):

		# Considering forms of headings

		#Form : Chapter I, Chapter 1, Chapter the First, Chapter.1

		arabicNumerals = '\d+'

		romanNumerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'

		numberWordsByTens = ['twenty', 'thirty', 'forty', 'fifty', 'sixty',
                              'seventy', 'eighty', 'ninety']

		numberWords = ['one', 'two', 'three', 'four', 'five', 'six',
                       'seven', 'eight', 'nine', 'ten', 'eleven',
                       'twelve', 'thirteen', 'fourteen', 'fifteen',
                       'sixteen', 'seventeen', 'eighteen', 'nineteen'] + numberWordsByTens

		numberWordsPat = '(' + '|'.join(numberWords) + ')'

		ordinalNumberWordsByTens = ['twentieth', 'thirtieth', 'fortieth', 'fiftieth', 
                                    'sixtieth', 'seventieth', 'eightieth', 'ninetieth'] + numberWordsByTens

		ordinalNumberWords = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 
                              'seventh', 'eighth', 'ninth', 'twelfth', 'last'] + \
                             [numberWord + 'th' for numberWord in numberWords] + ordinalNumberWordsByTens

		ordinalsPat = '(the )?(' + '|'.join(ordinalNumberWords) + ')'

		enumeratorsList = [arabicNumerals, romanNumerals, numberWordsPat, ordinalsPat] 

		enumerators = '(' + '|'.join(enumeratorsList) + ')'

		form = 'chapter ' + enumerators

		#Form 2 : II. THE ASTROLOGER

		enumerators2 = romanNumerals
		seperators = '(\. | )'
		title_format = '[A-Z][A-Z]'
		form2 = enumerators2 + seperators + title_format

		pattern = re.compile(form,re.IGNORECASE)
		pattern2 = re.compile(form2)

		headings = []

		for i,line in enumerate(self.lines):
			if pattern.match(line) is not None:
				headings.append(i)

			elif pattern2.match(line) is not None:
				headings.append(i)
		
		headings.append(len(self.lines)-1)

		# print(headings)
		return headings

class Entity:

	def __init__(self,name,gender=3):
		self.name = name
		self.gender=gender

		#Gender : male=1, female=2, Unknown=3

class Coreferences():

	def __init__(self,name_list):
		self.name_list=name_list
		self.entity_set=set()
		self.entity_match= dict()

		self.male_names=self.load_names('coreferences/male_name.txt')
		self.female_names=self.load_names('coreferences/female_name.txt')
		self.male_titles=self.load_names('coreferences/male_title.txt')
		self.female_titles=self.load_names('coreferences/female_name.txt')
		self.neutral_titles=self.load_names('coreferences/neutral_titles.txt')
		# self.nicknames=self.load_names('coreferences/nicknames.txt')

	def load_names(self,path):
		with open(path,'r') as f:
			l=f.read().splitlines()
		return [name.lower() for name in l]

	def find_gender(self,name):				# Gender : 1-Male, 2 -Female, 3- Unknown
		if name.title in self.male_titles:
			return 1
		if name.title in self.female_titles:
			return 2
		if name.first in self.male_names:
			return 1
		if name.first in self.female_names:
			return 2
		return 3

	def max_frequency_entity(self,possibilities):

		l=[(entity,list(self.entity_match.values()).count(entity)) for entity in possibilities]

		if(len(l)!=0):
			return max(l,key=lambda x:x[1])[0]
		else:
			return None

	def create_entity(self,index,name):
		gender= self.find_gender(name)
		new_entity = Entity(name, gender)
		self.entity_set.add(new_entity)
		self.entity_match[index]=name

	def resolve(self):

		human_name_list = [(index,HumanName(name)) for index,name in enumerate(self.name_list)]
		# HumanName returns an HumanName object which splits a given name into (title,first,last,middle,suffix,nickname)
		
		temp_list=[]

		empty_entity = Entity(HumanName("NONE"))

		for index,name in human_name_list:
			if (name.first=='' and name.last==''):
				self.entity_match[index]="None"
			else:
				temp_list.append((index,name))

		human_name_list=temp_list

		#Co-ref 1 : title, first and last
		temp_list=[]

		for index,name in tqdm(human_name_list):
			if name.title !='' and name.first!='' and name.last!='':
				try:
					mapped_entity=[entity for entity in self.entity_set if name.first==entity.name.first and name.last==entity.name.last][0]

					self.entity_match[index] = mapped_entity.name
				except IndexError:
					self.create_entity(index,name)

			else:
				temp_list.append((index,name))

		human_name_list = temp_list

		#Coref-2 : first,last
		temp_list=[]
		for index,name in tqdm(human_name_list):
			if name.first!='' and name.last!='':
				try:
					mapped_entity=[entity for entity in self.entity_set if name.first==entity.name.first and name.last==entity.name.last][0]

					self.entity_match[index] = mapped_entity.name
				except IndexError:
					self.create_entity(index,name)
			else:
				temp_list.append((index,name))

		human_name_list = temp_list


		#Co-ref 3 : title, first
		temp_list=[]
		for index,name in tqdm(human_name_list):
			if name.title !='' and name.first !='':
				possibilities=[]
				
				for entity in self.entity_set:
					if entity.name.first == name.first:
						name_gender = self.find_gender(name)
						if name_gender == 3 or entity.gender==name_gender:
							possibilities.append(entity)

				mapped_entity = self.max_frequency_entity(possibilities)

				if mapped_entity is None:
					self.create_entity(index,name)
				else:
					self.entity_match[index] = mapped_entity.name
			else:
				temp_list.append((index,name))

		human_name_list = temp_list

		# Co-ref 4: title, last

		temp_list=[]
		for index,name in tqdm(human_name_list):
			if name.title !='' and name.last !='':
				possibilities=[]
				
				for entity in self.entity_set:
					if entity.name.last == name.last:
						name_gender = self.find_gender(name)
						if name_gender == 3 or entity.gender==name_gender:
							possibilities.append(entity)

				mapped_entity = self.max_frequency_entity(possibilities)

				if mapped_entity is None:
					#print("#4")
					self.create_entity(index,name)
				else:
					#print("#4")
					self.entity_match[index] = mapped_entity.name
			else:
				temp_list.append((index,name))

		human_name_list = temp_list

		#Co-ref 5 : either first or last only

		for index,name in tqdm(human_name_list):
			possibilities=[]
			if name.first =='':
				possibilities= [entity for entity in self.entity_set 
								if entity.name.last==name.last or entity.name.first==name.last]

			elif name.last =='':
				possibilities= [entity for entity in self.entity_set 
								if entity.name.first==name.first or entity.name.last==name.first]

			mapped_entity = self.max_frequency_entity(possibilities)

			if mapped_entity is None:
				#print("#5", possibilities)
				self.create_entity(index,name)
			else:
				#print("#5",possibilities)
				self.entity_match[index] = mapped_entity.name

		print("---------------------------------------------------------------------")
		print("  Entities : \n")
		for i in self.entity_set:
			print(i.name)
		print("---------------------------------------------------------------------")

		
		return self.entity_match

class EntitiesExtractor():

	def __init__(self,path):
		self.bert_ner=Ner(path)

	@staticmethod
	def split_batches(text,size):

		l=text.split(" ")
		for i in range(len(text) // size):
			yield " ".join(l[i * size : (i+1) * size])
		if (len(text) % size) != 0:
			yield ' '.join(l[(len(l)//size) * size])

	def from_text(self,text,chapter,position):

		tokens=[]

		for batch in tqdm(list(EntitiesExtractor.split_batches(text,200)),desc='bar_text'):
				tokens += self.bert_ner.predict(batch)

		#print(tokens) 
		# each token is of form => dict(word,tag,confidence)
		# return tokens,len(tokens)

		per_list=[]

		i=0
		while i<len(tokens):
			if tokens[i]['tag'] != 'B-PER':
				i+=1
			else:
				pos = position + i
				character_name = tokens[i]['word']
				i+=1
				while i< len(tokens) and tokens[i]['tag']=='I-PER':
					# if tokens[i]['word'] !='s'
					character_name += ' '+ tokens[i]['word']
					i+=1
				per_list.append({'character_name':character_name,'position':pos,'chapter':chapter})

		# print(per_list,i)
		return per_list,i


	def from_chapter_folder(self,path):
		chapter_list = sorted(os.listdir(path),reverse=False)
		print("chapter_list: ",chapter_list,"\n")

		NER_list=[]
		position=0
		for i, chapter in tqdm(list(enumerate(chapter_list)), desc='Advance progression'):
			with open(path + chapter) as f:
				text = f.read()
				chapter_NER_list, no_tokens = self.from_text(text, i, position)

				position += no_tokens
				NER_list += chapter_NER_list

			print(i,chapter,position,"\n")
		return NER_list

	def coreferences(self,NER_list):
		l=[occurence['character_name'] for occurence in NER_list]
		coref=Coreferences(l)
		entity_match=coref.resolve()

		# print(len(NER_list),len(entity_match))
		# print("entity_match: ",entity_match)

		occurence_list = [{'name':NER_list[i]['character_name'], 'position': NER_list[i]['position'],
							'chapter':NER_list[i]['chapter'],
							'entity': str(entity_match[i]).upper()}
							for i in range(len(NER_list))]

		return occurence_list

def pre_processing(text):
	print("\n SPLITTING INTO CHAPTERS")
	#filename='books/' + book_name + '.txt'

	literature=Literature(text)

	print("\n EXTRACTING ENTITIES")
	entities_extractor = EntitiesExtractor(path='models/bert_ner_base/')

	NER_list = entities_extractor.from_chapter_folder(path= 'ip_chapters/')
	pickle.dump(NER_list,open('dump_files/ip.pkl','wb'))

	# NER_list=pickle.load(open('dump_files/'+book_name+'.pkl','rb'))

	print("\n \n RESOLVING COREFERENCES")
	occurence_list = entities_extractor.coreferences(NER_list)
	pickle.dump(occurence_list, open('dump_files/ip_occ.pkl', 'wb'))

	print("---------------------------------------------------------------------")
	print("\n Occurence list: ")

	for i in occurence_list:
		print(i)
	print(len(occurence_list))
	print("---------------------------------------------------------------------")

class NodeType():
	ENTITY=2
	OCCURENCE = 1
	CHAPTER = 3

	def __str__(self):
		if self == NodeType.OCCURENCE:
			return "occurence_node"
		if self == NodeType.ENTITY:
			return "entity_node"
		if self == NodeType.CHAPTER:
			return "chapter_node"

class EdgeType():
	TIME = 1
	IS_ENTITY = 2
	BELONG_TO = 3
	INTERACT_WITH = 4

	def __str__(self):
		if self == EdgeType.TIME:
			return "time_edge"
		if self == EdgeType.IS_ENTITY:
			return "is_entity_edge"
		if self == EdgeType.BELONG_TO:
			return "belong_to_edge"
		if self == EdgeType.INTERACT_WITH:
			return "interact_with"

class graphs():

	def __init__(self,text,window_size):
		self.book_name = 'ip.txt'
		self.full_graph = nx.Graph()
		self.entity_graph = nx.Graph()
		self.window_size = window_size
		self.entity_nodes = set()
		self.occurence_list = pickle.load(open('dump_files/ip_occ.pkl','rb'))
		self.create_full_graph()

	def create_full_graph(self):

		# self.temp = set((i['name'],i['position'],i['chapter']) for i in self.occurence_list)
		# print("temp",self.temp)

		self.occurence_nodes = set((i['name'],i['position']) for i in self.occurence_list)
		#print("\nself_occurence_node",self.occurence_nodes)

		for node in self.occurence_nodes:
			self.full_graph.add_node(node,type=NodeType.OCCURENCE)

		self.chapter_nodes = set(occurence['chapter'] for occurence in self.occurence_list)
		for node in self.chapter_nodes:
			self.full_graph.add_node(node,type=NodeType.CHAPTER)

		self.entity_nodes = set(occurence['entity'] for occurence in self.occurence_list)
		#print("self_entity_nodes",self.entity_nodes)

		for node in self.entity_nodes:
			self.full_graph.add_node(node, type =NodeType.ENTITY)

		for occurence in self.occurence_list:
			self.full_graph.add_edge((occurence['name'],occurence['position']),(occurence['entity']),type=EdgeType.IS_ENTITY)
			self.full_graph.add_edge((occurence['name'],occurence['position']),(occurence['chapter']),type=EdgeType.BELONG_TO)

		
		for entity_node in self.entity_nodes:
			l_occ_nodes = self.full_graph.neighbors(entity_node)
			#print("L_occ_nodes",l_occ_nodes)
			occ_sort_pos = sorted(l_occ_nodes,key = lambda x : x[1])
			for i in range(len(occ_sort_pos)-1):
				self.full_graph.add_edge(occ_sort_pos[i],occ_sort_pos[i+1],type=EdgeType.TIME)
		
		occ_sort_pos = sorted(list(self.occurence_nodes), key=lambda x:x[1])
		#print("\nocc_sort_pos",occ_sort_pos)

		for i in tqdm(range(len(occ_sort_pos)),desc='Full graph'):
			j = i+1
			current_position = occ_sort_pos[i][1]
			while j < len(occ_sort_pos) and (occ_sort_pos[j][1] - current_position < self.window_size):
				#print(i,j,current_position)
				self.full_graph.add_edge(occ_sort_pos[i],occ_sort_pos[j],type=EdgeType.INTERACT_WITH)
				j+=1

		pickle.dump(self.full_graph, open('dump_files/'+self.book_name+'_full_graph.pkl','wb'))
		plt.figure(figsize=(13,13))
		nx.draw(self.full_graph,with_labels=True,node_size=10, font_size=8)
		plt.savefig("full.png")

		#nx.draw(self.full_graph,with_labels=True,font_weight='bold')
		#plt.savefig("full.png")

		return self.full_graph

	def char_importance(self):

		degree = nx.degree_centrality(self.entity_graph)
		#print("degree:\n",degree)

		entity_imp = list(dict(sorted(degree.items(), key = lambda kv:(kv[1]), reverse=True)).keys())

		print("\nThe five most important characters of the novel based on degree of centrality are : ")
		print(entity_imp[:5])

	#@staticmethod
	def entity_interaction_graph(self, entities, img_name):
		for i in range(len(entities)):
			entities[i]=entities[i].upper()
			#print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   ', entities[i])
		nodes = [node for node,data in self.full_graph.nodes(data=True) if data["type"]==NodeType.ENTITY ]
		#nodes = [node for node,data in self.full_graph.nodes(data=True)]

		for entity in nodes:
			if [entity][0] in entities:
				print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$   ',str([entity]))
				self.entity_graph.add_node(entity,label=str([entity]))

		for i,j in tqdm(list(product(nodes,nodes)),desc='Entity_graph'):
			if i!=j and ([i][0] in entities) and ([j][0] in entities):
				no_inter = len(list(nx.all_simple_paths(self.full_graph,source=i,target=j,cutoff=3)))
				#print(i,j,no_inter)
				if no_inter > 0:
					self.entity_graph.add_edge(i,j,weight = no_inter, label = str(EdgeType.INTERACT_WITH))

		#nx.write_gexf(self.entity_graph, "graphs/"+self.book_name+".gexf", prettyprint=True)
		#nx.draw(self.entity_graph,with_labels=True,font_weight='bold')
		#plt.savefig("entity_interaction.png")
		plt.figure(figsize=(13,13))
		nx.draw(self.entity_graph,with_labels=True,node_size=10, font_size=8)
		plt.savefig("static/"+img_name)
'''
if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--book", type=str)
	args = parser.parse_args()
	pre_processing(args.book)
	graph_obj = graphs(args.book, 500)
	graph_obj.entity_interaction_graph()
	graph_obj.char_importance()
'''
