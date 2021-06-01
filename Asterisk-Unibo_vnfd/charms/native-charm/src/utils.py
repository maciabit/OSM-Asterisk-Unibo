import yaml

dict_file = [{'sports': ['soccer', 'football', 'basketball', 'cricket', 'hockey', 'table tennis']},
             {'countries': ['Pakistan', 'USA', 'India', 'China', 'Germany', 'France', 'Spain']}]


def write(filename: str):
	with open(filename, "a") as file_object:
		yaml.dump(dict_file, file_object, default_flow_style=False)
		file_object.write("\n")
