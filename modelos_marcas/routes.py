from flask import Blueprint, jsonify, request, current_app
from .repository import get_db, executar_select, executar_insert, executar_insert_many, executar_update, executar_delete
import json
import redisAccess as redis
import mqtt_service_client
from mySocketio import emitir_status_ar, emitir_status_all_ar
from .service import listar_modelos_marcas

bp = Blueprint("modelos_marcas", __name__)

@bp.route("/modelos-marcas/<int:marcaModelo_id>", methods=["DELETE"])
def deletar_marcaModelo(marcaModelo_id):
    try:
        linhas_afetadas = executar_delete(
            """
            DELETE FROM modelos_marcas
            WHERE id = %s
            """,
            (marcaModelo_id,),
        )

        if linhas_afetadas == 0:
            return jsonify({
                "status": "erro",
                "mensagem": "comando não encontrado"
            }), 404

        return jsonify({
            "status": "ok",
            "mensagem": "comando deletado com sucesso"
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@bp.route("/modelos-marcas", methods=["POST"])
def inserir_modelo_marca():
    data = request.json

    marca = data.get("marca")
    modelo = data.get("modelo")

    if not marca or not modelo:
        return jsonify({"status": "erro", "mensagem": "marca e modelo são obrigatórios"}), 400

    sql = "INSERT INTO modelos_marcas (marca, modelo) VALUES (%s, %s)"
    print(sql)
    try:
        novo_id = executar_insert(sql, (marca, modelo))

        return jsonify({"status": "ok", "id": novo_id})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/modelos-marcas-comandos", methods=["POST"])
def associar_modelo_comando():
    data = request.json

    modelo_marcas = data.get("modelo_marcas")
    comandos = data.get("comandos")
    # comando_valor = data.get("comando_valor")
    print(comandos)
    if not modelo_marcas or not comandos:
        return jsonify({"status": "erro", "mensagem": "modelo_marcas e pelo menos 1 comando são obrigatórios"}), 400

    try:

        valores = [
            (
                modelo_marcas,
                comando["id"],
                str(comando["valor"])
                # "teste"
            )
            for comando in comandos
        ]

        sql = """
            INSERT INTO modelosMarcas_comando
            (modelo_marcas, comando, comando_valor)
            VALUES (%s, %s, %s)
        """
        # novo_id = executar_insert(sql)
        print("valores")
        print(valores)

        executar_insert_many(sql, valores)

        return jsonify({"status": "ok"})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/updateModelosComando", methods=["POST"])
def updateModelosComando():
    conn = get_db()
    cursor = conn.cursor()
    try:
        data = request.json
        marca = data["marcaValue"]
        modelo = data["modeloValue"]
        modelo_marcas_id = data["mmId"]
        comandos = data["comandos"]

        cursor.execute("START TRANSACTION")
        c_id = comandos[0]["id"]
        c_valor = "".join(str(comandos[0]["valor"]))

        cursor.execute(
            """
            UPDATE modelos_marcas
            SET marca = %s, modelo = %s
            WHERE id = %s
            """, 
            (marca, modelo, modelo_marcas_id))

        for comando in comandos:
            comando_id = comando["id"]
            comando_valor = comando["valor"]

            if comando_valor is None: #or comando_valor.strip() == ""
                cursor.execute("""
                    DELETE FROM modelosMarcas_comando
                    WHERE modelo_marcas = %s
                    AND comando = %s
                """, (modelo_marcas_id, comando_id))
            else:
                cursor.execute(
                    """
                    INSERT INTO modelosMarcas_comando
                        (modelo_marcas, comando, comando_valor)
                    VALUES
                        (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        comando_valor = VALUES(comando_valor)
                    """,
                    (modelo_marcas_id, comando_id, "".join(str(comando_valor)) ))

        conn.commit()

        print(data)
        return jsonify({"status": "ok"})

    except Exception as erro:
        conn.rollback()
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/modelos-marcas", methods=["GET"])
def api_listar_modelos_marcas():
    valor = listar_modelos_marcas()
    if(valor["status"]=="ok"):
        return jsonify(valor)
    return jsonify(valor), 500


@bp.route("/edite-modelos-marcas/<int:modelo_marca_id>", methods=["GET"])
def listar_modelos_marcas1(modelo_marca_id):
    resultado =""
    try:
        marcaModelo = executar_select(
            """
            SELECT id, marca, modelo
            FROM modelos_marcas
            WHERE id=%s
            ORDER BY marca, modelo
            """
            , (modelo_marca_id,),
        )       

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500
    
    try:
        comandos = executar_select(
            """
            SELECT
                c.id AS comando_id,
                c.nome AS comando_nome,
                CASE
                    WHEN mmc.id IS NULL THEN false
                    ELSE true
                END AS cadastrado_no_modelo
            FROM comandos c
            LEFT JOIN modelosMarcas_comando mmc
                ON mmc.comando = c.id
            AND mmc.modelo_marcas = %s
            ORDER BY c.nome;
            """
            , (modelo_marca_id,),
        )

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500
    
    resultado = {"marcaModelo": marcaModelo[0], "comandos": comandos, "status": "ok"}

    print(comandos)
    
    return jsonify(resultado)


@bp.route("/modelos-marcas/<int:modelo_marca_id>/comandos", methods=["GET"])
def listar_comandos_por_modelo_marca(modelo_marca_id):
    try:
        resultado = executar_select(
            """
            SELECT
                mmc.id AS associacao_id,
                mm.id AS modelo_marca_id,
                mm.marca,
                mm.modelo,
                c.id AS comando_id,
                c.nome AS comando_nome,
                mmc.comando_valor
            FROM modelosMarcas_comando mmc
            INNER JOIN modelos_marcas mm
                ON mm.id = mmc.modelo_marcas
            INNER JOIN comandos c
                ON c.id = mmc.comando
            WHERE mm.id = %s
            ORDER BY c.nome
            """,
            (modelo_marca_id,),
        )

        return jsonify({"status": "ok", "dados": resultado})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500
