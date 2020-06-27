
import json
import networkx as nx
import matplotlib.pyplot as plt



def get_nested_elements(data):
	if not type(data) is str:
		aggregated_results = []
		for i in range(len(data)):
			aggregated_results.extend(data[i])

		return aggregated_results
	else:
		return [data]



if __name__ == "__main__":

	filename = "data/diamond.json"

	G=nx.MultiDiGraph()


	with open(filename,"r") as json_file:
		recipes = json.load(json_file)

	edge_labels = {}

	for item in recipes.keys():
			print(item)
			for option in recipes[item]["ingredients"]:
				print(option)
				all_ingreds = option[0]
				relation = option[1]
				all_ingreds = list(set(get_nested_elements(all_ingreds)))
				for ingred in all_ingreds:

					G.add_edge(ingred,item)

					if (ingred,item) not in edge_labels:
						edge_labels[(ingred,item)] = relation
					else:
						edge_labels[(ingred,item)] =  " / ".join(list(set((edge_labels[(ingred,item)] + " / "+relation).split(' / '))))

	pos = nx.planar_layout(G)
	nx.draw(G,pos,edge_color='blue',with_labels=True)

	nx.draw_networkx_edge_labels(G,pos,edge_labels,font_color='red',with_labels=True)

	plt.savefig("data/diamond_dependencies.png") # save as png
	plt.show() # display




