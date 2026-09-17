import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from mySocketio import init_socketio, socketio

from comandos.routes import comandos_bp
from modelos_marcas.routes import modelos_marcas_bp
from ar_condicionado.routes import ar_condicionado_bp
from salas.routes import salas_bp
from monitoramento.routes import monitoramento_bp


# Carrega variáveis de ambiente
load_dotenv()


def create_app():

    app = Flask(__name__)

    # Configuração do CORS
    CORS(app)

    # Inicialização do Socket.IO
    init_socketio(app)

    # Registro dos módulos
    app.register_blueprint(comandos_bp)
    app.register_blueprint(modelos_marcas_bp)
    app.register_blueprint(ar_condicionado_bp)
    app.register_blueprint(salas_bp)
    app.register_blueprint(monitoramento_bp)

    return app


# Mantém compatibilidade com importações de api:app
app = create_app()


if __name__ == "__main__":

    debug = os.getenv(
        "FLASK_DEBUG", "false"
    ).lower() == "true"

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=debug
    )