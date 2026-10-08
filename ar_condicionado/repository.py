from sqlalchemy import select, update

from comandos.models import Comandos
from database import SessionLocal
from modelos_marcas.models import ModelosMarcas, ModelosMarcasComando
from salas.models import Salas

from .models import ArCadastrados


def inserir_ar_cadastrado(
    temperatura_referencia,
    modelo_marca,
    status,
    atuador,
    nome,
    sala,
):
    with SessionLocal.begin() as session:
        ar = ArCadastrados(
            temperatura_referencia=temperatura_referencia,
            modelo_marca=modelo_marca,
            status=status,
            atuador=atuador,
            nome=nome,
            sala=sala,
        )
        session.add(ar)
        session.flush()
        return ar.id


def atualizar_ar_cadastrado(
    ar_cadastrado_id,
    temperatura_medida,
    temperatura_referencia,
    modelo_marca,
    status,
    atuador,
    nome,
    sala,
):
    with SessionLocal.begin() as session:
        resultado = session.execute(
            update(ArCadastrados)
            .where(ArCadastrados.id == ar_cadastrado_id)
            .values(
                temperatura_medida=temperatura_medida,
                temperatura_referencia=temperatura_referencia,
                modelo_marca=modelo_marca,
                status=status,
                atuador=atuador,
                nome=nome,
                sala=sala,
            )
        )
        return resultado.rowcount


def buscar_comando_ar(ar_cadastrado_id, comando_nome):
    consulta = (
        select(
            ArCadastrados.id.label("ar_id"),
            ArCadastrados.nome.label("ar_nome"),
            ArCadastrados.atuador,
            ArCadastrados.modelo_marca,
            Comandos.id.label("comando_id"),
            Comandos.nome.label("comando_nome"),
            ModelosMarcasComando.comando_valor,
        )
        .join(
            ModelosMarcasComando,
            ModelosMarcasComando.modelo_marcas == ArCadastrados.modelo_marca,
        )
        .join(Comandos, Comandos.id == ModelosMarcasComando.comando)
        .where(
            ArCadastrados.id == ar_cadastrado_id,
            Comandos.nome == comando_nome,
        )
    )
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(consulta).mappings().all()]


def buscar_ar_para_edicao(ar_cadastrado_id):
    consulta = (
        select(
            ArCadastrados.id,
            ArCadastrados.nome.label("nome_ar"),
            ArCadastrados.temperatura_referencia,
            Salas.nome.label("sala_nome"),
            Salas.id.label("sala_id"),
            ModelosMarcas.id.label("mm_id"),
            ModelosMarcas.marca,
            ModelosMarcas.modelo,
            ArCadastrados.atuador,
        )
        .outerjoin(Salas, ArCadastrados.sala == Salas.id)
        .outerjoin(
            ModelosMarcas,
            ArCadastrados.modelo_marca == ModelosMarcas.id,
        )
        .where(ArCadastrados.id == ar_cadastrado_id)
    )
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(consulta).mappings().all()]


def listar_ar_cadastrados():
    consulta = (
        select(
            ArCadastrados.id,
            ArCadastrados.nome.label("nome_ar"),
            ArCadastrados.temperatura_referencia,
            Salas.nome.label("sala_nome"),
            Salas.codigo.label("sala_cod"),
            ModelosMarcas.marca,
            ModelosMarcas.modelo,
            ArCadastrados.atuador,
        )
        .outerjoin(Salas, ArCadastrados.sala == Salas.id)
        .outerjoin(
            ModelosMarcas,
            ArCadastrados.modelo_marca == ModelosMarcas.id,
        )
        .order_by(Salas.nome, ArCadastrados.nome)
    )
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(consulta).mappings().all()]
