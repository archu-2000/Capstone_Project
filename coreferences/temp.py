
with open("female_title.txt", 'r') as f:
	list_of_rules = f.read().splitlines()
l= [rule.lower() for rule in list_of_rules]
print(l)