from flask import Flask, render_template, request, session, url_for, redirect, Blueprint
from opentok import OpenTok, MediaModes
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired
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

def generate_id():
	return ''.join(random.choices(string.ascii_lowercase, k=3)) + '-' + ''.join(random.choices(string.ascii_lowercase, k=2)) + '-' + ''.join(random.choices(string.ascii_lowercase, k=3))

class LoginForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	code = StringField('Code', validators=[])
	submit = SubmitField('Enter Chatroom')

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

@app.route('/create')
def create():
	name = session.get('name', '')
	code = session.get('code', '')
	if code == '':
		id = generate_id()
		opentok_session = opentok.create_session(media_mode=MediaModes.routed)
		sessions[id] = opentok_session
	else:
		id = code
	session['name'] = name
	return redirect(url_for('.chat', id=id))

@app.route('/<id>')
def chat(id):
	name = session.get('name', '')
	if name == '':
		return redirect(url_for('.index'))
	session_id = sessions[id].session_id
	token = opentok.generate_token(session_id)
	session['name'] = ''
	session['code'] = ''
	return render_template('chat.html', api_key=api_key, session_id=session_id, token=token, name=name)

if __name__ == '__main__':
	app.run(debug=True)	