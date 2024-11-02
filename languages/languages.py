import json

files = [
  "./languages/en.json",
]

DEFAULT = "en"

translations = {}
languages = []
for file in files:
  with open(file, "r") as file:
    values = json.load(file)
    translations[values["code"]] = values
    languages.append(values["code"])