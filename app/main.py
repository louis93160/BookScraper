from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient

class AdditionalInfo(BaseModel):
    editeur: Optional[str] = None
    langue: Optional[str] = None
    nbpage: Optional[str] = None
    isbn10: Optional[str] = None
    isbn13: Optional[str] = None
    poids_article: Optional[str] = None
    dimensions: Optional[str] = None

class CustomerReview(BaseModel):
    title: str
    text: str
    author: str
    date: str

class Book(BaseModel):
    title: str
    price: str
    rating: str
    reviews: str
    author: str
    image_url: str
    book_url: str
    additional_info: Optional[AdditionalInfo] = None
    customer_reviews: Optional[List[CustomerReview]] = []

#Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Books_database"]
collection = db["Books"]

app = FastAPI()

# Endpoints pour obtenir tous les livres
@app.get("/books", response_model=List[Book])
def get_books():
    books = list(collection.find({}, {"_id": 0}))  # Récupère tous les documents en excluant l'ID MongoDB
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return books

# Endpoints pour obtenir un livre par son titre
@app.get("/books/{title}", response_model=Book)
def get_book_by_title(title: str):
    book = collection.find_one({"title": title}, {"_id": 0})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Endpoints pour obtenir un livre par son ISBN10
@app.get("/books/isbn10/{isbn10}", response_model=Book)
def get_book_by_isbn10(isbn10: str):
    book = collection.find_one({"additional_info.isbn10": isbn10}, {"_id": 0})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Endpoints pour obtenir un livre par son ISBN13
@app.get("/books/isbn13/{isbn13}", response_model=Book)
def get_book_by_isbn13(isbn13: str):
    book = collection.find_one({"additional_info.isbn13": isbn13}, {"_id": 0})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
