import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from mySocketio import init_socketio, socketio

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    init_socketio(app)
    from comandos.routes import bp as comandos_bp
    from modelos_marcas.routes import bp as modelos_marcas_bp
    from ar_condicionado.routes import bp as ar_condicionado_bp
    from salas.routes import bp as salas_bp
    from monitoramento.routes import bp as monitoramento_bp
    for blueprint in (comandos_bp, modelos_marcas_bp, ar_condicionado_bp, salas_bp, monitoramento_bp):
        app.register_blueprint(blueprint)
    return app

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000,
                 debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")