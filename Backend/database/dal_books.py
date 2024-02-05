from sqlalchemy.orm import Session
from database.models import Books

class BookDAL:
    def __init__(self, session: Session):
        self.session = session

    def add_book(self, title, author, year_published, book_type, removed):
        book = Books(title=title, author=author, year_published=year_published, book_type=book_type, removed=removed)
        self.session.add(book)
        self.session.commit()
        return book
    
    def remove_book(self, id):
        book = self.session.query(Books).filter_by(id=id).first()
        book.removed = True
        self.session.commit()
        return book
    
    def update_book(self, id, title, author, year_published, book_type):
        book = self.session.query(Books).filter_by(id=id).first()
        book.title = title
        book.author = author
        book.year_published = year_published
        book.book_type = book_type
        self.session.commit()
        return book

    def get_all_books_by_name(self, name):
        return self.session.query(Books).filter(Books.title.like(f"%{name}%")).all()
    
    def get_all_books(self):
        return self.session.query(Books).all()

    def get_book_by_name(self, name):
        return self.session.query(Books).filter_by(name=name).first()
    
    def get_book_by_id(self, id):
        return self.session.query(Books).filter_by(id=id).first()