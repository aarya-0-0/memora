from flask import Flask, redirect, render_template, request
from dotenv import load_dotenv
import mysql.connector 
import os

app=Flask(__name__)
load_dotenv()
try:
    db= mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv("DB_USER"),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )
    print("Connection Successful!")
    cursor=db.cursor(buffered=True)
except Exception as e:
    print("Connection Failed :( ", e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/folders')
def folders():
    cursor.execute("select * from folders")
    folders=cursor.fetchall()
    if not folders:
        return render_template('Nofolders.html')
        
    return render_template('folders.html', folders=folders)

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/create-mem-folder')
def create_mem_folder():
    folder_name=request.form['folder_name']
    folder_description=request.form['folder_description']
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)
