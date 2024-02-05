from sqlalchemy.orm import Session
from database.models import Customers

class CustomerDAL:
    def __init__(self, session: Session):
        self.session = session

    def add_customer(self, name, password, city, age, removed):
        customer = Customers(name=name, password=password, city=city, age=age, removed=removed)
        self.session.add(customer)
        self.session.commit()
        return customer
        
    def remove_customer(self, id):
        customer = self.session.query(Customers).filter_by(id=id).first()
        customer.removed = True
        self.session.commit()
        return customer

    def get_all_customers_by_name(self, name):
        return self.session.query(Customers).filter(Customers.name.like(f"%{name}%")).all()

    def get_all_customers(self):
        return self.session.query(Customers).all()
    
    def get_customer_by_name(self, name):
        return self.session.query(Customers).filter_by(name=name).first()
    
    def get_customer_by_id(self, id):
        return self.session.query(Customers).filter_by(id=id).first()