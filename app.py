from flask import Flask, render_template, request, redirect, url_for, Response
import json
import os
from datetime import datetime
import csv
from io import StringIO

app = Flask(__name__)
DATA_FILE = 'entradas.json'

def carregar_entradas():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def salvar_entradas(entradas):
    with open(DATA_FILE, 'w') as f:
        json.dump(entradas, f, indent=4)

@app.route('/')
def index():
    entradas = carregar_entradas()
    saldo = sum(e['valor'] for e in entradas)
    return render_template('index.html', entradas=entradas[::-1], saldo=saldo)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    entradas = carregar_entradas()
    nova_entrada = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
        'descricao': request.form['descricao'],
        'valor': float(request.form['valor']),
        'data': request.form['data']
    }
    entradas.append(nova_entrada)
    salvar_entradas(entradas)
    return redirect(url_for('index'))

@app.route('/editar/<entrada_id>', methods=['POST'])
def editar(entrada_id):
    entradas = carregar_entradas()
    for entrada in entradas:
        if entrada['id'] == entrada_id:
            entrada['descricao'] = request.form['descricao']
            entrada['valor'] = float(request.form['valor'])
            entrada['data'] = request.form['data']
            salvar_entradas(entradas)
            return redirect(url_for('index'))
    return "Entrada não encontrada", 404

@app.route('/excluir/<entrada_id>', methods=['POST'])
def excluir(entrada_id):
    entradas = carregar_entradas()
    entradas = [e for e in entradas if e['id'] != entrada_id]
    salvar_entradas(entradas)
    return redirect(url_for('index'))

@app.route('/relatorio')
def relatorio():
    entradas = carregar_entradas()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Descrição', 'Valor (MT)', 'Data'])
    for e in entradas:
        cw.writerow([e['descricao'], f"{e['valor']:.2f}", e['data']])
    
    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype='text/csv',
        headers={
            "Content-Disposition": "attachment;filename=relatorio_entradas.csv"
        }
    )

if __name__ == '__main__':
    app.run(debug=True)
