

//################### SENDING FROM CLIENT TO SERVER #########################################################################################
/*============== Client Side ===================*/
var socket = io.connect('http://127.0.0.1:5000');//--->  WebSocket connection to the server at the specified address (http://127.0.0.1:5000).

//connect : event expecting to be triggered by
//function: will execute the message that will be send
socket.on('connect',function(){
    socket.send('I am now connected'); //Sender
    
    socket.on('message',function(msg){//Listener 
        alert(msg);
    });

    socket.emit('custom event','the custom event message'); //From client to server

    socket.on('from flask',function(msg){//Listening
        alert(msg);
    });

    socket.emit('receive json',{'name':'Paul Manriquez'});//Sending a json object to the server 
    socket.on('Send Json',function(jsonmessage){
            alert(jsonmessage['extension']);
    });
    
});

/*================== SERVER SIDE =================*/
/*#This will be triger when a connection between the client and server will be performed
@socketio.on('message') #Expecting a message
def receive_message(message):
	print('####################:{}'.format(message))
*/


//################### SENDING FROM CLIENT TO SERVER #########################################################################################