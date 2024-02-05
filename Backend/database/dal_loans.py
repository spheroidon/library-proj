from sqlalchemy.orm import Session
from database.models import Loans

class LoanDAL:
    def __init__(self, session: Session):
        self.session = session

    def add_loan(self, cust_id, book_id, loan_date, return_date):
        loan = Loans(cust_id=cust_id, book_id=book_id, loan_date=loan_date, return_date=return_date)
        self.session.add(loan)
        self.session.commit()
        return loan

    def get_all_loans(self):
        return self.session.query(Loans).all()

    def get_loan_by_id(self, id):
        return self.session.query(Loans).filter_by(id=id).first()
    
    def set_return_date(self, id, return_date):
        loan = self.session.query(Loans).filter_by(id=id).first()
        loan.return_date = return_date
        self.session.commit()
        return loan
    
    def is_book_loaned(self, id):
        loan = self.session.query(Loans).filter_by(book_id=id, return_date=None).first()
        return loan is not None
