from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random 
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MySecretKey'
socketio = SocketIO(app)
#===================================================================

rooms = {} #Dictionary of rooms created
def generate_unique_code(lenght:int) -> str:
    while True:
        code = ''
        #Generate the code
        for _ in range(lenght):
            code += random.choice(ascii_uppercase)
        #Check if the code doesn't exist in the rooms dictionary
        if code not in rooms:
            break 
    return code     


@app.route("/",methods=['GET','POST'])
def HomePage():
    session.clear() #Clear the session before create another one 

    if request.method=='POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join',False)#Button | since join is a key of a dictionary, we stablish it value to False to simulate that is off if is not being pressed
        create = request.form.get('create',False)#Button

        #Handle possible errors 
        if not name:
            return render_template("home.html",error='Please enter a name', code=code, name=name)
        if not code and join!=False:
            return render_template("home.html",error='Please enter a code', code=code, name=name)

        room = code #The room corresponds to the code introduced

        if create != False:#If you want to generate a new room 
            room = generate_unique_code(4)
            rooms [room] = {'members':0,'messages':[]}#New empty room | overwrite
        elif code not in rooms:#If you want tojoin to a room and the code is not in the dictionary of rooms
            return render_template('home.html',error='Room doesnt exist',code=code,name=name)

        #Create a SESSION in the room 
        session['room'] = room 
        session['name'] = name 
        #============================

        return redirect(url_for("Room")) #Now redirect the user to the room 


    return render_template("home.html")


@app.route('/room')
def Room():
    room = session.get('room') #Get the room where is 
    name = session.get('name') #Get the name
    #Needs to be a user, a room or the room must exist in rooms 
    if (room is None) or (name is None) or (room not in rooms):
        return redirect(url_for('HomePage')) 

    return render_template("room.html",roomcode=room, messages=rooms[room]["messages"])



#============= Socket ======
#Server re send the message to the room that corresponds
@socketio.on("message")
def message(data):
    room = session.get("room")
    
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }

    send(content,to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said:{data['data']}")


@socketio.on("connect") #Listening
def connect(auth):
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return 'No room or name'
    if room not in rooms:
        leave_room(room)
        return 'the room do not exist'
    
    #Validate and join the user to the room 
    join_room(room)
    send({"name":name, "message": "has entered in the room"}, to=room)
    rooms[room]["members"] += 1 #A new person has entered to this room 
    print(f"{name} joined room:{room}")

#Disconnect    
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -=1
        if rooms[room]["members"] <= 0:
            del rooms[room] #No longer we need this room 

    send({"name":name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room:{room}")

if __name__ == '__main__':
    socketio.run(app, debug=True) 
