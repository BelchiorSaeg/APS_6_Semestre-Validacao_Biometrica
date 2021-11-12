from login import L
from flask import Flask, render_template, request
app = Flask(__name__)

items = [
    {
        'id': 111,
        'Marca': 'Giga',
        'Caminho': 'Grande',
        'Cerro': 'Pequeno'
    },
    {
        'id': 555,
        'Marca': 'Giga',
        'Caminho': 'Pequeno',
        'Cerro': 'Rustico'
    },
    {
        'id': 999,
        'Marca': 'Humel',
        'Caminho': 'Fático',
        'Cerro': 'Moderno',
    }
]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        pass

@app.route('/tabela')
def tabela():
    return render_template('tabela.html', page_title='Produtos agrícolas', header_title='Produtos agrícolas', items=items, user='Edson', color='#C4F8A4', color_row_odd='#A5B5C6', color_row_even='#A9BE9C')

@app.route('/item')
def item():
    id = int(request.args.get('id'))
    for item in items:
        if item['id'] == id:
            return render_template('ver-mais.html', page_title=item['Marca'], header_title='Produtos agrícolas', item=item, user='Edson', color='#C4F8A4')
    return render_template('ver-mais.html', page_title='Item não encontrado', header_title='Produtos agrícolas', item={ 'Erro': 'Item não encontrado' }, user='Edson', color='#C4F8A4')