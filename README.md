# minecraft-concept-net
Relational information extracted from Minecraft wiki-sources, A Minecraft Conceptnet


**crafting_data** is a json of the form:
<pre>
<code>"Wooden Pickaxe": {
"ingredients": [
["Oak Planks", "Oak Planks", "Oak Planks", "", "Stick", "", "", "Stick", ""],
["", "", "", "Wooden Pickaxe", "Wooden Pickaxe", "", "", "", ""]],
"type": "Tools"}</code></pre>

Where each ingredient element corresponds to a crafting slot.


#TODO:
- Include crafting info for all animated Inv-Slots
- Include hierarchy for different types of pickaxe?
- Include Edges going from tools to materials they can be used for (from each block page)
