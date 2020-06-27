import json


ignore_categories = []
include_materials = ["planks","log","Wooden Pickaxe","Stick","Iron Ingot","Iron Pickaxe","Coal","Torch",]

def mapping(x):
	if "dye" in x.lower():
		return "dye"
	elif "arrow of" in x.lower():
		return "enchanted arrow"
	elif "oxide" in x.lower():
		return ("oxide")
	elif "quartz" in x.lower():
		return "quartz"
	elif "powder" in x.lower():
		return "powder"
	elif "nether" in x.lower():
		return "nether"
	elif "log" in x.lower():
		return "log"
	elif "planks" in x.lower():
		return "planks"
	else: return x

if __name__ == "__main__":

	with open("crafting_data_all.json","r") as json_file:
		crafting_data = json.load(json_file)

	filtered_crafting_data = {}

	for k,info in crafting_data.items():
		k = mapping(k)

		if info["type"].lower() in ignore_categories:
			filter_materials.add(k)
			continue

		for r,recipe in enumerate(info["ingredients"]) :
			for v,values in enumerate(recipe):
				for o,options in enumerate(values):
					info["ingredients"][r][v][o] = mapping(info["ingredients"][r][v][o])


		clean_ingredients = []

		for recipe in info["ingredients"]:
			skip_ingred = False
			for check_ingred in clean_ingredients:
				if recipe == check_ingred:
					skip_ingred = True
					break
			if not skip_ingred:
				clean_ingredients.append(recipe)
				
		filtered_crafting_data[k] = info
		filtered_crafting_data[k]["ingredients"] = clean_ingredients

	for x in range(5):

		for k,info in list(filtered_crafting_data.items()):
			if k not in include_materials or len(info["ingredients"]) == 0:
				del filtered_crafting_data[k]
			else:	
				remove_recipe = False

				for r,_ in enumerate(info["ingredients"]) :
					for v,_ in enumerate(info["ingredients"][r]):
						if info["ingredients"][r][v] == '': continue
						for o,_ in enumerate(info["ingredients"][r][v]):
							if not info["ingredients"][r][v][o] in include_materials: #filter_materials:
								 info["ingredients"][r][v].remove(info["ingredients"][r][v][o])
								 if len(info["ingredients"][r][v]) == 0:
								 	remove_recipe = True
					if remove_recipe:
						del info["ingredients"][r]
				if len(info["ingredients"]) == 0:
					del filtered_crafting_data[k]

	with open("filtered_crafting_data_all.json","w+") as json_file:
		json.dump(filtered_crafting_data,json_file)