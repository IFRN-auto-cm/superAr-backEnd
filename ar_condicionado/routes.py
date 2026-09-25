from flask import Blueprint, jsonify, request, current_app
from .repository import get_db, executar_select, executar_insert, executar_insert_many, executar_update, executar_delete
import json
import redisAccess as redis
import mqtt_service_client
from mySocketio import emitir_status_ar, emitir_status_all_ar
from salas.service import lista_salas
from modelos_marcas.service import listar_modelos_marcas
from .service import publicar_mqtt

bp = Blueprint("ar_condicionado", __name__)

@bp.route("/ar-cadastrados", methods=["POST"])
def inserir_ar_cadastrado():
    data = request.json

    # temperatura_medida = data.get("temperatura_medida")
    temperatura_referencia = data.get("temperatura_referencia")
    modelo_marca = data.get("marcaModeloId")
    status = data.get("status")
    atuador = data.get("atuador")
    nome = data.get("nome")
    sala = data.get("sala")

    if not modelo_marca:
        return jsonify({"status": "erro", "mensagem": "modelo_marca é obrigatório"}), 400

    try:
        novo_id = executar_insert(
            """
            INSERT INTO ar_cadastrados
            (temperatura_referencia, modelo_marca, status, atuador, nome, sala)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                temperatura_referencia,
                modelo_marca,
                status,
                atuador,
                nome,
                sala,
            ),
        )

        return jsonify({"status": "ok", "id": novo_id})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/ar-cadastrados/<int:ar_cadastrado_id>", methods=["POST"])
def update_ar_cadastrado(ar_cadastrado_id):
    data = request.json

    temperatura_medida = 0#data.get("temperatura_medida")
    temperatura_referencia = data.get("temperatura_referencia")
    modelo_marca = data.get("marcaModeloId")
    status = data.get("status")
    atuador = data.get("atuador")
    nome = data.get("nome")
    sala = data.get("sala")

    print(ar_cadastrado_id);
    print(data);

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
        linhas_afetadas = executar_update(
            """
            UPDATE ar_cadastrados
            SET
                temperatura_medida = %s,
                temperatura_referencia = %s,
                modelo_marca = %s,
                status = %s,
                atuador = %s,
                nome = %s,
                sala = %s
            WHERE id = %s
            """,
            (
                temperatura_medida,
                temperatura_referencia,
                modelo_marca,
                status,
                atuador,
                nome,
                sala,
                ar_cadastrado_id,
            ),
        )

        return jsonify({
            "status": "ok",
            "linhas_afetadas": linhas_afetadas
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@bp.route("/ar-cadastrados/<int:ar_cadastrado_id>/enviar-comando", methods=["POST"])
def enviar_comando_ar(ar_cadastrado_id):
    
    data = request.json   
    comando_nome = data.get("comando_nome")

    if not comando_nome:
        return jsonify({
            "status": "erro",
            "mensagem": "comando_nome é obrigatório"
        }), 400

    try:
        # resultado = []
        resultado = executar_select(
            """
            SELECT
                ar.id AS ar_id,
                ar.nome AS ar_nome,
                ar.atuador,
                ar.modelo_marca,
                c.id AS comando_id,
                c.nome AS comando_nome,
                mmc.comando_valor
            FROM ar_cadastrados ar
            INNER JOIN modelosMarcas_comando mmc
                ON mmc.modelo_marcas = ar.modelo_marca
            INNER JOIN comandos c
                ON c.id = mmc.comando
            WHERE ar.id = %s
              AND c.nome = %s
            """,
            (ar_cadastrado_id, comando_nome)
        )

        if len(resultado) == 0:
            return jsonify({
                "status": "erro",
                "mensagem": "Comando não cadastrado para o modelo deste ar-condicionado"
            }), 404

        dados = resultado[0]

        if not dados["atuador"]:
            return jsonify({
                "status": "erro",
                "mensagem": "Este ar-condicionado não possui atuador cadastrado"
            }), 400

        vetor = json.loads(dados["comando_valor"])
        # print(len(vetor))   

        print(comando_nome.casefold())
        referencia=0
        if(comando_nome.casefold() == "desligar"):
            cmdType = "desligar"
        elif (comando_nome.casefold().split()[0]=="ligar"):
            cmdType = "ligar"
            referencia = comando_nome.split()[1]

        payload = {
            # "ar_id": dados["ar_id"],
            # "comando_id": dados["comando_id"],
            # "comando_nome": dados["comando_nome"],
            "irCmd": vetor,#dados["comando_valor"],
            "length": len(vetor),
            "cmdType": cmdType,
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


@bp.route("/getAddFomrArData", methods=["GET"])
def getDataToAddFormAr():
    salas = lista_salas()
    marca_modelo = listar_modelos_marcas()

    if(salas["status"] != "ok"):
        return jsonify(salas), 500;
    if(marca_modelo["status"] != "ok"):
        return jsonify(marca_modelo), 500;

    return jsonify({"status": "ok", "salas": salas["dados"], "marcaModelo": marca_modelo["dados"]})


@bp.route("/getEditFomrArData/<int:Ar_id>", methods=["GET"])
def getDataToEditFormAr(Ar_id):
    salas = lista_salas()
    marca_modelo = listar_modelos_marcas()

    if(salas["status"] != "ok"):
        return jsonify(salas), 500;
    if(marca_modelo["status"] != "ok"):
        return jsonify(marca_modelo), 500;

    print(Ar_id)

    try:
        resultado = executar_select(
            """
            SELECT
                ar.id,
                ar.nome AS nome_ar,
                ar.temperatura_referencia,
                s.nome AS sala_nome,
                s.id as sala_id,
                mm.id as mm_id,
                mm.marca,
                mm.modelo,
                ar.atuador
            FROM ar_cadastrados ar
            LEFT JOIN salas s
                ON ar.sala = s.id
            LEFT JOIN modelos_marcas mm
                ON ar.modelo_marca = mm.id
            WHERE ar.id = %s
            """,
            str(Ar_id)
        )

        resultado = { "editAr": resultado, "salas": salas["dados"], "marcasModelos": marca_modelo["dados"]}

        return jsonify({
            "status": "ok",
            "dados": resultado
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@bp.route("/ar-cadastrados", methods=["GET"])
def listar_ar_cadastrados():
    try:
        resultado = executar_select(
            """
            SELECT
                ar.id,
                ar.nome AS nome_ar,
                ar.temperatura_referencia,
                s.nome AS sala_nome,
                s.codigo as sala_cod,
                mm.marca,
                mm.modelo,
                ar.atuador
            FROM ar_cadastrados ar
            LEFT JOIN salas s
                ON ar.sala = s.id
            LEFT JOIN modelos_marcas mm
                ON ar.modelo_marca = mm.id
            ORDER BY s.nome, ar.nome
            """
        )

        for ar in resultado:
            arStatus = redis.consultar_estado_dispositivo(ar["id"])
            if(arStatus != None):

                ar["temperatura_medida"] = arStatus["temperatura_medida"]
                ar["status"] = "ligado" if arStatus["power"] else "desligado"

            else:
                ar["status"]                = "desconhecido"
                ar["temperatura_medida"]    = "desconhecido"


        return jsonify({
            "status": "ok",
            "dados": resultado
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@bp.route("/enviar-comando/<int:ar_cadastrado_id>", methods=["GET"])
def acionar_comando(ar_cadastrado_id):
    return jsonify({"status":"erro", "mensagem":"Endpoint incompleto no código original; utilize POST /ar-cadastrados/<id>/enviar-comando"}), 501
