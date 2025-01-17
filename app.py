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
statuses = ['1', '2', '3', '4']
envs = ['PROD', 'DEV', 'TEST']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html', statuses=statuses, envs=envs)


@app.route('/send', methods=["GET", "POST"])
def send_data():
    if request.method == "POST":

        if 'upload_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = list(request.files.lists())[0][1]
        if app.config['UPLOAD_FOLDER'] not in os.listdir():
            os.mkdir(app.config['UPLOAD_FOLDER'])
        output_file = ''
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if len(files) == 0:
            flash('No selected file')
            return redirect(request.url)
            # filename = secure_filename(file.filename)

        curdate = datetime.date.today().strftime('%d.%m.%Y')
        dir_name = curdate + '_' + request.form['INC'] + '_' + request.form['AppEnv']

        #Удаляем старые папки и файлы если файл уже есть
        for upload_files in os.listdir(app.config['UPLOAD_FOLDER']):
            if dir_name in upload_files :
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], dir_name)
                try:
                    if os.path.isdir((old_file_path)):
                        shutil.rmtree(old_file_path)
                    else:
                        os.remove(old_file_path)
                    # Удаляем архив
                    old_archive_path = os.path.join(old_file_path,'.zip')
                    if os.path.exists(old_archive_path):
                        os.remove(old_archive_path)
                    break
                except:
                    flash('Не удалось очистить кэш, операция продолжается')
                    pass
                    break

        # for old_file in os.listdir(UPLOAD_FOLDER):
        #     old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_file)
        #     try:
        #         if os.path.isdir((old_file_path)):
        #             shutil.rmtree(old_file_path)
        #         else:
        #             os.remove(old_file_path)
        #     except:
        #         flash('Не удалось очистить кэш, операция продолжается')
        #         pass
        try:
            os.mkdir(app.config['UPLOAD_FOLDER'] + '//' + dir_name)
        except (FileExistsError):
            print('Folder already exists, skipping')
        for file in files:
            #Сохраняем загруженный файл
            upload_file_path = os.path.join(app.config['UPLOAD_FOLDER'], dir_name, dir_name + '.xml')
            file.save(upload_file_path)  # cначала папка потом файл
            #return redirect(url_for('download_file', name=filename))

            # Начинаем обработку сохранённого файла
            try:
                xml = XMLdoc(app.config['UPLOAD_FOLDER'], dir_name, dir_name + '.xml', request.form['Status'],
                             request.form['EGRULNotIncluded'], request.form['SVR_VERSION'])
            except:
                flash('Error in creating XMLObject ')
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
        try:
            output_folder_path = app.config['UPLOAD_FOLDER'] + '//' + dir_name
            shutil.make_archive(output_folder_path, 'zip', output_folder_path)
            return send_file(output_folder_path + '.zip', as_attachment=True)
        except FileNotFoundError:
            flash('No templates for splitting. Ask manager')
            pass
        os.remove(upload_file_path)
    return render_template('index.html', statuses=statuses, envs=envs)


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()
