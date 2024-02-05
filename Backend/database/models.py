from datetime import date, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import func

Base = declarative_base()

class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    year_published = Column(Integer)
    book_type = Column(Integer) # One: up to 10 days, Two: up to 5 days, Three: up to 2 days
    removed = Column(Boolean)
    loans = relationship('Loans', back_populates='book')

class Customers(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    city = Column(String)
    age = Column(Integer)
    removed = Column(Boolean)
    loans = relationship('Loans', back_populates='customer')

class Loans(Base):
    __tablename__ = 'loans'
    id = Column(Integer, primary_key=True)
    cust_id = Column(Integer, ForeignKey('customers.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    loan_date = Column(Date)
    return_date = Column(Date)
    customer = relationship('Customers', back_populates='loans')
    book = relationship('Books', back_populates='loans')

    def is_late(self):
        if self.loan_date is not None:
            # Calculate the difference between the return_date and today's date
            days_difference = (date.today() - self.loan_date).days

            # Check if the difference exceeds the allowed days based on book_type
            if self.book.book_type == 1 and days_difference > 10:
                return True
            elif self.book.book_type == 2 and days_difference > 5:
                return True
            elif self.book.book_type == 3 and days_difference > 2:
                return True

        return False

engine = create_engine('sqlite:///db.sqlite3')
Base.metadata.create_all(bind=engine)