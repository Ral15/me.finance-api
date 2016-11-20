import os
import re
from flask_bcrypt import Bcrypt
from flask import Flask, request
from flask_restful import Resource, Api, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt(app)

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
	# username = db.Column(db.String(64), unique=True, index=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	password = db.Column(db.String(64))
	email = db.Column(db.String(64), unique=True)
	bills = db.relationship('Bill')
	incomes = db.relationship('Income', backref='user', lazy='dynamic')
	payments = db.relationship('Payment', backref='user', lazy='dynamic')
	is_premium = db.Column(db.Boolean(), default=True)

	def __repr__(self):
		return '<User %r>' % self.email

class Bill(db.Model):
	__tablename__ = 'bills'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	name = db.Column(db.String(64))
	description = db.Column(db.String(64))
	amount = db.Column(db.Float())
	due_date = db.Column(db.DateTime())
	paid_date = db.Column(db.Integer, db.ForeignKey('payments.paid_date'))
	# is_paid = db.Column(db.Boolean())

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
	def __repr__(self):
		return '<Payment %r>' % self.name


class Category(db.Model):
	__tablename__ = 'categories'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.String(64))
	description = db.Column(db.String(64))
	payments = db.relationship('Payment')
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

parser = reqparse.RequestParser()


###########
#	User  #
###########

#Validation functions

def validEmail(email):
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
		raise ValueError("The email: '{}' is not valid.".format(email))
	else:
		return email

def validPassword(password):
	if len(password) >= 8:
		return bcrypt.generate_password_hash(password)
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

	# """Get all users"""
	# @marshal_with(user_fields)
	# def get(self):
	# 	return User.query.all()

	"""Get user by id"""
	@marshal_with(user_fields)
	def get(self, id):
		user = User.query.filter(User.id == id).first()
		if not user:
			abort(404, message="User {} doesn't exist".format(id))
		return user

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
		db.session.add(new_user)
		db.session.commit()
		return new_user, 201

api.add_resource(UserStore,	 '/auth/create', '/auth/<int:id>')

############
#	Bill   #
############

if __name__=='__main__':
	app.run(debug=True)