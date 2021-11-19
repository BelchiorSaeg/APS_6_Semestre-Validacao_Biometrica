import os
from data_manager import DataBase
from flask import Flask, render_template, request, make_response, session, redirect
from werkzeug.utils import secure_filename
from exceptions import ExceptionCodes, LoginError
import login as login_package
app = Flask(__name__)

app.secret_key = '98cece9dc0a7d58b18cf8118f655ee5c9de42730c2a761cee92613c6b1b2b3cf'

ALLOWED_MIMETYPES = ['image/*']

access_level = [
    {},
    {
        'title': 'Produção agrícola',
        'color': '#C4F8A4',
        'color_row_odd':'#A5B5C6',
        'color_row_even': '#A9BE9C'
    },
    {
        'title': 'Informações fiscais',
        'color': '#ED7D31',
        'color_row_odd':'#F8D7CD',
        'color_row_even': '#FCECE8'
    },
    {
        'title': 'Agrotóxicos',
        'color': '#70AD47',
        'color_row_odd':'#D5E3CF',
        'color_row_even': '#EBF1E9'
    }
]

class System:
    """
    | > Gerenciador do sistema.
    """
    SYSTEM_IDLE = 0
    SYSTEM_STARTED = 1
    SYSTEM_FINISHED = 2

    def __init__(self) -> None:
        self.start()
        self._status = self.SYSTEM_IDLE

    @property
    def database(self) -> DataBase:
        return self._database

    @property
    def status(self) -> int:
        return self._status

    def start(self):
        self._database = DataBase()
        self._database.connect()

        login.DATABASE = self.database

        self._status = self.SYSTEM_STARTED

    def finish(self):
        self._database.close()

        self._status = self.SYSTEM_FINISHED

def is_logged():
    return 'user_id' in session and 'full_name' in session and 'permission_level' in session

def carregar_dados():
    if int(session['permission_level']) == 1:
        agrotoxicos = SYSTEM.database.agrotoxicos.head(1000)
        items = []
        last_id = 0
        for index, row in agrotoxicos.iterrows():
            if index > 0:
                if int(row[0]) != last_id:
                    last_id = int(row[0])
                    items.append({
                        'id': int(row[0]),
                        'Marca comercial': row[1],
                        'Formulação': row[2],
                    })
    elif int(session['permission_level']) == 2:
        agrotoxicos = SYSTEM.database.informacoes_fiscais.head(1000)
        items = []
        for index, row in agrotoxicos.iterrows():
            if index > 0:
                items.append({
                    'id': int(index),
                    'Ano': row[0],
                    'Detalhes': row[7],
                })
    elif int(session['permission_level']) == 3:
        agrotoxicos = SYSTEM.database.produtores_rurais.head(1000)
        items = []
        for index, row in agrotoxicos.iterrows():
            if index > 0:
                items.append({
                    'id': int(index),
                    'Tipo de entidade': row[0],
                    'País': row[2],
                    'UF': row[3]
                })
    return items

@app.route('/')
def index():
    if is_logged():
        items = carregar_dados()
        return render_template(
            'tabela.html',
            page_title=access_level[int(session['permission_level'])]['title'],
            header_title=access_level[int(session['permission_level'])]['title'],
            items=items,
            user=session['full_name'],
            color=access_level[int(session['permission_level'])]['color'],
            color_row_odd=access_level[int(session['permission_level'])]['color_row_odd'],
            color_row_even=access_level[int(session['permission_level'])]['color_row_even'])
    else:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', accept_imagefile=','.join(ALLOWED_MIMETYPES))
    elif request.method == 'POST':
        login = login_package.LoginHandler()
        try:
            login.validate_login(request.form['username'], request.form['password'])

            if 'biometry' not in request.files:
                raise LoginError(ExceptionCodes.LoginError.NO_FINGERPRINT)
            fingerprint_file = request.files['biometry']
            if fingerprint_file.filename == '':
                raise LoginError(ExceptionCodes.LoginError.NO_FINGERPRINT)
            if fingerprint_file.mimetype not in ALLOWED_MIMETYPES:
                raise LoginError(ExceptionCodes.LoginError.INVALID_FINGERPRINT_MIMETYPE)
            if fingerprint_file:
                fingerprint_filename = secure_filename(fingerprint_file.filename)
                fingerprint_file.save(os.path.join('temp', fingerprint_filename))
                with open(os.path.join('temp', fingerprint_filename), mode='rb') as f:
                    login.validate_fingerprint(f.read())
                session['user_id'] = login.session.user_id
                session['full_name'] = login.session.full_name
                session['permission_level'] = login.session.permission_level
                return redirect('/index')
            else:
                raise LoginError(ExceptionCodes.UNDEFINED_ERROR)

        except LoginError as e:
            if e.error_code == ExceptionCodes.LoginError.NO_USER:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    error_no_username=True,
                    username=request.form['username'])
            elif e.error_code == ExceptionCodes.LoginError.NO_PASSWORD:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    error_no_password=True,
                    username=request.form['username'])
            elif e.error_code == ExceptionCodes.LoginError.NO_FINGERPRINT:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    error_no_fingerprint=True,
                    username=request.form['username'])
            elif e.error_code == ExceptionCodes.LoginError.INVALID_FINGERPRINT_MIMETYPE:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    error_invalid_filetype=True,
                    username=request.form['username'])
            elif e.error_code == ExceptionCodes.LoginError.INVALID_USER_OR_PASSWORD:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    error_invalid_login=True,
                    username=request.form['username'])
            elif e.error_code == ExceptionCodes.LoginError.INVALID_FINGERPRINT:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    error_invalid_fingerprint=True,
                    username=request.form['username'])
            elif e.error_code == ExceptionCodes.LoginError.LOGIN_NOT_VALIDATE:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    error_login_not_validate=True,
                    username=request.form['username'])
            elif e.error_code == ExceptionCodes.LoginError.UNREGISTERED_FINGERPRINT:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    error_unregistered_fingerprint=True,
                    username=request.form['username'])
            elif e.error_code == ExceptionCodes.UNDEFINED_ERROR:
                return render_template(
                    'login.html',
                    accept_imagefile=','.join(ALLOWED_MIMETYPES),
                    unknown_error=True,
                    username=request.form['username'])


@app.route('/logout')
def logout():
    SYSTEM.finish()

    session.pop('user_id', None)
    session.pop('full_name', None)
    session.pop('permission_level', None)
    return redirect('/index')

@app.route('/item')
def item():
    if is_logged():
        items = carregar_dados()
        id = int(request.args.get('id'))
        for item in items:
            if item['id'] == id:
                return render_template(
                    'ver-mais.html',
                    page_title=item['Marca'],
                    header_title=access_level[int(session['permission_level'])]['title'],
                    item=item,
                    user='Edson',
                    color=access_level[int(session['permission_level'])]['color'])
        return make_response(
            render_template(
                'ver-mais.html',
                page_title='Item não encontrado',
                header_title=access_level[int(session['permission_level'])]['title'],
                item={ 'Erro': 'Item não encontrado' },
                user='Edson',
                color=access_level[int(session['permission_level'])]['color']), 404)
    else:
        return redirect('/login')

SYSTEM = System()
SYSTEM.start()