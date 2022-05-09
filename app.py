from datetime import date
import os
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@172.17.0.3:3306/bd_pixeon'

db = SQLAlchemy(app)

class Logins(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usuario = db.Column(db.String(50))  
    senha = db.Column(db.String(50))  

    def to_json(self):
        return {"usuário": self.usuario, "password": self.senha}

class Pacientes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(50))  
    data_de_nascimento = db.Column(db.Date())   
    
    def to_json(self):
        return {"id": self.id, "nome": self.nome,"data de nascimento": json.dumps(self.data_de_nascimento, default = dt_parser )}

db.create_all()

def dt_parser(dt):
    if isinstance(dt, date):
        return dt.isoformat()

#Buscar status do Servidor
@app.route("/healt", methods = ["GET"])
def busca_status_servidor():  
    
    return gera_response(200)

# Cadastrar
@app.route("/pacientes", methods=["POST"])
def cria_paciente():
    body = request.get_json()

    try:
        paciente = Pacientes(id=body["id"], nome=body["nome"], data_de_nascimento = body["data_de_nascimento"])
        db.session.add(paciente)
        db.session.commit()
        return gera_response(201, "Paciente", paciente.to_json(), "Paciente Criado com sucesso")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "Paciente", {}, "Erro ao cadastrar paciente")

# Atualizar Paciente
@app.route("/pacientes/<nome>", methods=["PUT"])
def atualiza_paciente(nome):
    paciente_objeto = Pacientes.query.filter_by(nome=nome).first()
    body = request.get_json()

    try:
        if('nome' in body):
            paciente_objeto.nome = body['nome']
        if('data_de_nascimento' in body):
            paciente_objeto.email = body['data_de_nascimento']
        
        db.session.add(paciente_objeto)
        db.session.commit()
        return gera_response(200, "Paciente: ", paciente_objeto.to_json(), "Paciente atualizado com sucesso")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "Paciente: ", {}, "Erro ao atualizar paciente")

# Selecionar Paciente por Nome
@app.route("/pacientes/<nome>", methods=["GET"])
def seleciona_paciente(nome):
    paciente_objeto = Pacientes.query.filter_by(nome=nome).first()
    paciente_json = paciente_objeto.to_json()

    return gera_response(200, "Paciente: ", paciente_json)

#Selecionar todos pacientes
@app.route("/pacientes", methods = ["GET"])
def seleciona_usuarios():
    pacientes_objetos = Pacientes.query.all()
    pacientes_json = [paciente.to_json() for paciente in pacientes_objetos]
    print(pacientes_json)
    return gera_response(200, "pacientes: ", pacientes_json)

# Deletar Paciente
@app.route("/pacientes/<nome>", methods=["DELETE"])
def deleta_paciente(nome):
    paciente_objeto = Pacientes.query.filter_by(nome=nome).first()

    try:
        db.session.delete(paciente_objeto)
        db.session.commit()
        return gera_response(200, "Paciente: ", paciente_objeto.to_json(), "Paciente deletado com sucesso")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "Paciente: ", {}, "Erro ao deletar")

#Login do paciente
@app.route("/login/<usuario> <senha>", methods=["GET"])
def seleciona_usuario(usuario,senha):
    paciente_objeto = Logins.query.filter_by(usuario=usuario, senha = senha).first()
    if not paciente_objeto:
        return gera_response(404)
    else:
        paciente_json = paciente_objeto.to_json()
   
        return gera_response(200, "Login: ", paciente_json)

#Gera response
def gera_response(status, nome_do_conteudo="", conteudo="", mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


app.run(host='localhost', debug=True)
