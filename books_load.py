import json
from pymongo import MongoClient

#Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["nom_de_votre_base_de_donnees"]
collection = db["nom_de_votre_collection"]

#Chemin vers le fichier JSON
with open("chemin de mon fichier") as file:
    file_data = json.load(file)

#Si le fichier contient une liste de documents
if isinstance(file_data, list):
    collection.insert_many(file_data)
else:
    collection.insert_one(file_data)


print("Les données ont été importées avec succès dans MongoDB !")

