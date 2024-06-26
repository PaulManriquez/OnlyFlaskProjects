from flask import Flask, render_template, request,redirect, url_for

app = Flask(__name__,template_folder='templates')

@app.template_filter('enumerate')#<-- custom function to enumerate with jinja2 | used in index.html page 
def do_enumerate(seq):
    return enumerate(seq)
#=============== Global task todo =============
todos = [{"Task":"sample to do 0", "Done":False},
         {"Task":"sample to do 1", "Done":False},
         {"Task":"sample to do 2", "Done":False}
         ]
#==============================================

@app.route('/')
def Index():
    return render_template('index.html',todos = todos)


#================================= Add a new task endpoint
@app.route('/add',methods=['POST'])
def Add():
    todo = request.form['Todo']
    if todo:
        todos.append({"Task":todo, "Done":False}) #<-- Add a new task 
    return redirect(url_for('Index'))

#================================== Edit a task
@app.route('/edit/<int:index>', methods=['POST'])
def Edit(index):
    todo = todos[index]# <--- Get the index (Reference) for the dictionary where we need to update the task
    return render_template('edit.html',todo=todo, index = index)

@app.route('/FinishEdit/<int:index>',methods=['POST'])
def FinishEdit(index):
    EditTask = request.form['TodoEdit']
    todos[index]['Task'] = EditTask
    return redirect(url_for('Index'))
#===============================================


#=============================== Check box to mark a task if was completed or not 
@app.route('/check/<int:index>',methods=['POST'])
def Check(index):
    print('I was pressed')
    print(todos[index]['Done'])
    #==== Change the state of a chackbox button === 
    todos[index]['Done'] = not ( todos[index]['Done'] ) 
    print(todos[index]['Done'])
    return redirect(url_for('Index'))

#=============================== Delete a task todo
@app.route('/delete/<int:index>', methods=['POST'])
def Delete(index):
    del todos[index] # <--- Get the index to delete the dictionary  
    return redirect(url_for('Index'))


if __name__ == '__main__':
    app.run(debug=True)