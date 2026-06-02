import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import MySQLdb
from MySQLdb.cursors import DictCursor
import logging

app = Flask(__name__)
CORS(app)
load_dotenv()

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

# Sample in-memory data
incomes = [
    {'description': 'salario fak', 'amount': 60000},
    {'description': 'freelanceee', 'amount': 2000}
]

# GET endpoint to retrieve all incomes
@app.route('/incomes', methods=['GET'])
def get_incomes():
    return jsonify(incomes)

# POST endpoint to add a new income
@app.route('/incomes', methods=['POST'])
def add_income():
    # Get JSON data from the request body
    new_income = request.get_json()
    incomes.append(new_income)
    # Return an empty response with a 204 status code (No Content)
    return '', 204

def get_db():
    return MySQLdb.connect(
        # host="127.0.0.1",
        host="mysql_super_ar",
        user= os.getenv("MYSQL_USER"),
        passwd= os.getenv("MYSQL_PASSWORD"),
        db= os.getenv("MYSQL_DATABASE"),
        port=int( 3306),
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

@app.route("/comandos/<int:comando_id>", methods=["DELETE"])
def deletar_comando(comando_id):
    try:
        linhas_afetadas = executar_delete(
            """
            DELETE FROM comandos
            WHERE id = %s
            """,
            (comando_id,),
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

@app.route("/modelos-marcas/<int:marcaModelo_id>", methods=["DELETE"])
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

@app.route("/comandos", methods=["POST"])
def inserir_comando():
    data = request.json

    # return jsonify({"status": "ok", "id": 1})
    nome = data.get("nome")

    if not nome:
        return jsonify({"status": "erro", "mensagem": "nome é obrigatório"}), 400

    sql = "insert into comandos (nome) values ('"+nome+"');"
    # return jsonify({"status": "ok", "id": 1})
    try:
        novo_id = executar_insert(sql)
        return jsonify({"status": "ok", "id": novo_id})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500

@app.route("/modelos-marcas", methods=["POST"])
def inserir_modelo_marca():
    data = request.json

    marca = data.get("marca")
    modelo = data.get("modelo")

    if not marca or not modelo:
        return jsonify({"status": "erro", "mensagem": "marca e modelo são obrigatórios"}), 400

    sql = "INSERT INTO modelos_marcas (marca, modelo) VALUES ('" + marca + "','" + modelo + "')"
    print(sql)
    try:
        novo_id = executar_insert(sql)

        return jsonify({"status": "ok", "id": novo_id})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500

@app.route("/modelos-marcas-comandos", methods=["POST"])
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

@app.route("/ar-cadastrados", methods=["POST"])
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

@app.route("/salas", methods=["POST"])
def inserir_sala():
    data = request.json

    nome = data.get("nome")
    predio = data.get("predio")
    numero_de_ar = data.get("numero_de_ar", 0)
    ar1 = data.get("ar1")
    ar2 = data.get("ar2")
    ar3 = data.get("ar3")
    ar4 = data.get("ar4")

    if not nome:
        return jsonify({"status": "erro", "mensagem": "nome é obrigatório"}), 400

    try:
        novo_id = executar_insert(
            """
            INSERT INTO salas
            (nome, predio, numero_de_ar, ar1, ar2, ar3, ar4)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nome, predio, numero_de_ar, ar1, ar2, ar3, ar4),
        )

        return jsonify({"status": "ok", "id": novo_id})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500

@app.route("/salas", methods=["GET"])
def api_lista_salas():
    salas = lista_salas()
    if(salas["status"]=="ok"):
        return jsonify(salas)
    return jsonify(salas), 500

def lista_salas():
    try:
        resultado = executar_select(
            """
            SELECT id, nome, codigo, predio
            FROM salas
            ORDER BY codigo, nome
            """
        )

        return {"status": "ok", "dados": resultado}

    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}

@app.route("/getAddFomrArData", methods=["GET"])
def getDataToAddFormAr():
    salas = lista_salas()
    marca_modelo = listar_modelos_marcas()

    if(salas["status"] != "ok"):
        return jsonify(salas), 500;
    if(marca_modelo["status"] != "ok"):
        return jsonify(marca_modelo), 500;

    return jsonify({"status": "ok", "salas": salas["dados"], "marcaModelo": marca_modelo["dados"]})

@app.route("/getEditFomrArData/<int:Ar_id>", methods=["GET"])
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
                mm.modelo
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

@app.route("/updateModelosComando", methods=["POST"])
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

@app.route("/modelos-marcas", methods=["GET"])
def api_listar_modelos_marcas():
    valor = listar_modelos_marcas()
    if(valor["status"]=="ok"):
        return jsonify(valor)
    return jsonify(valor), 500

def listar_modelos_marcas():
    try:
        resultado = executar_select(
            """
            SELECT id, marca, modelo
            FROM modelos_marcas
            ORDER BY marca, modelo
            """
        )

        return {"status": "ok", "dados": resultado}

    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}

@app.route("/edite-modelos-marcas/<int:modelo_marca_id>", methods=["GET"])
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

@app.route("/modelos-marcas/<int:modelo_marca_id>/comandos", methods=["GET"])
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

@app.route("/comandos", methods=["GET"])
def listar_comandos():
    try:
        resultado = executar_select(
            """
            SELECT id, nome
            FROM comandos
            ORDER BY nome
            """
        )

        return jsonify({"status": "ok", "dados": resultado})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500

@app.route("/ar-cadastrados", methods=["GET"])
def listar_ar_cadastrados():
    try:
        resultado = executar_select(
            """
            SELECT
                ar.id,
                ar.nome AS nome_ar,
                ar.temperatura_referencia,
                s.nome AS sala_nome,
                mm.marca,
                mm.modelo
            FROM ar_cadastrados ar
            LEFT JOIN salas s
                ON ar.sala = s.id
            LEFT JOIN modelos_marcas mm
                ON ar.modelo_marca = mm.id
            ORDER BY s.nome, ar.nome
            """
        )

        return jsonify({
            "status": "ok",
            "dados": resultado
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)