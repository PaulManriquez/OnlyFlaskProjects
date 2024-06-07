from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from faker import Faker 
import random

app = Flask(__name__)
fake = Faker()

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True 

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)
app.app_context().push()# <--- this is important to enable the manipulation of the app.py in the linux shell. 

#====================== My Tables ====================================
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    postcode = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)

    #<------------------------ Order relationship --------------------------->
    orders = db.relationship('Order', backref='customer')

#<--- Product id and order id per custumer # assosiation table
order_product = db.Table('order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
) 

class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    shipped_date = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    coupon_code = db.Column(db.String(50))
    

    #<---------------------- ForeignKey | an order have a customer -------------------> 
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    products = db.relationship('Product', secondary=order_product)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Integer,nullable=False)



#=== Populate data =====================================================================
def add_customers():
    for _ in range(100):
        customer = Customer(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            address=fake.street_address(),
            city=fake.city(),
            postcode=fake.postcode(),
            email=fake.email()
        )
        db.session.add(customer)
    db.session.commit()

def add_orders():
    customers = Customer.query.all()

    for _ in range(1000):
        #choose a random customer
        customer = random.choice(customers)

        ordered_date = fake.date_time_this_year()
        shipped_date = random.choices([None, fake.date_time_between(start_date=ordered_date)], [10, 90])[0]

        #choose either random None or random date for delivered and shipped
        delivered_date = None
        if shipped_date:
            delivered_date = random.choices([None, fake.date_time_between(start_date=shipped_date)], [50, 50])[0]

        #choose either random None or one of three coupon codes
        coupon_code = random.choices([None, '50OFF', 'FREESHIPPING', 'BUYONEGETONE'], [80, 5, 5, 5])[0]

        order = Order(
            customer_id=customer.id,
            order_date=ordered_date,
            shipped_date=shipped_date,
            delivered_date=delivered_date,
            coupon_code=coupon_code
        )

        db.session.add(order)
    db.session.commit()

def add_products():
    for _ in range(10):
        product = Product(
            name=fake.color_name(),
            price=random.randint(10,100)
        )
        db.session.add(product)
    db.session.commit()
    
def add_order_products():
    orders = Order.query.all()
    products = Product.query.all()

    for order in orders:
        #select random k
        k = random.randint(1, 3)
        # select random products
        purchased_products = random.sample(products, k)
        order.products.extend(purchased_products)
        
    db.session.commit()

def create_random_data():
    db.create_all()
    add_customers()
    add_orders()
    add_products()
    add_order_products()

#======================== QUERY'S as a fucntions =========================
# ============================= SQL ALCHEMY ==============================    

#Function to get the orders made by a customer id 
def get_orders_by(customer_id=1):
    print('Get orders by customer')
    customer_orders = Order.query.filter_by(customer_id=customer_id).all()
    for order in customer_orders:
        print(order.order_date)

#Function to: get the orders without date and order it by date in asc
def get_pending_orders():
    print('Pending orders')
    pending_orders = Order.query.filter(Order.shipped_date.is_(None)).order_by(Order.order_date.desc()).all()
    for order in pending_orders:
        print(order.order_date)

#Get the total number of customers
def how_many_customers():
    print("How many customers?")
    print(Customer.query.count())