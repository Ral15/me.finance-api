# from app import db
# from .models import User
# from flask_restful import Resource, Api, reqparse, fields, marshal_with

# parser = reqparse.RequestParser()

# class Usr(Resource):
# 	resource_fields = {
#     	'username':   fields.String
# 	}
# 	@marshal_with(resource_fields)
# 	def get(self):
# 		return User.query.all()

# 	def post(self):
# 		parser.add_argument('username', type=str, required=True)
# 		parser.add_argument('first_name', type=str, required=True)
# 		parser.add_argument('last_name', type=str, required=True)
# 		parser.add_argument('password', type=str, required=True)
# 		args = parser.parse_args()
# 		new_user = User(username=args['username'], 
# 						first_name=args['first_name'],
# 						last_name=args['last_name'],
# 						password=args['password']) 
# 		db.session.add(new_user)
# 		db.session.commit()
# 		return '' , 201

# api.add_resource(Usr,	 '/auth/create', '/auth/all')