import json

# Loads a json file in a dictionnary and returns it
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)
