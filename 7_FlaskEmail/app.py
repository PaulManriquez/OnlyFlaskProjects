from flask import Flask, render_template, request
from flask_mail import Mail, Message
from wtforms import Form, StringField, validators
from wtforms.widgets import TextArea
import logging




def create_app():
    app = Flask(__name__)

    #======================== Configurations =================================================
    app.config['MAIL_SERVER'] = 'smtp.gmail.com' #Server of your email
    app.config['MAIL_PORT'] = 465 #Port were will be send the message
    app.config['MAIL_USERNAME'] = '' #Your Email
    app.config['MAIL_PASSWORD'] = ''  # Your password
    app.config['MAIL_USE_TLS'] = False #(Transport Layer Security)
    app.config['MAIL_USE_SSL'] = True #(Secure Sockets Layer)
    app.config['MAIL_DEFAULT_SENDER'] = '' #Name of the sender 

    #============== Mail instance
    mail = Mail(app)

    #======================================= Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    #============================================== My form to send a message
    class MyForm(Form):
        #User Name 
        user_Subject = StringField("Subject",
                                validators=[validators.InputRequired(),
                                            validators.length(min=4,max=20)])
            
            #Message
        user_Message = StringField("My message",
                                    validators=[validators.Optional()],
                                    widget=TextArea())
    #=========================================================================


    @app.route('/',methods=['GET','POST'])#Root endpoint
    def Index():
        try:
            
            FormEmail = MyForm(request.form) #Generate an instance of the form 
            
            if request.method == 'POST' and FormEmail.validate(): # if the form was filled and is a POST method
                subjectName = FormEmail.user_Subject.data #Get the string data
                TheMessage = FormEmail.user_Message.data #Get the string data
                
                #====================================================================== Sending the message
                              #Subject | asunto
                msg = Message(subjectName,
                            sender=('Paul Manriquez','paulmanriquezengineer@gmail.com'), 
                            recipients=['wamim33955@fna6.com'])
                msg.body = TheMessage #Messaje

                mail.send(msg)#Send the email
                #======================================================================

                return '<h1>The message was sent</h1>' #Confirmation message
            
            return render_template("home.html",form=FormEmail)#upload the form
        
        except Exception as e:#Let me know if an exception rise
            logger.exception("Failed to send email")
            return f'<h1>Failed to send email: {e}</h1>'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
