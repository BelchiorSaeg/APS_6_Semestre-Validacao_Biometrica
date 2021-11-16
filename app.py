from flask import Flask, render_template, request, make_response, url_for
from werkzeug.utils import redirect
from exceptions import ExceptionCodes
from login import LoginHandler, LoginError
app = Flask(__name__)

app.secret_key = '98cece9dc0a7d58b18cf8118f655ee5c9de42730c2a761cee92613c6b1b2b3cf'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        login = LoginHandler()
        try:
            login.validate_login(request.form['username'], request.form['password'])
        except LoginError as e:
            if e.error_code == ExceptionCodes.LoginError.NO_USER:
                return render_template('login.html', error_no_username=True, username=request.form['username'])
            if e.error_code == ExceptionCodes.LoginError.NO_PASSWORD:
                return render_template('login.html', error_no_password=True, username=request.form['username'])
            

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/tabela')
def tabela():
    return render_template(
        'tabela.html',
        page_title='Produtos agrícolas',
        header_title='Produtos agrícolas',
        items=items,
        user='Edson',
        color='#C4F8A4',
        color_row_odd='#A5B5C6',
        color_row_even='#A9BE9C')

@app.route('/item')
def item():
    id = int(request.args.get('id'))
    for item in items:
        if item['id'] == id:
            return render_template(
                'ver-mais.html',
                page_title=item['Marca'],
                header_title='Produtos agrícolas',
                item=item, user='Edson',
                color='#C4F8A4')
    return make_response(
        render_template(
            'ver-mais.html',
            page_title='Item não encontrado',
            header_title='Produtos agrícolas',
            item={ 'Erro': 'Item não encontrado' },
            user='Edson', color='#C4F8A4'), 404)