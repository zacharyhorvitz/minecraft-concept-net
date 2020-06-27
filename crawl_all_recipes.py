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
import re

import selenium

from selenium import webdriver

driver = webdriver.PhantomJS()

def requester(url):
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,} 

	request=urllib.request.Request(url,None,headers) #The assembled request
	response = urllib.request.urlopen(request)
	data = response.read() # The data u need
	soup = BeautifulSoup(data, 'lxml')

	return soup


def get_all_urls(url = 'https://minecraft.gamepedia.com/Crafting'):

	soup = requester(url)
	divs = soup.findAll('div',{"class":"load-page-content"}) #attrs={"data-description":"Crafting recipes"})
	all_urls = []

	for d in divs:
		links = d.findAll('a')

		for a in links:
			if "http" not in a['href']: all_urls.append('https://minecraft.gamepedia.com'+a['href']) #Only grab relative paths

	return all_urls


def process_invitem(invitem):
	slot = invitem.get_attribute("innerHTML")
	titles = re.findall(r'title="(.*?)"', slot)
	if len(titles) == 0:
		return ''
	else:
		return titles[0]

def get_crafting_data(url,use_print=False):

	recipes = []
	category = url.split("/")[-1]

	driver.get(url)
	table = driver.find_element_by_css_selector("table") 
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

		recipes.append((bench[:-1],bench[-1],category))

		if use_print:
			print(bench[:-1],"--->",bench[-1],category)

	return recipes

def extract_recipe_options(recipe):
	all_ingredients = recipe[0]
	outputs = recipe[1]
	category = recipe[2]

	options = []

	for i,output in enumerate(outputs):
		print(output[0])

		ingredients = []

		try:

			for ingred in all_ingredients:
				if len(ingred) == 0:
					ingredients.append('')
				elif len(ingred) == 1:
					ingredients.append(ingred[0])
				else:
					ingredients.append(ingred[i])

			options.append((output[0],category,ingredients))

		except IndexError:
			print("SKIPPED")
			print(all_ingredients)
			continue


	return options




if __name__ == "__main__":

	all_urls = get_all_urls()
	print(all_urls)
	all_recipes = []

	for u in all_urls:
		all_recipes.extend(get_crafting_data(u,use_print=True))

	all_recipes_expanded = []
	for r in all_recipes:
		all_recipes_expanded.extend(extract_recipe_options(r))

	print("Recipes:", len(all_recipes_expanded))

	item_to_data = {}
	for r in all_recipes_expanded:
		name = r[0]
		ingredients = r[2]
		category=r[1]

		if name not in item_to_data:
			item_to_data[name] = {"ingredients":[],"type":category}

		item_to_data[name]["ingredients"].append(ingredients)



	with open("crafting_data_all.json","w+") as json_file:
		json.dump(item_to_data,json_file)




