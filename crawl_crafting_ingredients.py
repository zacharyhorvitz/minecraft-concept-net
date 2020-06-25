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

def get_crafting_data(url,use_print=False):

	recipes = []
	category = url.split("/")[-1]

	driver.get(url)
	table = driver.find_element_by_css_selector("table") 
	tr_all = table.find_elements_by_css_selector("tr")


	for tr in tr_all:

		crafting = tr.find_elements_by_css_selector("span.invslot")
		bench = []
		for invslot in crafting:
			slot = invslot.get_attribute("innerHTML")
			titles = re.findall(r'title="(.*?)"', slot)

			if len(titles) == 0:
				bench.append('')
			else:
				bench.append(titles[0])

		if len(bench) == 0: continue

		recipes.append((bench[:-1],bench[-1],category))

		if use_print:
			print(bench[:-1],"--->",bench[-1],category)

	return recipes


if __name__ == "__main__":

	all_urls = get_all_urls()
	print(all_urls)
	all_recipes = []

	for u in all_urls:
		all_recipes.extend(get_crafting_data(u))

	print("Recipes:", len(all_recipes))

	item_to_data = {}
	for r in all_recipes:
		name = r[1]
		ingredients = r[0]
		category=r[2]

		if name not in item_to_data:
			item_to_data[name] = {"ingredients":[],"type":category}

		item_to_data[name]["ingredients"].append(ingredients)

	with open("crafting_data.json","w+") as json_file:
		json.dump(item_to_data,json_file)




