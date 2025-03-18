# app.py

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from email.message import EmailMessage
import smtplib
import pandas as pd
import psycopg2
import locale
import json

app = Flask(__name__)


class InicializaBase:

    def __init__(self):
        self.con = psycopg2.connect(host='127.0.0.1', port=5432, database='postgres', user='postgres', password='masterkey')
        self.con.autocommit = True

class InsertBase:

    def __init__(self):
        self.con = InicializaBase().con

    def insertSale(self, usuario_id, empresa_id, venda, formaPagamento, compromisso, data):
        cur = self.con.cursor()
        cur.execute("INSERT INTO emanuela.vendas (user_id, empresa_id, valor, pg_id, descricao, data_venda) VALUES (%s, %s, %s, %s, %s, %s)",(usuario_id, empresa_id, venda, formaPagamento, compromisso, data))
        cur.close()

class GetBase:

    def __init__(self):
        self.con = InicializaBase().con

    def getEmpresas(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM emanuela.empresas")
        empresas = cur.fetchall()
        cur.close()
        return empresas
    
    def getEmpresasId(self, empresa):
        cur = self.con.cursor()
        cur.execute(f"SELECT id FROM emanuela.empresas where nome = '{empresa}'")
        empresas = cur.fetchall()
        cur.close()
        return empresas[0][0]
    
    def getFormasPagamento(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM emanuela.type_pg")
        formasPagamento = cur.fetchall()
        cur.close()
        return formasPagamento
    
    def getUsuarios(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM emanuela.usuarios")
        usuarios = cur.fetchall()
        cur.close()
        return usuarios
    
    def getUsuariosId(self, usuario):
        cur = self.con.cursor()
        cur.execute(f"SELECT id FROM emanuela.usuarios where nome = '{usuario}'")
        usuarios = cur.fetchall()
        cur.close()
        return usuarios[0][0]
    
    def getFormasPagamento(self):
        cur = self.con.cursor()
        cur.execute(f"SELECT * FROM emanuela.type_pg")
        pg = cur.fetchall()
        cur.close()
        return pg
    
    def getFormasPagamentoId(self, pg):
        cur = self.con.cursor()
        cur.execute(f"SELECT id FROM emanuela.type_pg where pg = '{pg}'")
        pg = cur.fetchall()
        cur.close()
        return pg[0][0]
    
    def getVendas(self, sql):
        cur = self.con.cursor()
        cur.execute(sql)
        vendas = cur.fetchall()
        cur.close()
        return vendas

    
class DeleteInfo:

    def __init__(self):
        self.con = InicializaBase().con

    def deleteSale(self, id, data, empresa_id, pg_id):
        cur = self.con.cursor()
        cur.execute(f"DELETE FROM emanuela.vendas WHERE user_id = {id} and data_venda = '{data}' and empresa_id = {empresa_id} and pg_id = {pg_id}")
        cur.close()

app.secret_key = 'sua_chave_secreta_aqui'  # Defina uma chave secreta para a sessão

# Função para verificar se o usuário está logado
def verificar_login():
    # Aqui você adicionaria a lógica para verificar se o usuário está logado
    # Por exemplo, verificar se há uma sessão ativa ou um cookie de autenticação
    # Se o usuário não estiver logado, redirecione para a página de login
    return False  # Altere para True se o usuário estiver logado

# Rota para a página inicial
@app.route('/')
def home():
    
    if verificar_login():
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

# Rota para lidar com o login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # Aqui você adicionaria a lógica para verificar as credenciais
    usuarios = GetBase().getUsuarios()
    for usuario in usuarios:
        if usuario[1] == username and usuario[3] == password:
            session['username'] = username
            session['last_login'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            return redirect(url_for('dashboard'))
    return "Login falhou!"

# Rota para lidar com o logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('last_login', None)
    return redirect(url_for('home'))


# Rota para a página do dashboard (após o login)
@app.route('/dashboard')
def dashboard():
    
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'], last_login=session['last_login'])
    
    return redirect(url_for('home'))

@app.route('/deleteSale', methods=['POST'])
def deleteSale():
    
    if request.method == 'POST':
        if 'username' in session:
            id = GetBase().getUsuariosId(session['username'])
            data = request.json['date']
            
            empresa = request.json['company']
            empresa_id = GetBase().getEmpresasId(empresa)
            
            pg = request.json['pag']
            pg_id = GetBase().getFormasPagamentoId(pg)
            

            DeleteInfo().deleteSale(id, data, empresa_id, pg_id)
            return "Venda deletada com sucesso!"
    
    return redirect(url_for('cadastroVendas'))


@app.route('/cadastroVendas', methods=['GET', 'POST'])
def cadastroVendas():
    
    if 'username' in session:
        if request.method == 'GET':
            empresas = GetBase().getEmpresas()
            formasPagamento = GetBase().getFormasPagamento()
            empresas = [empresa[1] for empresa in empresas]
            formasPagamento = [forma[1] for forma in formasPagamento]

            return render_template('cadastroVendas.html', empresas=empresas, formasPagamento=formasPagamento)
        
        if request.method == 'POST':

            data = request.json['date']
            compromisso = request.json['title']

            empresa = request.json['company']
            if empresa == 'Teste':
                empresa_id = 1
            elif empresa == 'JBL':
                empresa_id = 2
            elif empresa == 'Brasil Sul':
                empresa_id = 3

            venda = request.json['value']

            formaPagamento = request.json['pag']
            if formaPagamento == 'Dinheiro':
                formaPagamento = 4
            elif formaPagamento == 'Crédito':
                formaPagamento = 2
            elif formaPagamento == 'Débito':
                formaPagamento = 1
            elif formaPagamento == 'PIX':
                formaPagamento = 3

            usuario_id = GetBase().getUsuariosId(session['username'])

            InsertBase().insertSale(usuario_id, empresa_id, venda, formaPagamento, compromisso, data)
            # Aqui você pode adicionar a lógica para salvar o compromisso em um banco de dados ou arquivo
            return "Compromisso agendado com sucesso!"
        
        return render_template('cadastroVendas.html')
    
    return redirect(url_for('home'))

@app.route('/visualizar', methods=['POST'])
def visualizar():
    if 'username' in session:
        if request.method == 'POST':
            formaPg = request.json['formaPg']
            empresa = request.json['company']
            usuario = request.json['user']
            dataInicial = request.json['dataInicial']
            dataFinal = request.json['dataFinal']
            
            if formaPg == 'todos' and empresa == 'todas' and usuario == 'todos':
                sql = f"SELECT * FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}'"
                sqlTotal = f"SELECT SUM(valor) FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}'"
            elif formaPg != 'todos' and empresa != 'todas' and usuario != 'todos':
                sql = f"SELECT * FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and pg_id = {formaPg} and empresa_id = {empresa} and user_id = {usuario}"
                sqlTotal = f"SELECT SUM(valor) FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and pg_id = {formaPg} and empresa_id = {empresa} and user_id = {usuario}"
            elif formaPg == 'todos' and empresa != 'todas' and usuario != 'todos':
                sql = f"SELECT * FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and empresa_id = {empresa} and user_id = {usuario}"
                sqlTotal = f"SELECT SUM(valor) FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and empresa_id = {empresa} and user_id = {usuario}"
            elif formaPg != 'todos' and empresa == 'todas' and usuario != 'todos':
                sql = f"SELECT * FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and pg_id = {formaPg} and user_id = {usuario}"
                sqlTotal = f"SELECT SUM(valor) FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and pg_id = {formaPg} and user_id = {usuario}"
            elif formaPg != 'todos' and empresa != 'todas' and usuario == 'todos':
                sql = f"SELECT * FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and pg_id = {formaPg} and empresa_id = {empresa}"
                sqlTotal = f"SELECT SUM(valor) FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and pg_id = {formaPg} and empresa_id = {empresa}"
            elif formaPg == 'todos' and empresa == 'todas' and usuario != 'todos':
                sql = f"SELECT * FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and user_id = {usuario}"
                sqlTotal = f"SELECT SUM(valor) FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and user_id = {usuario}"
            elif formaPg == 'todos' and empresa != 'todas' and usuario == 'todos':
                sql = f"SELECT * FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and empresa_id = {empresa}"
                sqlTotal = f"SELECT SUM(valor) FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and empresa_id = {empresa}"
            elif formaPg != 'todos' and empresa == 'todas' and usuario == 'todos':
                sql = f"SELECT * FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and pg_id = {formaPg}"
                sqlTotal = f"SELECT SUM(valor) FROM emanuela.vendas WHERE data_venda >= '{dataInicial}' and data_venda <= '{dataFinal}' and pg_id = {formaPg}"
            
            vendas = GetBase().getVendas(sql)
            vendasTotal = GetBase().getVendas(sqlTotal)
            
            df = pd.DataFrame(vendas, columns=['ID', 'User ID', 'Empresa ID', 'Valor', 'PG ID', 'Descrição', 'Data Venda'])
            dfSelect = df[['Valor', 'Descrição', 'Data Venda']]
            dfSelectValues = dfSelect.values.tolist()
            dfTotal = pd.DataFrame(vendasTotal, columns=['Total'])
            vendasTotalList = dfTotal['Total'].values.tolist()
            


            return jsonify(success=True, eventos=dfSelectValues, total=vendasTotalList)
            
    return jsonify(success=False, error="Usuário não autenticado")

@app.route('/relatorio', methods=['GET', 'POST'])
def relatorio():

    getFormasPagamento = GetBase().getFormasPagamento()
    formas_pagamento = {forma[0]: forma[1] for forma in getFormasPagamento}
    formas_pagamento = pd.DataFrame(formas_pagamento.items(), columns=['ID', 'Forma de Pagamento'])
    formas_pagamento = formas_pagamento.to_dict(orient='records')
    formas_pagamento.append({'ID': 'todos', 'Forma de Pagamento': 'Todos'})

    getNomesEmpresas = GetBase().getEmpresas()
    empresas = {empresa[0]: empresa[1] for empresa in getNomesEmpresas}
    empresas = pd.DataFrame(empresas.items(), columns=['ID', 'Empresa'])
    empresas = empresas.to_dict(orient='records')
    empresas.append({'ID': 'todas', 'Empresa': 'Todas'})

    getUsuarios = GetBase().getUsuarios()
    usuarios = {usuario[0]: usuario[1] for usuario in getUsuarios}
    usuarios = pd.DataFrame(usuarios.items(), columns=['ID', 'Usuário'])
    usuarios = usuarios.to_dict(orient='records')
    usuarios.append({'ID': 'todos', 'Usuário': 'Todos'})
    
    
    return render_template('relatorio.html', formas_pagamento=formas_pagamento, empresas=empresas, usuarios=usuarios)


@app.route('/download')
def download():
    
    if 'username' in session:
        return render_template('download.html')
    
    return redirect(url_for('home'))

@app.route('/contato')
def contato():
    
    if 'username' in session:
        return render_template('contato.html')
    
    return redirect(url_for('home'))

@app.route('/enviarContato', methods=['POST'])
def enviarContato():
        
    nome = request.form['nome']
    email = request.form['email']
    mensagem = request.form['mensagem']
    senha = 'ecpoziyhpapjuefz'
    username = 'enviador.marketing.calliari@gmail.com'
    msg = EmailMessage()
    msg['Subject'] = "CONTATO CALLIARI REPRESENTAÇÕES"
    msg['From'] = 'enviador.marketing.calliari@gmail.com'
    msg['To'] = email
    msg.set_content(f'''Prezado(a/o), segue contato preliminar.''')
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        
        smtp.login(username, senha)
        smtp.send_message(msg)
    
    return redirect(url_for('dashboard')) #TODO: Criar uma tela para mensagem enviada com sucesso

@app.route('/whatsapp')
def whatsapp():
    
    numero = '5551991214191'
    mensagem = 'Olá, como posso ajudar?'
    link = f'https://api.whatsapp.com/send?phone={numero}&text={mensagem}'
    
    
    return render_template('whatsapp.html', link=link)

if __name__ == "__main__":
    app.run(debug=True, host= '0.0.0.0', port=5490)
