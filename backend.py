from flask import Flask, redirect, render_template
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
    return render_template('folders.html')

if __name__=='__main__':
    app.run(debug=True)
