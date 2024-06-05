from flask import Flask, g, request,jsonify
from database import get_db

app = Flask(__name__)

#Authentication credentials
api_username = 'admin'
apr_password = 'password'
#==========================


#Each time we dont neet a data base connection, we disconnect, ensuring no memory leaks
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
#======================================================================================       



@app.route('/member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    
    #Make a connection with the data base and execute a query to se the user by id that corresponds
    db = get_db()
    memberCur = db.execute('SELECT id,name,email,level FROM members WHERE id = ?',[member_id])
    member = memberCur.fetchone()

    return jsonify({'member':{'id':member['id'],'name':member['name'],'email':member['email'],'level':member['level']}})

#===================================================================================================

#===================================== Display all the members GET
@app.route('/member', methods=['GET'])
def get_members():
    
    #Data base connection 
    db = get_db()#Get the data base connection
    member_cur = db.execute('SELECT id,name,email,level FROM members')#query
    member_rows = member_cur.fetchall()#Get nthe list of objects 

    print('*************')
    Members = [] #Construct a list to hold dictionaries 
    for member in member_rows:
        dictionary = {} #Each element in the list must be a dictionary to jsonify
        dictionary['id'] = member['id']
        dictionary['name'] = member['name']
        dictionary['email'] = member['email']
        dictionary['level'] = member['level']

        Members.append(dictionary)

    #======== Authentication ================
    username = request.authorization.username
    password = request.authorization.password 

    if username == api_username and password == apr_password:
        print('*******UserName|Password*******')
        print(f'Name:{username} Password={password} authentication PASS')
        return jsonify({'members':Members})
    else:
        print('*******UserName|Password*******')
        print(f'Name:{username} Password={password} authentication FAILED')
        return jsonify({'message':'Authentication failed!'}), 403
        
#====================================== Insert a member POST 
@app.route('/member', methods=['POST'])
def add_member():
    new_member_data = request.get_json()# when we get the json file, save it in new_member_data

    #======= get  the data from the json file
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']
    #========================================

    #Data base connection
    db = get_db()#Get the connection to the data base 
    db.execute('insert into members (name, email, level) values (?, ?, ?)', [name, email, level])#write the query
    db.commit()#Commit the changes
    #============================================================================================================ 

    #Confirmation data received
    member_cur = db.execute('SELECT id,name,email,level FROM members WHERE name = ?', [name])
    member = member_cur.fetchone()

    return jsonify({'id':member['id'],'name':member['name'],'email':member['email'],'level':member['level']})
#================================================================================================================

#============================================================== UPDATE A NEW MEMBER ENDPOINT
#PUT: Used to create or update all the data
#PATCH: Update pacial data 
@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
def edit_member(member_id):

    update_memberData = request.get_json()#Get the json data

    #====== Get the data from the json 
    name = update_memberData['name'] 
    email = update_memberData['email']
    level = update_memberData['level']
    #=================================

    #Quote: since we are not retrieving data, we dont need a cursor in (db.execute) to make the commit
    db = get_db()#Data base connection
    db.execute('UPDATE members SET name = ?,email = ?,level = ?  WHERE id = ?',[name,email,level,member_id])#Write the query
    db.commit()#======================================================================================

    #Get the new data member that you have updated
    member_cur = db.execute('SELECT id,name,email,level FROM members WHERE id = ?', [member_id])
    myMember = member_cur.fetchone()
    
    return jsonify({'member':{'id':myMember['id'],'name':myMember['name'],'email':myMember['email'],'level':myMember['level']}})
#================================================================================================================================


#======================================================== Delete a member by ID
@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    db = get_db()#Connect to the data base 
    db.execute('DELETE FROM members WHERE id = ?',[member_id])
    db.commit()

    ans = 'the member with the id {} has been deleted'.format(member_id)

    return jsonify({'message': ans})
#============================================================================================

if __name__ == '__main__':
    app.run(debug=True)