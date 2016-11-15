from app import app

@app.route('/')
def index():
	return '<h1>Hello World, Me.Finance API</h1>'