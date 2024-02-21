from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

messages = []

def generate_chatroom_id():
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for _ in range(4))

@app.route('/')
def index():
    return render_template('landing_page.html')

@app.route('/join_chatroom', methods=['GET', 'POST'])
def join_chatroom():
    if request.method == 'POST':
        chatroom_id = request.form['chatroom_id']
        return redirect(url_for('enter_username', chatroom_id=chatroom_id))
    return render_template('join_chatroom.html')

@app.route('/create_chatroom', methods=['GET', 'POST'])
def create_chatroom():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['chatroom_id'] = generate_chatroom_id()
        return redirect(url_for('chatroom', chatroom_id=session['chatroom_id']))
    return render_template('create_chatroom.html')

@app.route('/enter_username/<chatroom_id>', methods=['GET', 'POST'])
def enter_username(chatroom_id):
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('chatroom', chatroom_id=chatroom_id))
    return render_template('enter_username.html', chatroom_id=chatroom_id)

@app.route('/chatroom/<chatroom_id>')
def chatroom(chatroom_id):
    username = session.get('username')
    if not username or session.get('chatroom_id') != chatroom_id:
        return redirect(url_for('index'))
    return render_template('chatroom.html', chatroom_id=chatroom_id, username=username)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('chatroom_id', None)
    messages.clear()
    return redirect(url_for('index'))

@socketio.on('message')
def handle_message(data):
    messages.append(data)
    emit('message', {'username': data['username'], 'message': data['message']}, broadcast=True)

@socketio.on('fetch_messages')
def fetch_messages():
    emit('messages', messages)



if __name__ == '__main__':
    socketio.run(app, debug=True,host='0.0.0.0')
