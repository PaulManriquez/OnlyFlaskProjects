from flask import Flask, render_template,request
from wtforms import Form, StringField, validators,DateTimeField, PasswordField,BooleanField
from wtforms.widgets import TextArea

app = Flask(__name__)#Instance 

class UserRegistration_F(Form):
    #User Name 
    user_name = StringField("Name",
                            validators=[validators.InputRequired(),
                                        validators.length(min=4,max=20)])
    #User Password 
    user_password = PasswordField("Password",
                            validators=[validators.InputRequired(),
                                        validators.length(min=4,max=20)])
    #Phone
    user_phone = StringField("Phone",
                            validators=[validators.InputRequired()])
    #Time
    user_time = DateTimeField("Date",
                              validators=[validators.InputRequired()],
                              format="%Y-%m-%d")
    #Check box
    user_GetImail = BooleanField("Save Email",
                                 default=False)
    #About me
    user_Aboutme = StringField("About me",
                               validators=[validators.Optional()],
                               widget=TextArea())
     



#=============== Home Route
@app.route("/",methods=['GET','POST'])
def Index():
    UR_form = UserRegistration_F(request.form) #Creates an instance of our form
    if request.method=='POST' and UR_form.validate():
        print('<*******Getting Data*******>')
        print(UR_form.user_name.data)
        print(UR_form.user_password.data)
        print(UR_form.user_phone.data)
        print(UR_form.user_time.data)
        print(UR_form.user_GetImail.data)
        print(UR_form.user_Aboutme.data)

    return render_template("home.html",form = UR_form)

#============== Running app =================== 
app.run(host="0.0.0.0", port=5000, debug = True)