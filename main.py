from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json

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

# Charger les données JSON avec encodage UTF-8
with open("test_api.json", "r", encoding="utf-8") as f:
    data = json.load(f)

app = FastAPI()

#Route pour obtenir tous les livres
@app.get("/books", response_model=List[Book])
def get_books():
    return data

@app.get("/books/{title}", response_model=Book)
def get_book_by_title(title: str):
    for book in data:
        if book['title'].lower() == title.lower():
            # Si 'additional_info' existe et est un dictionnaire, on le convertit en objet AdditionalInfo
            if 'additional_info' in book and isinstance(book['additional_info'], dict):
                book['additional_info'] = AdditionalInfo(**book['additional_info'])
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/isbn10/{isbn10}", response_model=Book)
def get_book_by_isbn10(isbn10: str):
    for book_data in data:
        additional_info = book_data.get('additional_info')
        if additional_info and additional_info.get('isbn10') == isbn10:
            book = Book(**book_data)
            return book
    raise HTTPException(status_code=404, detail="Book with ISBN-10 not found")

@app.get("/books/isbn13/{isbn13}", response_model=Book)
def get_book_by_isbn13(isbn13: str):
    for book_data in data:
        additional_info = book_data.get('additional_info')
        if additional_info and additional_info.get('isbn13') == isbn13:
            book = Book(**book_data)
            return book
    raise HTTPException(status_code=404, detail="Book with ISBN-13 not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
