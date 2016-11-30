import os
import re
import datetime
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from flask import Flask, request, g
from flask_restful import Resource, Api, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
app.config["DEBUG"]


#local
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)

manager = Manager(app)

def make_shell_context():
	return dict(app=app, db=db, User=User, Bill=Bill, Income=Income, Payment=Payment, Category=Category, Tip=Tip)
manager.add_command("shell", Shell(make_context=make_shell_context))

migrate = Migrate(app,db)
manager.add_command('db', MigrateCommand)

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	password = db.Column(db.String(128))
	email = db.Column(db.String(64), unique=True)
	bills = db.relationship('Bill')
	balance = db.relationship('Balance', backref='user', lazy='dynamic')
	incomes = db.relationship('Income', backref='user', lazy='dynamic')
	payments = db.relationship('Payment', backref='user', lazy='dynamic')
	is_premium = db.Column(db.Boolean(), default=True)
	# created_at = db.Column(db.DateTime())

	def __repr__(self):
		return '<User %r>' % self.email

	def hash_password(self, password):
		self.password = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password)

class Bill(db.Model):
	__tablename__ = 'bills'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	name = db.Column(db.String(64), unique=True)
	description = db.Column(db.String(64))
	amount = db.Column(db.Float())
	due_date = db.Column(db.DateTime())
	# paid_date = db.Column(db.DateTime())
	is_paid = db.Column(db.Boolean(), default=False)

	def paidBill(self, payment_status):
		self.is_paid = payment_status
		# self.paid_date = datetime.datetime.now()

	def createDueDate(self, date):
		self.due_date = date

	def __repr__(self):
		return '<Bill %r>' % self.name

class Income(db.Model):
	__tablename__ = 'incomes'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	name = db.Column(db.String(64))
	description = db.Column(db.String(64))
	amount = db.Column(db.Float())
	received_date = db.Column(db.DateTime())

	# def createReceivedDate(self, date):
	# 	self.received_date = date

	def __repr__(self):
		return '<Income %r>' % self.name

class Payment(db.Model):
	__tablename__ = 'payments'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	name = db.Column(db.String(64))
	description = db.Column(db.String(64))
	amount = db.Column(db.Float())
	paid_date = db.Column(db.DateTime())
	bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))

	def __repr__(self):
		return '<Payment %r>' % self.name


class Category(db.Model):
	__tablename__ = 'categories'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	name = db.Column(db.String(64))
	description = db.Column(db.String(64))
	payments = db.relationship('Payment', backref='category', lazy='dynamic')
	incomes = db.relationship('Income', backref='category', lazy='dynamic')
	bills = db.relationship('Bill', backref='category', lazy='dynamic')

	def __repr__(self):
		return '<Category %r>' % self.name

class Tip(db.Model):
	__tablename__ = 'tips'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.String(64))
	description = db.Column(db.String(64))	

	def __repr__(self):
		return '<Tip %r>' % self.name


class Balance(db.Model):
	__tablename__ = 'balances'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	amount = db.Column(db.Float, default=0.0)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def addBalance(self, amount):
		self.amount += amount

	def removeBalance(self, amount):
		self.amount -= amount

	def __repr__(self):
		return '<Balance %r>' % self.id


parser = reqparse.RequestParser()


###########
#	User  #
###########

#Validation functions

@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email = email).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

def validEmail(email):
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
		raise ValueError("The email: '{}' is not valid.".format(email))
	else:
		return email

def validPassword(password):
	if len(password) >= 8:
		return password
	else:
		raise ValueError("The password mus be at least 8 characters long.")

class UserStore(Resource):
	#Get all users
	user_fields = {
    	'id': fields.String,
    	'email':   fields.String,
    	# 'password': fields.String,
    	'first_name': fields.String,
    	'last_name': fields.String
	}
	"""Create user"""
	@marshal_with(user_fields)
	def post(self):
		# parser.add_argument('username', type=str, required=True)
		parser.add_argument('first_name', type=str, required=True, help="First name cannot be blank!")
		parser.add_argument('last_name', type=str, required=True, help="Last name cannot be blank!")
		parser.add_argument('password', type=validPassword, required=True)
		parser.add_argument('email', type=validEmail, required=True)
		args = parser.parse_args()
		new_user = User(first_name=args['first_name'],
						last_name=args['last_name'],
						email=args['email'],
						password=args['password'])
		new_user.hash_password(args['password']) 
		db.session.add(new_user)
		db.session.commit()
		return new_user, 201

	"""Get user """
	@auth.login_required
	@marshal_with(user_fields)
	def get(self):
		user = User.query.filter(User.email == g.user.email).first()
		return user, 201

api.add_resource(UserStore,	 '/auth')


############
#	Bill   #
############


class BillStore(Resource):
	bill_fields = {
		'id': fields.Integer,
		'user_id': fields.Integer,
		'payment_id': fields.Integer,
		'category_id': fields.Integer,
		'name': fields.String,
		'description': fields.String,
		'amount': fields.Float,
		'due_date': fields.DateTime,
		'paid_date': fields.DateTime,
		'is_paid' : fields.Boolean
	}

	@auth.login_required
	@marshal_with(bill_fields)
	def get(self):
		bills = Bill.query.filter_by(user_id=g.user.id).all()
		return bills, 201

	"""Create bill """
	@auth.login_required
	@marshal_with(bill_fields)
	def post(self):
		parser.add_argument('name', type=str, help="Name cannot be blank!", required=True)
		parser.add_argument('description', type=str, required=False)
		parser.add_argument('category_id', type=int, required=False)
		parser.add_argument('amount', type=float, help="Amount cannot be blank", required=True)
		parser.add_argument('due_date', type=lambda x: datetime.datetime.strptime(x,'%Y-%m-%d'), required=True, help="Due date cannot be blank")
		args = parser.parse_args()
		new_bill = Bill(name=args['name'],
						description=args['description'],
						amount=args['amount'],
						category_id=args['category_id'],
						user_id=g.user.id,
						due_date=args['due_date'])
		db.session.add(new_bill)
		db.session.commit()
		return new_bill, 201

api.add_resource(BillStore, '/bill', '/bills')


################
#	Category   #
################

class CategoryStore(Resource):
	category_fields = {
		'id': fields.Integer,
		'name': fields.String,
		'description': fields.String,
		'user_id': fields.Integer
	}

	@auth.login_required
	@marshal_with(category_fields)
	def get(self):
		categories = Category.query.filter_by(user_id=g.user.id).all()
		return categories, 201

	@auth.login_required
	@marshal_with(category_fields)
	def post(self):
		parser.add_argument('name', type=str, help="Name cannot be blank", required=True)
		parser.add_argument('description', type=str, required=False)
		args = parser.parse_args()
		new_category = Category(name=args['name'],
								description=args['description'], 
								user_id=g.user.id)
		db.session.add(new_category)
		db.session.commit()
		return new_category, 201

api.add_resource(CategoryStore, '/category', '/categories')

################
#	 Income    #
################

def addToBalance(amount):
	balance = Balance.query.filter_by(user_id=g.user.id).first()
	balance.addBalance(amount)

class IncomeStore(Resource):
	income_fields = {
		'id': fields.Integer,
		'name': fields.String,
		'category_id': fields.Integer,
		'amount': fields.Float,
		'received_date': fields.DateTime,
		'user_id': fields.Integer
	}

	@auth.login_required
	@marshal_with(income_fields)
	def get(self):
		incomes = Income.query.filter_by(user_id=g.user.id).all()
		return incomes, 201


	@auth.login_required
	@marshal_with(income_fields)
	def post(self):
		parser.add_argument('name', type=str, required=True, help="Name cannot be blank")
		parser.add_argument('amount', type=float, required=True, help="Amount cannot be blank")
		parser.add_argument('category_id', type=int, required=False)
		# parser.add_argument('received_date', type=setDateTime, required=True)
		# parser.add_argument('received_date', type=datetime, required=False)
		args = parser.parse_args()
		new_income = Income(name=args['name'],
							amount=args['amount'],
							category_id=args['category_id'],
							user_id=g.user.id, 
							received_date=datetime.datetime.now())
		db.session.add(new_income)
		db.session.commit()
		addToBalance(args['amount'])
		return new_income, 201

api.add_resource(IncomeStore, '/income', '/incomes')


################
#	 Payment   #
################

""" Substract from balance the amount spend """
def delBalance(amount):
	balance = Balance.query.filter_by(user_id=g.user.id).first()
	balance.removeBalance(amount)

""" Validate that the bill id exists ind db """
def validBillId(bill_id):
	bill = Bill.query.get(bill_id)
	if bill is None:
		raise ValueError('Bill id does not exist in db')
	else :
		bill.paidBill(True)
		return bill_id

""" Validate that the category id exists """
def validCategoryId(category_id):
	category = Category.query.get(category_id)
	if category is None:
		raise ValueError('Category id does not exist in db')
	else:
		return category_id

class PaymentStore(Resource):
	payment_fields = {
		'id': fields.Integer,
		'user_id': fields.Integer,
		'name': fields.String,
		'category_id': fields.Integer,
		'description': fields.String,
		'paid_date': fields.DateTime,
		'amount': fields.Float,
		'bill_id': fields.Integer
	}

	@auth.login_required
	@marshal_with(payment_fields)
	def get(self):
		payments = Payment.query.all()
		return payments, 201

	@auth.login_required
	@marshal_with(payment_fields)
	def post(self):
		parser.add_argument('name', type=str, required=True, help="Name cannot be blank")
		parser.add_argument('amount', type=float, required=True, help="Amount cannot be blank")
		parser.add_argument('category_id', type=validCategoryId, required=False)
		parser.add_argument('description', type=str, required=False)
		parser.add_argument('bill_id', type=validBillId, required=False)
		args = parser.parse_args()
		new_payment = Payment(name=args['name'], 
							  amount=args['amount'],
							  category_id=args['category_id'],
							  description=args['description'],
							  user_id=g.user.id,
							  bill_id=args['bill_id'],
							  paid_date=datetime.datetime.now())
		delBalance(args['amount'])
		db.session.add(new_payment)
		db.session.commit()
		return new_payment, 201

api.add_resource(PaymentStore, '/payment', '/payments')


################
#	 Balance   #
################

class BalanceStore(Resource):
	balance_fields = {
		'id': fields.Integer,
		'user_id': fields.Integer,
		'amount': fields.Float
	}

	@auth.login_required
	@marshal_with(balance_fields)
	def get(self):
		balance = Balance.query.filter_by(user_id=g.user.id).first()
		return balance, 201

	@auth.login_required
	@marshal_with(balance_fields)
	def post(self):
		parser.add_argument('amount', type=float, required=True, help="Amount cannot be blank")
		args = parser.parse_args()
		new_balance = Balance(amount=args['amount'],
							  user_id=g.user.id)
		db.session.add(new_balance)
		db.session.commit()
		# new_balance.addBalance(args['amount'])
		return new_balance, 201

api.add_resource(BalanceStore, '/balance')
