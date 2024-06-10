from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, IMAGES 

app = Flask(__name__) #Flask instance 

#============= configuration to store the photos
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'pictures'
configure_uploads(app,photos)
#===============================================

@app.route('/upload', methods=['GET','POST'])
def Upload():

    if request.method == 'POST' and 'Filename' in request.files: #If an image were upload
        try:
            ImageName = photos.save(request.files['Filename']) # Save the photo in 'photos' variable instance 
            return '<h1>' + ImageName + '</h1>'
        except Exception as e:
            return '<h1>File not allowed </h1>'
        
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)