import json as js

# Loads a json file in a dictionnary and returns it
def load_json(file):
    with open(file, 'r') as f:
        return js.load(f)

# Writes a dictionnary as a json in the given file
def write_json(json_dict, file):
    with open(file, 'w') as f:
        js.dump(json_dict, f)
