
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

	filename = "diamond.json"

	G=nx.DiGraph()


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
					edge_labels[(ingred,item)] = relation




# # adding just one node:
# G.add_node("a")
# # a list of nodes:
# G.add_nodes_from(["b","c"])

# print("Nodes of graph: ")
# print(G.nodes())
# print("Edges of graph: ")
# print(G.edges())
	pos = nx.spring_layout(G)
	nx.draw(G,pos,edge_color='black',with_labels=True)


	nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels,font_color='red',with_labels=True)

	plt.savefig("diamond_dependencies.png") # save as png
	plt.show() # display

# with open(goal_items+".json","w+") as json_file:
# 		json.dump(item_to_data,json_file)



