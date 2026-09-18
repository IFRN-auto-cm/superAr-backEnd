import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import MySQLdb
from MySQLdb.cursors import DictCursor
import logging
# import paho.mqtt.client as mqtt
import mqtt_service_client
import json
import re
import redisAccess as redis
from mySocketio import init_socketio, emitir_status_ar, socketio, emitir_status_all_ar
# Importando o models
from sqlalchemy import select, case
from database import SessionLocal
from models.models import (
    Comandos,
    ModelosMarcas,
    Salas,
    ArCadastrados,
    ModelosMarcasComando,
)

app = Flask(__name__)
CORS(app)
init_socketio(app)
load_dotenv()
redis.teste()

# logger = logging.getLogger("AIPO_NFC_READER")
# logging.basicConfig(filename='allLogs.log', encoding='ISO-8859-1', level=logging.DEBUG)

# # handle para lidar com o terminal
# terminal_logger = logging.StreamHandler()
# terminal_logger.setLevel(logging.DEBUG)

# # handle para lidar com o arquivo
# file_logger = logging.FileHandler("nfcReader.log", encoding='ISO-8859-1')
# file_logger.setLevel(logging.WARNING)

# # create formatter
# formatter = logging.Formatter('%(name)s:%(levelname)s \t- - %(asctime)s %(message)s', datefmt='[%d/%m/%Y %H:%M:%S]')

# # add formatter to handles
# terminal_logger.setFormatter(formatter)
# file_logger.setFormatter(formatter)

# # add handles to logger
# logger.addHandler(terminal_logger)
# logger.addHandler(file_logger)

def salvar_status_no_banco(device, state, sensors, diagnostics, statistics):
    conn = get_db()
    cursor = conn.cursor()

    print("dados: ", device)

    # try:
    #     cursor.execute(
    #         """
    #         INSERT INTO historico_comandos
    #             (atuador, ir_cmd, tamanho, tipo_comando)
    #         VALUES
    #             (%s, %s, %s, %s)
    #         """,
    #         (
    #             atuador,
    #             ir_cmd,
    #             length,
    #             cmd_type
    #         )
    #     )

    #     conn.commit()
    #     registro_id = cursor.lastrowid

    #     return {
    #         "id": registro_id
    #     }

    # except Exception:
    #     conn.rollback()
    #     raise

    # finally:
    #     cursor.close()

def normalizar(texto):
    # Encontra o primeiro número na string
    numero = re.search(r'\d+', texto)

    if not numero:
        return re.sub(r'\s+', '', texto).lower()

    numero = numero.group()

    # Remove todos os números
    descricao = re.sub(r'\d+', '', texto)

    # Remove todos os espaços e converte para minúsculas
    descricao = re.sub(r'\s+', '', descricao).lower()

    return f"{descricao} {numero}"

def publicar_mqtt(endereco, payload):
    return mqtt_service_client.publicar_comando_ar(
        atuador=endereco,
        payload=payload
    )

def get_db():
    return MySQLdb.connect(
        host= os.getenv("HOST_DATABASE"),
        user= os.getenv("MYSQL_USER"),
        passwd= os.getenv("MYSQL_PASSWORD"),
        db= os.getenv("MYSQL_DATABASE"),
        port= int(os.getenv("DB_PORT")),
        cursorclass=DictCursor,
    )

def executar_insert_many(sql, valores):
    conn = get_db()
    cursor = conn.cursor()
    print(sql, valores)
    try:
        cursor.executemany(sql, valores)
        conn.commit()
        cursor.close()

    except Exception as erro:
        conn.rollback()
        raise erro

    finally:
        cursor.close()
        conn.close()

def executar_insert(sql, valores=None):
    conn = get_db()
    cursor = conn.cursor()

    try:
        if (valores==None):
            cursor.execute(sql)
        else:
            cursor.execute(sql,valores)
        conn.commit()
        return cursor.lastrowid

    except Exception as erro:
        conn.rollback()
        raise erro

    finally:
        cursor.close()
        conn.close()

def executar_select(sql, valores=None): 
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, valores or ())
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def executar_select1(sql, valores): 
    conn = get_db()
    cursor = conn.cursor()
    print(sql)
    print(valores)
    try:
        cursor.execute(sql, '34')
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def executar_delete(sql, valores=None):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, valores or ())
        conn.commit()
        return cursor.rowcount

    except Exception as erro:
        conn.rollback()
        raise erro

    finally:
        cursor.close()
        conn.close()

def executar_update(sql, valores=None):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, valores or ())
        conn.commit()
        return cursor.rowcount

    except Exception as erro:
        conn.rollback()
        raise erro

    finally:
        cursor.close()
        conn.close()

# =========================
# ROTAS - SQLAlchemy
# =========================

@app.route("/comandos/<int:comando_id>", methods=["DELETE"])
def deletar_comando(comando_id):
    try:
        with SessionLocal() as session:
            comando = session.get(Comandos, comando_id)

            if comando is None:
                return jsonify({
                    "status": "erro",
                    "mensagem": "comando não encontrado"
                }), 404

            session.delete(comando)
            session.commit()

        return jsonify({
            "status": "ok",
            "mensagem": "comando deletado com sucesso"
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/modelos-marcas/<int:marcaModelo_id>", methods=["DELETE"])
def deletar_marcaModelo(marcaModelo_id):
    try:
        with SessionLocal() as session:
            marca_modelo = session.get(ModelosMarcas, marcaModelo_id)

            if marca_modelo is None:
                return jsonify({
                    "status": "erro",
                    "mensagem": "comando não encontrado"
                }), 404

            session.delete(marca_modelo)
            session.commit()

        return jsonify({
            "status": "ok",
            "mensagem": "comando deletado com sucesso"
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500

#Rota comandos "migrada"
@app.route("/comandos", methods=["POST"])
def inserir_comando():
    data = request.json or {}
    nome = normalizar(data.get("nome", ""))

    if not nome:
        return jsonify({
            "status": "erro",
            "mensagem": "nome é obrigatório"
        }), 400

    try:
        with SessionLocal() as session:
            novo_comando = Comandos(nome=nome)
            session.add(novo_comando)
            session.commit()
            session.refresh(novo_comando)
            novo_id = novo_comando.id

        return jsonify({
            "status": "ok",
            "id": novo_id
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/modelos-marcas", methods=["POST"])
def inserir_modelo_marca():
    data = request.json or {}

    marca = data.get("marca")
    modelo = data.get("modelo")

    if not marca or not modelo:
        return jsonify({
            "status": "erro",
            "mensagem": "marca e modelo são obrigatórios"
        }), 400

    try:
        with SessionLocal() as session:
            novo = ModelosMarcas(
                marca=marca,
                modelo=modelo
            )
            session.add(novo)
            session.commit()
            session.refresh(novo)
            novo_id = novo.id

        return jsonify({
            "status": "ok",
            "id": novo_id
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/modelos-marcas-comandos", methods=["POST"])
def associar_modelo_comando():
    data = request.json or {}

    modelo_marcas = data.get("modelo_marcas")
    comandos = data.get("comandos")

    if not modelo_marcas or not comandos:
        return jsonify({
            "status": "erro",
            "mensagem": "modelo_marcas e pelo menos 1 comando são obrigatórios"
        }), 400

    try:
        with SessionLocal() as session:
            valores = [
                ModelosMarcasComando(
                    modelo_marcas=modelo_marcas,
                    comando=comando["id"],
                    comando_valor=str(comando["valor"])
                )
                for comando in comandos
            ]

            session.add_all(valores)
            session.commit()

        return jsonify({"status": "ok"})

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/ar-cadastrados", methods=["POST"])
def inserir_ar_cadastrado():
    data = request.json or {}

    # temperatura_medida = data.get("temperatura_medida")
    temperatura_referencia = data.get("temperatura_referencia")
    modelo_marca = data.get("marcaModeloId")
    status = data.get("status")
    atuador = data.get("atuador")
    nome = data.get("nome")
    sala = data.get("sala")

    if not modelo_marca:
        return jsonify({
            "status": "erro",
            "mensagem": "modelo_marca é obrigatório"
        }), 400

    try:
        with SessionLocal() as session:
            novo = ArCadastrados(
                temperatura_referencia=temperatura_referencia,
                modelo_marca=modelo_marca,
                status=status,
                atuador=atuador,
                nome=nome,
                sala=sala
            )
            session.add(novo)
            session.commit()
            session.refresh(novo)
            novo_id = novo.id

        return jsonify({
            "status": "ok",
            "id": novo_id
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/ar-cadastrados/<int:ar_cadastrado_id>", methods=["POST"])
def update_ar_cadastrado(ar_cadastrado_id):
    data = request.json or {}

    temperatura_medida = 0
    temperatura_referencia = data.get("temperatura_referencia")
    modelo_marca = data.get("marcaModeloId")
    status = data.get("status")
    atuador = data.get("atuador")
    nome = data.get("nome")
    sala = data.get("sala")

    if not modelo_marca:
        return jsonify({
            "status": "erro",
            "mensagem": "modelo_marca é obrigatório"
        }), 400

    if not sala:
        return jsonify({
            "status": "erro",
            "mensagem": "sala é obrigatória"
        }), 400

    try:
        with SessionLocal() as session:
            ar = session.get(ArCadastrados, ar_cadastrado_id)

            if ar is None:
                return jsonify({
                    "status": "ok",
                    "linhas_afetadas": 0
                })

            ar.temperatura_medida = temperatura_medida
            ar.temperatura_referencia = temperatura_referencia
            ar.modelo_marca = modelo_marca
            ar.status = status
            ar.atuador = atuador
            ar.nome = nome
            ar.sala = sala

            session.commit()

        return jsonify({
            "status": "ok",
            "linhas_afetadas": 1
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/salas", methods=["POST"])
def inserir_sala():
    data = request.json or {}

    nome = data.get("nome")
    predio = data.get("predio")
    numero_de_ar = data.get("numero_de_ar", 0)
    ar1 = data.get("ar1")
    ar2 = data.get("ar2")
    ar3 = data.get("ar3")
    ar4 = data.get("ar4")

    if not nome:
        return jsonify({
            "status": "erro",
            "mensagem": "nome é obrigatório"
        }), 400

    try:
        with SessionLocal() as session:
            nova_sala = Salas(
                nome=nome,
                predio=predio,
                numero_de_ar=numero_de_ar,
                ar1=ar1,
                ar2=ar2,
                ar3=ar3,
                ar4=ar4
            )
            session.add(nova_sala)
            session.commit()
            session.refresh(nova_sala)
            novo_id = nova_sala.id

        return jsonify({
            "status": "ok",
            "id": novo_id
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/ar-cadastrados/<int:ar_cadastrado_id>/enviar-comando", methods=["POST"])
def enviar_comando_ar(ar_cadastrado_id):
    data = request.json or {}
    comando_nome = data.get("comando_nome")

    if not comando_nome:
        return jsonify({
            "status": "erro",
            "mensagem": "comando_nome é obrigatório"
        }), 400

    try:
        with SessionLocal() as session:
            stmt = (
                select(
                    ArCadastrados.id.label("ar_id"),
                    ArCadastrados.nome.label("ar_nome"),
                    ArCadastrados.atuador,
                    ArCadastrados.modelo_marca,
                    Comandos.id.label("comando_id"),
                    Comandos.nome.label("comando_nome"),
                    ModelosMarcasComando.comando_valor
                )
                .join(
                    ModelosMarcasComando,
                    ModelosMarcasComando.modelo_marcas == ArCadastrados.modelo_marca
                )
                .join(
                    Comandos,
                    Comandos.id == ModelosMarcasComando.comando
                )
                .where(
                    ArCadastrados.id == ar_cadastrado_id,
                    Comandos.nome == comando_nome
                )
            )

            dados = session.execute(stmt).mappings().first()

            if dados is None:
                return jsonify({
                    "status": "erro",
                    "mensagem": "Comando não cadastrado para o modelo deste ar-condicionado"
                }), 404

            if not dados["atuador"]:
                return jsonify({
                    "status": "erro",
                    "mensagem": "Este ar-condicionado não possui atuador cadastrado"
                }), 400

            vetor = json.loads(dados["comando_valor"])

        referencia = 0
        partes = comando_nome.casefold().split()

        if comando_nome.casefold() == "desligar":
            cmd_type = "desligar"
        elif partes and partes[0] == "ligar":
            cmd_type = "ligar"
            referencia = comando_nome.split()[1]
        else:
            cmd_type = comando_nome.casefold()

        payload = {
            "irCmd": vetor,
            "length": len(vetor),
            "cmdType": cmd_type,
            "ref": referencia
        }

        endereco_atuador = dados["atuador"]
        publicar_mqtt(endereco_atuador, payload)

        return jsonify({
            "status": "ok",
            "mensagem": "Comando enviado com sucesso",
            "endereco": endereco_atuador,
            "payload": payload
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


def lista_salas():
    try:
        with SessionLocal() as session:
            stmt = (
                select(
                    Salas.id,
                    Salas.nome,
                    Salas.codigo,
                    Salas.predio
                )
                .order_by(Salas.codigo, Salas.nome)
            )
            resultado = session.execute(stmt).mappings().all()

        return {
            "status": "ok",
            "dados": [dict(row) for row in resultado]
        }

    except Exception as erro:
        import traceback
        traceback.print_exc()
        return {
            "status": "erro",
            "mensagem": str(erro)
        }


@app.route("/salas", methods=["GET"])
def api_lista_salas():
    salas = lista_salas()

    if salas["status"] == "ok":
        return jsonify(salas)

    return jsonify(salas), 500


@app.route("/getAddFomrArData", methods=["GET"])
def getDataToAddFormAr():
    salas = lista_salas()
    marca_modelo = listar_modelos_marcas()

    if salas["status"] != "ok":
        return jsonify(salas), 500

    if marca_modelo["status"] != "ok":
        return jsonify(marca_modelo), 500

    return jsonify({
        "status": "ok",
        "salas": salas["dados"],
        "marcaModelo": marca_modelo["dados"]
    })


@app.route("/getEditFomrArData/<int:Ar_id>", methods=["GET"])
def getDataToEditFormAr(Ar_id):
    salas = lista_salas()
    marca_modelo = listar_modelos_marcas()

    if salas["status"] != "ok":
        return jsonify(salas), 500

    if marca_modelo["status"] != "ok":
        return jsonify(marca_modelo), 500

    try:
        with SessionLocal() as session:
            stmt = (
                select(
                    ArCadastrados.id,
                    ArCadastrados.nome.label("nome_ar"),
                    ArCadastrados.temperatura_referencia,
                    Salas.nome.label("sala_nome"),
                    Salas.id.label("sala_id"),
                    ModelosMarcas.id.label("mm_id"),
                    ModelosMarcas.marca,
                    ModelosMarcas.modelo,
                    ArCadastrados.atuador
                )
                .outerjoin(Salas, ArCadastrados.sala == Salas.id)
                .outerjoin(
                    ModelosMarcas,
                    ArCadastrados.modelo_marca == ModelosMarcas.id
                )
                .where(ArCadastrados.id == Ar_id)
            )

            resultado = session.execute(stmt).mappings().all()

        resultado = {
            "editAr": [dict(row) for row in resultado],
            "salas": salas["dados"],
            "marcasModelos": marca_modelo["dados"]
        }

        return jsonify({
            "status": "ok",
            "dados": resultado
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/updateModelosComando", methods=["POST"])
def updateModelosComando():
    data = request.json or {}

    try:
        marca = data["marcaValue"]
        modelo = data["modeloValue"]
        modelo_marcas_id = data["mmId"]
        comandos = data["comandos"]

        with SessionLocal() as session:
            modelo_marca = session.get(ModelosMarcas, modelo_marcas_id)

            if modelo_marca is None:
                return jsonify({
                    "status": "erro",
                    "mensagem": "modelo/marca não encontrado"
                }), 404

            modelo_marca.marca = marca
            modelo_marca.modelo = modelo

            for comando in comandos:
                comando_id = comando["id"]
                comando_valor = comando.get("valor")

                stmt = (
                    select(ModelosMarcasComando)
                    .where(
                        ModelosMarcasComando.modelo_marcas == modelo_marcas_id,
                        ModelosMarcasComando.comando == comando_id
                    )
                )
                associacao = session.execute(stmt).scalar_one_or_none()

                if comando_valor is None:
                    if associacao is not None:
                        session.delete(associacao)
                else:
                    valor = "".join(str(comando_valor))

                    if associacao is None:
                        associacao = ModelosMarcasComando(
                            modelo_marcas=modelo_marcas_id,
                            comando=comando_id,
                            comando_valor=valor
                        )
                        session.add(associacao)
                    else:
                        associacao.comando_valor = valor

            session.commit()

        return jsonify({"status": "ok"})

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


def listar_modelos_marcas():
    try:
        with SessionLocal() as session:
            stmt = (
                select(
                    ModelosMarcas.id,
                    ModelosMarcas.marca,
                    ModelosMarcas.modelo
                )
                .order_by(ModelosMarcas.marca, ModelosMarcas.modelo)
            )
            resultado = session.execute(stmt).mappings().all()

        return {
            "status": "ok",
            "dados": [dict(row) for row in resultado]
        }

    except Exception as erro:
        return {
            "status": "erro",
            "mensagem": str(erro)
        }


@app.route("/modelos-marcas", methods=["GET"])
def api_listar_modelos_marcas():
    valor = listar_modelos_marcas()

    if valor["status"] == "ok":
        return jsonify(valor)

    return jsonify(valor), 500


@app.route("/edite-modelos-marcas/<int:modelo_marca_id>", methods=["GET"])
def listar_modelos_marcas1(modelo_marca_id):
    try:
        with SessionLocal() as session:
            marca_stmt = (
                select(
                    ModelosMarcas.id,
                    ModelosMarcas.marca,
                    ModelosMarcas.modelo
                )
                .where(ModelosMarcas.id == modelo_marca_id)
                .order_by(ModelosMarcas.marca, ModelosMarcas.modelo)
            )
            marca_modelo = session.execute(marca_stmt).mappings().first()

            if marca_modelo is None:
                return jsonify({
                    "status": "erro",
                    "mensagem": "modelo/marca não encontrado"
                }), 404

            cadastrado = case(
                (ModelosMarcasComando.id.is_(None), False),
                else_=True
            ).label("cadastrado_no_modelo")

            comandos_stmt = (
                select(
                    Comandos.id.label("comando_id"),
                    Comandos.nome.label("comando_nome"),
                    cadastrado
                )
                .outerjoin(
                    ModelosMarcasComando,
                    (
                        (ModelosMarcasComando.comando == Comandos.id)
                        & (ModelosMarcasComando.modelo_marcas == modelo_marca_id)
                    )
                )
                .order_by(Comandos.nome)
            )

            comandos = session.execute(comandos_stmt).mappings().all()

        return jsonify({
            "marcaModelo": dict(marca_modelo),
            "comandos": [dict(row) for row in comandos],
            "status": "ok"
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/modelos-marcas/<int:modelo_marca_id>/comandos", methods=["GET"])
def listar_comandos_por_modelo_marca(modelo_marca_id):
    try:
        with SessionLocal() as session:
            stmt = (
                select(
                    ModelosMarcasComando.id.label("associacao_id"),
                    ModelosMarcas.id.label("modelo_marca_id"),
                    ModelosMarcas.marca,
                    ModelosMarcas.modelo,
                    Comandos.id.label("comando_id"),
                    Comandos.nome.label("comando_nome"),
                    ModelosMarcasComando.comando_valor
                )
                .join(
                    ModelosMarcas,
                    ModelosMarcas.id == ModelosMarcasComando.modelo_marcas
                )
                .join(
                    Comandos,
                    Comandos.id == ModelosMarcasComando.comando
                )
                .where(ModelosMarcas.id == modelo_marca_id)
                .order_by(Comandos.nome)
            )

            resultado = session.execute(stmt).mappings().all()

        return jsonify({
            "status": "ok",
            "dados": [dict(row) for row in resultado]
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/comandos", methods=["GET"])
def listar_comandos():
    try:
        with SessionLocal() as session:
            stmt = (
                select(Comandos.id, Comandos.nome)
                .order_by(Comandos.nome)
            )
            resultado = session.execute(stmt).mappings().all()

        return jsonify({
            "status": "ok",
            "dados": [dict(row) for row in resultado]
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/ar-cadastrados", methods=["GET"])
def listar_ar_cadastrados():
    try:
        with SessionLocal() as session:
            stmt = (
                select(
                    ArCadastrados.id,
                    ArCadastrados.nome.label("nome_ar"),
                    ArCadastrados.temperatura_referencia,
                    Salas.nome.label("sala_nome"),
                    Salas.codigo.label("sala_cod"),
                    ModelosMarcas.marca,
                    ModelosMarcas.modelo,
                    ArCadastrados.atuador
                )
                .outerjoin(Salas, ArCadastrados.sala == Salas.id)
                .outerjoin(
                    ModelosMarcas,
                    ArCadastrados.modelo_marca == ModelosMarcas.id
                )
                .order_by(Salas.nome, ArCadastrados.nome)
            )

            resultado = [dict(row) for row in session.execute(stmt).mappings().all()]

        for ar in resultado:
            arStatus = redis.consultar_estado_dispositivo(ar["id"])

            if arStatus is not None:
                ar["temperatura_medida"] = arStatus["temperatura_medida"]
                ar["status"] = "ligado" if arStatus["power"] else "desligado"
            else:
                ar["status"] = "desconhecido"
                ar["temperatura_medida"] = "desconhecido"

        return jsonify({
            "status": "ok",
            "dados": resultado
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@app.route("/enviar-comando/<int:ar_cadastrado_id>", methods=["GET"])
def acionar_comando(ar_cadastrado_id):
    data = request.json or {}
    comando = data.get("comando")

    if not comando:
        return jsonify({
            "status": "erro",
            "mensagem": "comando é obrigatório"
        }), 400

    # Esta rota já existia no arquivo original, mas não possuía
    # implementação. Mantida sem acesso ao banco.
    return jsonify({
        "status": "ok",
        "mensagem": "Rota ainda sem implementação",
        "ar_cadastrado_id": ar_cadastrado_id,
        "comando": comando
    })


@app.post("/internal/mqtt/status")
def registrar_status_mqtt():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "erro": "Corpo da requisição deve ser um JSON"
        }), 400

    device = dados.get("device")

    if not device:
        return jsonify({
            "erro": "O campo atuador é obrigatório"
        }), 400

    try:
        with SessionLocal() as session:
            stmt = (
                select(
                    ArCadastrados.id.label("ar_cadastrado_id"),
                    Salas.id.label("sala_id")
                )
                .join(Salas, Salas.id == ArCadastrados.sala)
                .where(ArCadastrados.atuador == device.get("id"))
            )

            sala_condicionador = session.execute(stmt).mappings().first()

            if sala_condicionador is None:
                return jsonify({
                    "erro": "Ar-condicionado não encontrado para este atuador"
                }), 404

            sala_condicionador = dict(sala_condicionador)

        ar_cadastrado_id = sala_condicionador["ar_cadastrado_id"]
        sala_id = sala_condicionador["sala_id"]

        redis.atualizar_estado_dispositivo(
            ar_cadastrado_id,
            sala_id,
            dados
        )

        emitir_status_ar(
            ar_cadastrado_id=ar_cadastrado_id,
            sala_id=sala_id,
            dados=dados
        )

        return jsonify({
            "mensagem": "Status registrado",
            "resultado": sala_condicionador
        }), 201

    except Exception:
        app.logger.exception("Erro ao registrar status MQTT")
        return jsonify({
            "erro": "Não foi possível registrar o status"
        }), 500


@app.post("/internal/mqtt/availability")
def registrar_availability():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "erro": "Corpo da requisição deve ser um JSON"
        }), 400

    device_id = dados.get("atuador")

    try:
        with SessionLocal() as session:
            stmt = (
                select(
                    ArCadastrados.id.label("ar_cadastrado_id"),
                    Salas.id.label("sala_id")
                )
                .join(Salas, Salas.id == ArCadastrados.sala)
                .where(ArCadastrados.atuador == device_id)
            )

            sala_condicionador = session.execute(stmt).mappings().first()

            if sala_condicionador is None:
                return jsonify({
                    "erro": "Ar-condicionado não encontrado para este atuador"
                }), 404

            ar_id = sala_condicionador["ar_cadastrado_id"]
            sala_id = sala_condicionador["sala_id"]

        redis.atualizar_online_offline(
            ar_id,
            sala_id,
            device_id,
            dados.get("online")
        )

        return jsonify({
            "mensagem": "Status registrado"
        }), 200

    except Exception:
        app.logger.exception("Erro ao registrar availability MQTT")
        return jsonify({
            "erro": "Não foi possível registrar o status"
        }), 500


@app.route("/status-ar/<int:ar_cadastrado_id>", methods=["GET"])
def enviar_status_ar(ar_cadastrado_id):
    resposta = redis.consultar_estado_dispositivo(ar_cadastrado_id)

    return jsonify({
        "status": "ok",
        "resultado": resposta
    }), 201


@app.route("/status-all-ar", methods=["GET"])
def enviar_status_all_ar():
    dados = redis.get_data_all_ars()

    return jsonify({
        "status": "ok",
        "mensagem": "get ars",
        "data": dados
    })

@app.get("/teste-socket")
def teste_socket():
    ar_cadastrado_id =1
    sala_id = 10

    dados ={
        "device": {
            "id": "dispositivo-teste"
        },
        "state": {
            "power": True
        },
        "sensors": {
            "temperature": 23.5
        },
        "diagnostics": {
            "RSSI": -52
        },
        "statistics": {
            "tempo_ligado": 120
        },
        "atuador": "atuador-teste",
        "topico": "teste/socket"
    }

    # emitir_status_ar(
    #     ar_cadastrado_id=ar_cadastrado_id,
    #     sala_id=sala_id,
    #     dados=dados
    # )

    emitir_status_all_ar(
        ar_cadastrado_id=ar_cadastrado_id,
        sala_id=sala_id,
        socketIO_sala="dashboard",
        dados=dados
    )

    return jsonify({
        "status": "ok",
        "mensagem": "Evento emitido"
    })


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )

# Rotas temporárias:

from sqlalchemy import text
from database import engine


@app.route("/teste-sqlalchemy")
def teste_sqlalchemy():
    try:
        with engine.connect() as conn:
            resultado = conn.execute(text("SELECT 1")).scalar()

        return jsonify({
            "status": "ok",
            "sqlalchemy": resultado
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500