from flask import Flask, flash, render_template, request, redirect, send_file, url_for
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from XMLdoc import XMLdoc
import os
import datetime
import shutil

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
        files = list(request.files.lists())[0][1]
        output_file=''
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if len(files) == 0:
            flash('No selected file')
            return redirect(request.url)
            # filename = secure_filename(file.filename)
        curdate = datetime.date.today().strftime('%d.%m.%Y')
        dir_name = curdate + '_' + request.form['INC'] + '_' + request.form['AppEnv']
        try:
            os.mkdir(app.config['UPLOAD_FOLDER'] + '//' + dir_name)
        except (FileExistsError):
            print('Folder already exists, skipping')
        for file in files:
                #Сохраняем загруженный файл
                upload_file_path =os.path.join(app.config['UPLOAD_FOLDER'], dir_name, dir_name+'.xml')
                file.save(upload_file_path) # cначала папка потом файл
                #return redirect(url_for('download_file', name=filename))

                # Начинаем обработку сохранённого файла
                try:
                    xml = XMLdoc(app.config['UPLOAD_FOLDER'],dir_name,dir_name+'.xml', request.form['Status'],request.form['EGRULNotIncluded'])
                except:
                    break;
                #xml = XMLdoc(app.config['UPLOAD_FOLDER']+'//'+dir_name+'//'+ dir_name+'.xml', request.form['Status'],request.form['EgrulNotIncluded'])
                # if xml.check_encoding()['encoding'] != 'utf-8':
                #     xml.convert_encoding(old_encoding="iso-8859-5", new_encoding="utf-8")
                #Удалим заголовки
                xml.remove_header()
                #Отредачим тело
                xml.edit_xml()
                #Поставим заголовки
                xml.set_header("ul_template.xml", "utf-8")
                #Канонализируем и скачаем
                #xml.canonicalize()
                os.remove(upload_file_path)
        try:
            output_folder_path=app.config['UPLOAD_FOLDER']+'//'+dir_name
            shutil.make_archive(output_folder_path, 'zip', output_folder_path)
            return send_file(output_folder_path+'.zip', as_attachment=True)
        except FileNotFoundError:
            flash('No templates for splitting. Ask manager')
            pass
    return render_template('index.html', statuses=statuses, envs=envs)

if __name__ == '__main__':

    app.run()

