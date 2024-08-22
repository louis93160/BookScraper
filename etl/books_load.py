import json
from pymongo import MongoClient

#Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Books_database"]
collection = db["Books"]

#Chemin vers le fichier JSON
with open("/home/louis/BookScraper/data/books_modifier.json") as file:
    file_data = json.load(file)

#Si le fichier contient une liste de documents
if isinstance(file_data, list):
    collection.insert_many(file_data)
else:
    collection.insert_one(file_data)


print("Les données ont été importées avec succès dans MongoDB !")

