from flask import Flask, render_template
from flask_socketio import SocketIO,send,emit

app = Flask(__name__)

app.config['SECRET_KEY']='secretkey'
app.config['DEBUG']= True

socketio=SocketIO(app)
#==============================================

@app.route('/')
def Index():
	return render_template('index.html')

@socketio.on('message')
def receive_message(message):
	print('####################:{}'.format(message))
	
	send('This is a message from flask')

#-------------------------------------------------------------------------
@socketio.on('custom event')
def receive_custom_event(message):
	print('****************This is the custom message:{}'.format(message))

	emit('from flask', 'Custom Event: sending alert from flask!!!')#From server to client

#-------------------------------------------------------------------------	

#Receive and Send Json Objects
@socketio.on('receive json')
def receive_json(jsonMessage):
	print('***************** Receive Json *******************')
	print('This is the mesage: {}'.format(jsonMessage['name']))
	print('***************** Sending Json *******************')
	emit('Send Json',{'extension':'Flask-SocketIO'},json=True)

if __name__ == '__main__':
	socketio.run(app) 
