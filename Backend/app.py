from datetime import datetime
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from database.dal_books import BookDAL
from database.dal_loans import LoanDAL
from database.dal_customers import CustomerDAL
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from database.models import Base, Customers

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Set up SQLite database
engine = create_engine('sqlite:///db.sqlite3', echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# Create DAL instance
customer_dal = CustomerDAL(Session())
book_dal = BookDAL(Session())
loan_dal = LoanDAL(Session())

@app.route('/remove-account', methods=['POST'])
@jwt_required()
def remove_customer():
    id = get_jwt_identity()
    customer_dal.remove_customer(id=id)

    return jsonify({'message': 'User removed successfully'}), 201


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    city = data.get('city')
    age = data.get('age')
    password = data.get('password')

    if not name or not city or not age or not password:
        return jsonify({'message': 'Incomplete data'}), 400

    hashed_password = bcrypt.generate_password_hash(password)

    # Check if the user with the same name already exists
    existing_user = customer_dal.get_customer_by_name(name)
    if existing_user:
        return jsonify({'message': 'User with this name already exists'}), 400

    # Add the new user to the database
    customer_dal.add_customer(name=name, password=hashed_password, city=city, age=age, removed=False)

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({'message': 'Incomplete data'}), 400

    # Check if the user with the given name exists
    customer = customer_dal.get_customer_by_name(name)

    if not customer or customer.removed or not bcrypt.check_password_hash(customer.password, password):
        return jsonify({"message': 'Invalid credentials or account doesn't exist"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=customer.id)
    return jsonify(access_token=access_token), 200

@app.route('/books', methods=['GET','POST'])
@jwt_required(optional=True)
def books_info():
    method = request.method
    identity = get_jwt_identity()

    if method == 'GET':
        books = [{'id': book.id, 'title': book.title, 'author': book.author, 'year_published': book.year_published, 'book_type': book.book_type, 'is_loaned': loan_dal.is_book_loaned(id=book.id)} if not book.removed else None for book in book_dal.get_all_books()]
        return jsonify(books), 200
    elif method == 'POST':
        if identity == None:
            return jsonify({'message': 'An account is required to use this method'}), 401
        
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        year_published = data.get('year_published')
        book_type = data.get('book_type')

        if not title or not author or not year_published or not book_type:
            return jsonify({'message': 'Incomplete data'}), 400
        
        try:
            if int(book_type) < 1 or int(book_type) > 3:
                return jsonify({'message': 'Book Type must be either 1, 2 or 3'}), 400
        except:
            return jsonify({'message': 'Book Type must be either 1, 2 or 3'}), 400
        
        book_dal.add_book(title=title,author=author,year_published=year_published,book_type=book_type,removed=False)
        return jsonify({'message': 'Book added successfuly'}), 201

@app.route('/books/<int:id>', methods=['GET','POST','DELETE'])
@jwt_required(optional=True)
def book_info(id):
    method = request.method
    identity = get_jwt_identity()

    if method == 'GET':
        book = book_dal.get_book_by_id(id=id)
        is_loaned = loan_dal.is_book_loaned(id=id)
        return jsonify({'id': book.id, 'title': book.title, 'author': book.author, 'year_published': book.year_published, 'book_type': book.book_type, 'is_loaned': is_loaned}), 200
    elif method == 'POST':
        if identity == None:
            return jsonify({'message': 'An account is required to use this method'}), 401
        
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        year_published = data.get('year_published')
        book_type = data.get('book_type')

        if not title or not author or not year_published or not book_type:
            return jsonify({'message': 'Incomplete data'}), 400
        
        try:
            if int(book_type) < 1 or int(book_type) > 3:
                return jsonify({'message': 'Book Type must be either 1, 2 or 3'}), 400
        except:
            return jsonify({'message': 'Book Type must be either 1, 2 or 3'}), 400
        
        book_dal.update_book(id=id,title=title,author=author,year_published=year_published,book_type=book_type)
        return jsonify({'message': 'Book added successfuly'}), 201
    elif method == 'DELETE':
        if identity == None:
            return jsonify({'message': 'An account is required to use this method'}), 401

        book_dal.remove_book(id=id)
        return jsonify({'message': 'Book removed successfuly'}), 201

@app.route('/search-books/<string:title>', methods=['GET'])
def book_search(title):
    method = request.method

    if method == 'GET':
        books = [{'id': book.id, 'title': book.title, 'author': book.author, 'year_published': book.year_published, 'book_type': book.book_type} if not book.removed else None for book in book_dal.get_all_books_by_name(name=title)]
        return jsonify(books), 200

@app.route('/customers', methods=['GET'])
def customers_info():
    method = request.method

    if method == 'GET':
        customers = [{'id': customer.id, 'name': customer.name, 'city': customer.city, 'age': customer.age} if not customer.removed else None for customer in customer_dal.get_all_customers()]
        return jsonify(customers), 200

@app.route('/customers/<int:id>', methods=['GET'])
def customer_info(id):
    method = request.method

    if method == 'GET':
        customer = customer_dal.get_customer_by_id(id=id)
        return jsonify({'id': customer.id, 'name': customer.name, 'city': customer.city, 'age': customer.age}), 200

@app.route('/search-customers/<string:name>', methods=['GET'])
def customer_search(name):
    method = request.method

    if method == 'GET':
        customers = [{'id': customer.id, 'name': customer.name, 'city': customer.city, 'age': customer.age} if not customer.removed else None for customer in customer_dal.get_all_customers_by_name(name=name)]
        return jsonify(customers), 200

@app.route('/loans', methods=['GET','POST'])
@jwt_required(optional=True)
def loans_info():
    method = request.method
    identity = get_jwt_identity()

    if method == 'GET':
        loans = [{'id': loan.id, 'cust_id': loan.cust_id, 'book_id': loan.book_id, 'loan_date': loan.loan_date, 'return_date': loan.return_date, 'cust_name': loan.customer.name, 'book_title': loan.book.title} for loan in loan_dal.get_all_loans()]
        return jsonify(loans), 200
    elif method == 'POST':
        if identity == None:
            return jsonify({'message': 'An account is required to use this method'}), 401
        
        data = request.get_json()
        cust_id = identity
        book_id = data.get('book_id')

        if not cust_id or not book_id:
            return jsonify({'message': 'Incomplete data'}), 400
                
        loan_dal.add_loan(cust_id=cust_id,book_id=book_id,loan_date=datetime.now(),return_date=None)
        return jsonify({'message': 'Loan added successfuly'}), 201

@app.route('/loans/<int:id>', methods=['GET','POST'])
@jwt_required(optional=True)
def loan_info(id):
    method = request.method
    identity = get_jwt_identity()

    if method == 'GET':
        loan = loan_dal.get_loan_by_id(id=id)
        return jsonify({'id': loan.id, 'cust_id': loan.cust_id, 'book_id': loan.book_id, 'cust_name': loan.customer.name, 'book_title': loan.book.title, 'loan_date': loan.loan_date, 'return_date': loan.return_date}), 200
    elif method == 'POST':
        if identity == None:
            return jsonify({'message': 'An account is required to use this method'}), 401
        
        if identity != loan_dal.get_loan_by_id(id=id).cust_id:
            return jsonify({'message': 'Unauthorized'}), 401
        
        loan_dal.set_return_date(id=id,return_date=datetime.now())
        return jsonify({'message': 'Loan returned successfuly'}), 201

@app.route('/late-loans', methods=['GET'])
def late_loans():
    method = request.method

    if method == 'GET':
        loans = [{'id': loan.id, 'cust_id': loan.cust_id, 'book_id': loan.book_id, 'loan_date': loan.loan_date, 'return_date': loan.return_date, 'cust_name': loan.customer.name, 'book_title': loan.book.title} if loan.is_late() else None for loan in loan_dal.get_all_loans()]
        return jsonify(loans), 200


if __name__ == '__main__':
    app.run(debug=True,port=5001)
