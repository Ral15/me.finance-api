import os
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Role(db.Model):
	__tablename__ = 'role'
	id = db.Column(db.Integer, primary_key=True)
	is_premium = db.Column(db.Boolean(), default=False)

	def __repr__(self):
		return '<Role %r>' % self.is_premium

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))

	def __repr__(self):
		return '<User %r>' % self.username

# class Bill(db.Model):
# 	__table__name = 'bill'
# 	id = db.Column(db.Integer, primary_key=True)


@app.route('/')
def index():
	return '<h1>Hello World, I am me.finance</h1>'


@app.route('/user/<name>')
def user(name):
	return '<h1>Hello, %s!</h1>' % name

if __name__=='__main__':
	app.run(debug=True)