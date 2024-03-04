from flask import Flask, flash, render_template, request, redirect, send_file, url_for
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from XMLdoc import XMLdoc
import os
import datetime
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xml'}

app = Flask(__name__)
statuses=['1','2','3','4']
envs=['PROD','DEV','TEST']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html',statuses=statuses,envs=envs)

@app.route('/send', methods = ["GET","POST"])
def send_data():
    if request.method == "POST":
        if 'upload_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['upload_file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            curdate = datetime.date.today().strftime('%d.%m.%Y')
            newfile_name = curdate + '_' + request.form['INC'] + '_' + request.form['AppEnv']
            try:
                os.mkdir(app.config['UPLOAD_FOLDER']+'\\'+ newfile_name)
            except (FileExistsError):
                print('Folder already exists, skipping')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],  newfile_name+'.xml')) # cначала папка потом файл
            #return redirect(url_for('download_file', name=filename))

            xml = XMLdoc(app.config['UPLOAD_FOLDER']+'\\'+ newfile_name+'.xml', request.form['Status'],request.form['EgrulNotIncluded'])
            if xml.check_encoding()['encoding'] != 'utf-8':
                xml.convert_encoding(old_encoding="iso-8859-5", new_encoding="utf-8")

            #Удалим заголовки
            xml.remove_header()
            #Отредачим тело
            xml.edit_xml()
            #Поставим заголовки и скачаем пользователю
            output_file = xml.set_header("ul_template.xml", "utf-8")
            try:
                return send_file(output_file, as_attachment=True)
            except FileNotFoundError:
                flash('No templates for splitting. Ask manager')
                pass
    return render_template('index.html', statuses=statuses, envs=envs)

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()

