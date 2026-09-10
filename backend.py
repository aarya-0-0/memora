from flask import Flask, redirect, render_template, request,send_from_directory
from dotenv import load_dotenv
import mysql.connector 
import os
import mimetypes


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

@app.route('/create-mem-folder', methods=['GET','POST'])
def create_mem_folder():
    folder_name=request.form['folder_name']
    folder_description=request.form['folder_description']
    cursor.execute('insert into folders (folder_name,folder_description) values(%s,%s)',(folder_name, folder_description))
    db.commit()
    return redirect('/')

@app.route('/media-page/<int:folder_id>', methods=['GET','POST'])
def media_page(folder_id):
    cursor.execute("Select folder_name from folders where   folder_id=%s",(folder_id,))
    folder=cursor.fetchone()
    cursor.execute("Select * from media where folder_id=%s",(folder_id,))
    media=cursor.fetchall()
    
    return render_template('media.html',folder_id=folder_id,media=media, folder_name=folder[0])

@app.route('/add-media', methods=['POST','GET'])
def add_media():
    folder_id = request.form['folder_id']

    cursor.execute('select folder_name from folders where folder_id=%s',(folder_id,))
    folder = cursor.fetchone()

    folder_name= folder[0]
    folder_path= os.path.join('media', folder_name)
    os.makedirs(folder_path, exist_ok=True)


    files = request.files.getlist('media')

    for file in files:
        file.save(os.path.join(folder_path,file.filename))
        media_type= mimetypes.guess_type(file.filename)[0]
        if media_type and media_type.startswith('image'):
            media_type='image'
        elif media_type and media_type.startswith('video'):
            media_type='video'
        cursor.execute("insert into media (folder_id, media_type, media_name ) values (%s,%s,%s)",(folder_id,media_type,file.filename))
        db.commit()
    return redirect(f'/media-page/{folder_id}')

@app.route('/media/<folder_name>/<filename>')
def serve_media(folder_name,filename):
    return send_from_directory(os.path.join('media',folder_name,),filename)

@app.route('/delete-media/<int:media_id>', methods=['POST'])
def delete_media(media_id):
    cursor.execute("select folder_id , media_name from media where media_id=%s",(media_id,))
    media=cursor.fetchone()
    if media:
        folder_id=media[0]
        media_name=media[1]

        cursor.execute("select folder_name from folders where folder_id=%s",(folder_id,))
        folder=cursor.fetchone()
        folder_name=folder[0]
        file_path=os.path.join('media',folder_name,media_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        cursor.execute("Delete from media where media_id=%s",(media_id,))
        db.commit()
        return redirect(f'/media-page/{folder_id}')
    return redirect('/')

@app.route('/delete-folder/<int:folder_id>', methods=['POST'])
def delete_folder(folder_id):

    cursor.execute(
        "select folder_name from folders where folder_id=%s",
        (folder_id,)
    )
    folder = cursor.fetchone()

    if folder:
        folder_name = folder[0]

        folder_path = os.path.join('media', folder_name)

        if os.path.exists(folder_path):
            import shutil
            shutil.rmtree(folder_path)

        cursor.execute(
            "delete from media where folder_id=%s",
            (folder_id,)
        )

        cursor.execute(
            "delete from folders where folder_id=%s",
            (folder_id,)
        )

        db.commit()

    return redirect('/folders')

if __name__=='__main__':
    app.run(debug=True)

