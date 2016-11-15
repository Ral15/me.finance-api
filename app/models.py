from app import db

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(64), unique=True, index=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	password = db.Column(db.String(64))
	bills = db.relationship('Bill')
	incomes = db.relationship('Income', backref='user', lazy='dynamic')
	payments = db.relationship('Payment', backref='user', lazy='dynamic')
	balance = db.relationship('Balance', backref='balances', lazy='dynamic')
	is_premium = db.Column(db.Boolean(), default=True)

	def __repr__(self):
		return '<User %r %r>' % self.username % self.id

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


class Balance(db.Model):
	__tablename__= 'balances'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	amount = db.Column(db.Integer, primary_key=True, unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def __repr__(self):
		return '<Balance %r %r>' % self.user_id % self.amount
