import urllib.request
import urllib.error
from lxml import etree
import numpy as np
import requests
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import random
from tqdm import tqdm
import unicodedata
import nltk.data
import re

import sys

import selenium

from selenium import webdriver

driver = webdriver.PhantomJS()
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def get_crafting_data(table,category,operation,mapping,use_print=False):

	recipes = []
	tr_all = table.find_elements_by_css_selector("tr")

	# counter = 0
	for tr in tr_all:
		# counter += 1
		# if counter > 5: return recipes

		crafting = tr.find_elements_by_css_selector("span.invslot")
		bench = []
	
		for invslot in crafting:
			frame_data = []

			possible_values = invslot.find_elements_by_xpath("*")

			for options in possible_values:
				if 	"animated-subframe" in options.get_attribute("class"):
					frames = options.find_elements_by_css_selector('span.invslot-item')
					frame_data.append([process_invitem(f) for f in frames])
				else:
					frame_data.append([process_invitem(options)])

			bench.append(frame_data)

		if len(bench) == 0: continue
		skip = True
		for output in bench[-1]:
			# print(output,category)
			if category == mappings(output[0]):
				skip = False
				break
		if operation == "Smelting":
			bench = [bench[0],bench[2]]


		bench = [x for x in bench if x != '']

		if not skip:
			recipes.append([bench[:-1],bench[-1],operation])

			if use_print:
				print(bench[:-1],"--->",bench[-1],operation)

	return recipes


def process_invitem(invitem):
	slot = invitem.get_attribute("innerHTML")
	titles = re.findall(r'title="(.*?)"', slot)
	if len(titles) == 0:
		return ''
	else:
		return titles[0]

def get_dependencies(url,mappings):

	recipes = []
	category = url.split("/")[-1]
	# print(category)
	driver.get(url)

	if 'class="notaninfobox"' not in \
	driver.find_element_by_css_selector("body").get_attribute("innerHTML"):
		return []

	top_info = driver.find_element_by_css_selector("div.notaninfobox")

	if "is required" in top_info.get_attribute("innerHTML"):
		words = top_info.get_attribute("innerHTML").split()
		index = words.index('required')
		required_tool = " ".join(words[index-5:index-3])
		recipes.append([[[[required_tool.lower()]]],[[category]],"Required Tool"])

	for drop in set(retrieve_drop_info(url)):
		recipes.append([[[[drop.lower()]]],[[category]],"Drop"])


	tables = driver.find_elements_by_css_selector("table") 

	for table in tables:
		if 'title="Crafting"' in table.get_attribute("innerHTML"):
			recipes.extend(get_crafting_data(table,category,"Crafting",mappings,use_print=False))

		elif 'title="Smelting"' in table.get_attribute("innerHTML"):
			recipes.extend(get_crafting_data(table,category,"Smelting",mappings,use_print=False))
			
	for r,_ in enumerate(recipes):
		recipes[r][0] = appy_nested_elements(recipes[r][0],mappings)
		recipes[r][1] = appy_nested_elements(recipes[r][1],mappings)

	return recipes


def extract_recipe_options(recipe,filter_repair=True):
	# print("STARTING_RECIPE",recipe)

	all_ingredients = recipe[0]
	outputs = recipe[1]
	# category = recipe[1]
	operation = recipe[2]

	options = []

	for i,output in enumerate(outputs):
		# print(output[0])

		ingredients = []

		try:
			for ingred in all_ingredients:
				if len(ingred) == 0:
					ingredients.append('')
				elif len(ingred) == 1:
					ingredients.append(ingred[0])
				else:
					ingredients.append(list(set(ingred[i])))

			skip = False
			if filter_repair:
				for ingred in ingredients:
					if ingred == '': continue
					elif output[0] in ingred:
							skip = True 



			if not skip:
					options.append((output[0],ingredients,operation))

		except IndexError:
			print("SKIPPED")
			print(all_ingredients)
			continue


	return options

def appy_nested_elements(data,function):
	if not type(data) is str:
		for i in range(len(data)):
			data[i] = appy_nested_elements(data[i],function)
	else:
		data = function(data)
	return data


def retrieve_drop_info(url):
	key_term = url.split('/')[-1].replace('_',' ')
	driver.get(url)
	terms = []
	for p in driver.find_elements_by_css_selector('p'):
		data = p.get_attribute("innerHTML")
	
		split_sentences = sent_detector.tokenize(data)

		for x in split_sentences:
				if not ' drop ' in x and not 'obtained from' in x: continue
				if ' dropping' in x: continue

				if key_term.lower() in x.lower():
					terms += re.findall(r'title="(.*?)"', x)

	return terms


def process_dependencies(dependencies,item_to_data,mappings,exclude):
	all_urls = ['https://minecraft.gamepedia.com/' + d for d in dependencies] #get_all_urls()
	# print(all_urls)

	all_recipes = []


	for u in all_urls:
		all_recipes.extend(get_dependencies(u,mappings))
	# print(all_recipes)
	# exit()

	all_recipes_expanded = []
	for r in all_recipes:
		all_recipes_expanded.extend(extract_recipe_options(r))

	new_dependencies = []

	
	print("New Recipes:",len(all_recipes_expanded))
	# for r in all_recipes_expanded:
		# print(r)
	

	for r in all_recipes_expanded:
		name = r[0]
		ingredients = r[1]
		# category=r[1]
		operation = r[2]

		if name not in dependencies: continue

		if name in exclude: continue

		skip = False
		for i,_ in enumerate(ingredients):
			for v,_ in enumerate(ingredients[i]):
				if ingredients[i][v] in exclude:
					del ingredients[i][v]
					if len(ingredients[i]) == 0:
						skip = True
		if skip: continue

		if name not in item_to_data:
			item_to_data[name] = {"ingredients":[]}

		item_to_data[name]["ingredients"].append((ingredients,operation))

		for x in ingredients:
			# if x != '':
				new_dependencies.extend(x)

	new_dependencies = list(set(new_dependencies))

	return item_to_data,new_dependencies


if __name__ == "__main__":

	def mappings(x):
		if "Block of" in x:
			return "block"
		elif "Planks" in x:
			return "planks"
		elif "Log" in x:
			return "log"

		elif "Cave Spider" in x:
			return "spider"
		else:
			return x.lower()

	exclude = {'block','pickaxe','chest loot','blackstone','bamboo','iron nugget','shears','bamboo','dead bush','iron golem','emerald','silk touch',"fortune","looting","hoblin","mooshroom"}
	dependencies = [x.replace('_',' ') for x in sys.argv[1:]] #["Wooden Pickaxe","Wooden Shovel"]
	goal_items = "-".join(dependencies)
	processed_dependencies = set()
	item_to_data = {}


	while True:

		for d in dependencies:
			processed_dependencies.add(d)

		_,dependencies = process_dependencies(dependencies,item_to_data,mappings,exclude)

		dependencies = [mappings(d) for d in dependencies if mappings(d) not in processed_dependencies and mappings(d) not in exclude]
		print("New dependencies:",dependencies)
		print("Items:", len(list(item_to_data.keys())))

		if len(dependencies) == 0:
			break

	print(item_to_data)

	with open(goal_items+".json","w+") as json_file:
		json.dump(item_to_data,json_file)











	# with open("crafting_data_all.json","w+") as json_file:
	# 	json.dump(item_to_data,json_file)

	# all_recipes_expanded = []
	# for r in all_recipes:
	# 	all_recipes_expanded.extend(extract_recipe_options(r))

	# print("Recipes:", len(all_recipes_expanded))

	# item_to_data = {}
	# for r in all_recipes_expanded:
	# 	name = r[0]
	# 	ingredients = r[2]
	# 	category=r[1]

	# 	if name not in item_to_data:
	# 		item_to_data[name] = {"ingredients":[],"type":category}

	# 	item_to_data[name]["ingredients"].append(ingredients)



	# with open("crafting_data_all.json","w+") as json_file:
	# 	json.dump(item_to_data,json_file)




