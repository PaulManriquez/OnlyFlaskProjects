#Programmer: Paul Manriquez
#Date: June 2024

from flask import Flask, render_template, request, url_for, redirect, send_from_directory, session
import os 

app = Flask(__name__)
app.secret_key = 'SECRETKEY'

#============= Folder configuration to upload images ==============
UPLOAD_FOLDER = 'uploads'                   # <-- Create the folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
#==================================================================    


#Static endpoint
@app.route('/')
def Indexx():
    MyList = [1,2,3,4,5]
    Sometext = 'Hello human'

    return render_template('index.html',MyList=MyList,Sometext=Sometext)

#ClickME
@app.route('/clickme')
def ClickMe():
    return render_template('clickme.html')

#Dinamic route
@app.route('/greet/<name>')
def Greet(name):
    return f'hello {name}'

#Integers as parameters
@app.route('/add/<int:n1>/<int:n2>')
def Add(n1,n2):
    return f'{n1} + {n2} = {n1 + n2}'

#====== Dump Login Practice SESSIONS =======================================================================
@app.route('/login',methods=['GET','POST'])
def LoginForm():
    if request.method == 'GET':
        return render_template('LoginForm.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        #Login session cokie
        session['name'] = username
        session['password'] = password
        #
        LoginList = [username,password]
        return render_template('UserLogIn.html',LoginList=LoginList , message='A session has been created')

#Clear session ENDPOINT
@app.route('/clearSession')
def ClearSession():
    session.clear()
    return render_template('SessionEND.html',message='SESSION ENDED')    

#=============================================================================================================
    
#==================== UPLOAD IMAGES =======================================
@app.route('/uploadImage',methods=['GET','POST'])
def UploadFile():
    if request.method == 'GET':
        return render_template('UploadFile.html')
    elif request.method == 'POST':
        try:
            if 'MyImage' not in request.files:
                return 'There is not a image uploaded'
            
            file = request.files['MyImage'] #Get the image
            
            if file.filename == '':#If the file wasn't upload with a name 
                return 'No file, blank file'
            else:
                print('***********UploadImage')
                print(file.filename) 
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],file.filename))#File.save method to store the image

                return redirect(url_for('uploaded_file',filename=file.filename))
        except Exception as e:
            return f'An error has occurred: {e}'

@app.route('/uploads/<filename>') #Endpoint to send the file name
def uploaded_file(filename):
    return render_template('display_image.html',filename=filename)


#==============================================================================================================

#=== DOWNLOAD IMAGES 
@app.route('/downloadImages')
def DownloadImage():
    ListOfImages = os.listdir(app.config['UPLOAD_FOLDER']) #Get the images from uploads folder 
    print('***********************************')
    print(ListOfImages)
    return render_template('Download_images.html',ImagesL = ListOfImages)

@app.route('/download/<filename>') #Return a link to download the image
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename, as_attachment=True)

@app.route('/uploads/images/<filename>')# return the image to display
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

if __name__ == '__main__':
    app.run(debug=True)