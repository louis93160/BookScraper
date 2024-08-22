import json
import re
import unicodedata

fichier = "books.json"


with open(fichier, "r", encoding="utf-8") as file:
    data = json.load(file)

def clean_author(author_str):
     # Retirer "de", "et", "al.", "|"
    author_str = re.sub(r'\b(de|et|al\.)\b', '', author_str)
    # Retirer le "al." en fin de chaîne (avec ou sans espace)
    author_str = re.sub(r'\s*al\.\s*$', '', author_str)
    # Retirer la date (au format "5 avril 2018" par exemple)
    author_str = re.sub(r'\|\s*\d+\s\w+\s\d{4}', '', author_str)
    # Supprimer les espaces multiples et les virgules inutiles
    author_str = re.sub(r'\s*,\s*', ', ', author_str)
    author_str = re.sub(r'\s+', ' ', author_str).strip()
    author_str = re.sub(r',\s*$', '', author_str)  # retirer les virgules à la fin
    return author_str

def remove_euro_sign(price_str):
    return price_str.replace("€", "").strip()


# Fonction pour retirer les emojis
def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticônes
        "\U0001F300-\U0001F5FF"  # Symboles et pictogrammes divers
        "\U0001F680-\U0001F6FF"  # Transport et symboles de carte
        "\U0001F1E0-\U0001F1FF"  # Drapeaux (iOS)
        "\U00002702-\U000027B0"  # Divers symboles
        "\U000024C2-\U0001F251"  # Divers symboles encore
        "\U0001F900-\U0001F9FF"  # Emoticônes supplémentaires
        "\U0001FA70-\U0001FAFF"  # Émoticônes supplémentaires
        "\U00002600-\U000026FF"  # Symboles divers
        "\U00002300-\U000023FF"  # Divers symboles techniques
        "\U00002B50-\U00002B59"  # Symboles supplémentaires
        "\U0001F1F2-\U0001F1F4"  # Drapeaux
        "\U0001F1E6-\U0001F1FF"  # Drapeaux
        "\U0001F600-\U0001F636"
        "\U0001F681-\U0001F6C5"
        "\U0001F30D-\U0001F567"
        "\u2600-\u26FF\u2700-\u27BF"
        "\U0001F191-\U0001F251"
        "\U0001F004-\U0001F0CF"
        "\U0001F170-\U0001F171"
        "\U0001F17E-\U0001F17F"
        "\U0001F18E-\U0001F18F"
        "\U0001F201-\U0001F202"
        "\U0001F21A-\U0001F21B"
        "\U0001F22F-\U0001F22F"
        "\U0001F232-\U0001F23A"
        "\U0001F250-\U0001F251"
        "\U0001F300-\U0001F320"
        "\U0001F32D-\U0001F32F"
        "\U0001F330-\U0001F335"
        "\U0001F337-\U0001F37C"
        "\U0001F37E-\U0001F393"
        "\U0001F3A0-\U0001F3CA"
        "\U0001F3CF-\U0001F3D3"
        "\U0001F3E0-\U0001F3F0"
        "\U0001F3F4-\U0001F3F4"
        "\U0001F3F8-\U0001F43E"
        "\U0001F440-\U0001F440"
        "\U0001F442-\U0001F4FC"
        "\U0001F4FF-\U0001F53D"
        "\U0001F54B-\U0001F54E"
        "\U0001F550-\U0001F567"
        "\U0001F57A-\U0001F57A"
        "\U0001F595-\U0001F596"
        "\U0001F5A4-\U0001F5A4"
        "\U0001F5FB-\U0001F5FF"
        "\U0001F600-\U0001F64F"
        "\U0001F680-\U0001F6C5"
        "\U0001F6CB-\U0001F6D2"
        "\U0001F6E0-\U0001F6E5"
        "\U0001F6EB-\U0001F6EC"
        "\U0001F6F0-\U0001F6F0"
        "\U0001F6F3-\U0001F6F8"
        "\U0001F910-\U0001F93E"
        "\U0001F940-\U0001F970"
        "\U0001F973-\U0001F976"
        "\U0001F97A-\U0001F9A2"
        "\U0001F9B0-\U0001F9B9"
        "\U0001F9C0-\U0001F9C2"
        "\U0001F9D0-\U0001F9FF"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# Fonction pour normaliser et corriger les clés de "additional_info"
def normalize_additional_info_keys(additional_info):
    corrected_info = {}
    for key, value in additional_info.items():
        # Supprimer les deux-points
        new_key = re.sub(r':', '', key).strip()
        
        # Convertir en minuscules
        new_key = new_key.lower()
        
        # Supprimer les accents
        new_key = unicodedata.normalize('NFKD', new_key).encode('ascii', 'ignore').decode('ascii')
        
        # Remplacer "broche" et "poche" par "nbpage"
        if new_key in ["broche", "poche"]:
            new_key = "nbpage"
        
        # Supprimer les tirets de "isbn-10" et "isbn-13"
        new_key = re.sub(r'[^a-z0-9]', '', new_key) if 'isbn' in new_key else new_key
        
        corrected_info[new_key] = value
    return corrected_info

# Fonction pour supprimer les sauts de ligne (\n)
def remove_newlines(text):
    return text.replace('\n', ' ').strip()

# Parcourir les données et modifier les valeurs des clés "price", "author", "additional_info", etc.
def update_data(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "price":
                obj[key] = remove_euro_sign(value)
            elif key == "author":
                obj[key] = clean_author(value)
            elif key == "additional_info":
                obj[key] = normalize_additional_info_keys(value)
            if isinstance(value, str):
                obj[key] = remove_newlines(remove_emojis(value))
            elif isinstance(value, (dict, list)):
                update_data(value)
    elif isinstance(obj, list):
        for item in obj:
            update_data(item)

# Appliquer la mise à jour sur les données
update_data(data)


with open("books_modifier.json", "w", encoding = "utf-8") as file:
    json.dump(data, file, ensure_ascii = False, indent = 4)

print("Les prix ont été mis à jour avec succès.")