from datetime import date
from database.dal_books import BookDAL
from database.dal_loans import LoanDAL
from database.dal_customers import CustomerDAL
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine('sqlite:///db.sqlite3', echo=False)
Session = sessionmaker(bind=engine)
loan_dal = LoanDAL(Session())

loan_dal.add_loan(1,1, date.today() - relativedelta(years=3),None)