from flask import Flask, render_template, request, session, url_for, redirect, Blueprint, send_from_directory
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired
from opentok import OpenTok, MediaModes
import os
import random
import string

main = Blueprint('main', __name__)

secret_key = str(os.urandom(24))

app = Flask(__name__)
app.config['TESTING'] = False
app.config['DEBUG'] = True
app.config['FLASK_ENV'] = 'deployment'
app.config['SECRET_KEY'] = secret_key

api_key = "46878634"
api_secret = "bf5a7aea68750bbccbaae8c1c4c424f38d8ec2ae"
opentok = OpenTok(api_key, api_secret)

sessions = dict()

class LoginForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	code = StringField('Code', validators=[])
	submit = SubmitField('Enter Chatroom')

def generate_id():
	return ''.join(random.choices(string.ascii_lowercase, k=3)) + '-' + ''.join(random.choices(string.ascii_lowercase, k=2)) + '-' + ''.join(random.choices(string.ascii_lowercase, k=3))

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET', 'POST'])
def index():
	form = LoginForm()
	if form.validate_on_submit():
		session['name'] = form.name.data
		session['code'] = form.code.data
		return redirect(url_for('.create'))
	elif request.method == 'POST':
		form.name.data = session.get('name', '')
		form.code.data = session.get('code', '')
	return render_template('index.html', form=form)

@app.route('/create', methods=['GET', 'POST'])
def create():
	form = LoginForm()
	if request.method == 'GET':
		name = session.get('name', '')
		code = session.get('code', '')
		if code == '':
			id = generate_id()
			try:
				sessions[id] = opentok.create_session(media_mode=MediaModes.routed)
			except Exception as e:
				app.logger.error(e.__cause__)
				return redirect(url_for('.create'))
			return redirect(url_for('.chat', id=id))
		else:
			id = code
			return redirect(url_for('.chat', id=id))
	else:
		name = form.name.data
		code = form.code.data
		if code == '':
			id = generate_id()
			try:
				sessions[id] = opentok.create_session(media_mode=MediaModes.routed)
			except Exception as e:
				app.logger.error(e.__cause__)
				return redirect(url_for('.create'))
			return redirect(url_for('.chat', id=id))
		else:
			id = code
			return redirect(url_for('.chat', id=id))

@app.route('/<id>', methods=['GET', 'POST'])
def chat(id):
	form = LoginForm()
	current_sessions = sessions
	if not current_sessions:
		return redirect(url_for('.chat', id=id))
	if request.method == 'GET':
		name = session.get('name', '')
		session['name'] = ''
		session['code'] = ''
		if name == "":
			return render_template('index.html', id=id, form=form)
		else:
			session_id = current_sessions[id].session_id
			try:
				token = opentok.generate_token(session_id)
			except Exception as e:
				app.logger.error(e.__cause__)
				return redirect(url_for('.chat', id=id))
			return render_template('chat.html', api_key=api_key, session_id=session_id, token=token, name=name)
	else:
		name = form.name.data
		code = form.code.data
		session_id = current_sessions[id].session_id
		try:
			token = opentok.generate_token(session_id)
		except Exception as e:
			app.logger.error(e.__cause__)
			return redirect(url_for('.chat', id=id))
		return render_template('chat.html', api_key=api_key, session_id=session_id, token=token, name=name)

if __name__ == '__main__':
	app.run(debug=True)