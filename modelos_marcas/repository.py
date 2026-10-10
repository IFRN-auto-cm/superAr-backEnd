from sqlalchemy import case, delete, select, update
from sqlalchemy.dialects.mysql import insert as mysql_insert

from comandos.models import Comandos
from database import SessionLocal
from .models import ModelosMarcas, ModelosMarcasComando


def deletar_modelo_marca(modelo_marca_id):
    with SessionLocal.begin() as session:
        resultado = session.execute(
            delete(ModelosMarcas).where(ModelosMarcas.id == modelo_marca_id)
        )
        return resultado.rowcount


def inserir_modelo_marca(marca, modelo):
    with SessionLocal.begin() as session:
        novo_modelo_marca = ModelosMarcas(marca=marca, modelo=modelo)
        session.add(novo_modelo_marca)
        session.flush()
        return novo_modelo_marca.id


def associar_modelo_comandos(associacoes):
    with SessionLocal.begin() as session:
        session.add_all(
            [
                ModelosMarcasComando(
                    modelo_marcas=modelo_marcas,
                    comando=comando,
                    comando_valor=comando_valor,
                )
                for modelo_marcas, comando, comando_valor in associacoes
            ]
        )


def atualizar_modelo_marca_comandos(
    marca,
    modelo,
    modelo_marcas_id,
    comandos_para_remover,
    comandos_para_salvar,
):
    with SessionLocal.begin() as session:
        session.execute(
            update(ModelosMarcas)
            .where(ModelosMarcas.id == modelo_marcas_id)
            .values(marca=marca, modelo=modelo)
        )

        for comando_id in comandos_para_remover:
            session.execute(
                delete(ModelosMarcasComando).where(
                    ModelosMarcasComando.modelo_marcas == modelo_marcas_id,
                    ModelosMarcasComando.comando == comando_id,
                )
            )

        for modelo_id, comando_id, comando_valor in comandos_para_salvar:
            stmt = mysql_insert(ModelosMarcasComando).values(
                modelo_marcas=modelo_id,
                comando=comando_id,
                comando_valor=comando_valor,
            )
            session.execute(
                stmt.on_duplicate_key_update(comando_valor=comando_valor)
            )


def listar_modelos_marcas():
    consulta = select(
        ModelosMarcas.id,
        ModelosMarcas.marca,
        ModelosMarcas.modelo,
    ).order_by(ModelosMarcas.marca, ModelosMarcas.modelo)
    with SessionLocal() as session:
        return [
            dict(row) for row in session.execute(consulta).mappings().all()
        ]


def buscar_dados_edicao_modelo_marca(modelo_marca_id):
    marca_modelo_stmt = (
        select(
            ModelosMarcas.id,
            ModelosMarcas.marca,
            ModelosMarcas.modelo,
        )
        .where(ModelosMarcas.id == modelo_marca_id)
        .order_by(ModelosMarcas.marca, ModelosMarcas.modelo)
    )
    cadastrado_no_modelo = case(
        (ModelosMarcasComando.id.is_(None), False),
        else_=True,
    ).label("cadastrado_no_modelo")
    comandos_stmt = (
        select(
            Comandos.id.label("comando_id"),
            Comandos.nome.label("comando_nome"),
            cadastrado_no_modelo,
        )
        .outerjoin(
            ModelosMarcasComando,
            (ModelosMarcasComando.comando == Comandos.id)
            & (ModelosMarcasComando.modelo_marcas == modelo_marca_id),
        )
        .order_by(Comandos.nome)
    )

    with SessionLocal() as session:
        marca_modelo = [
            dict(row)
            for row in session.execute(marca_modelo_stmt).mappings().all()
        ]
        comandos = [
            dict(row)
            for row in session.execute(comandos_stmt).mappings().all()
        ]
    return marca_modelo, comandos


def listar_comandos_por_modelo_marca(modelo_marca_id):
    consulta = (
        select(
            ModelosMarcasComando.id.label("associacao_id"),
            ModelosMarcas.id.label("modelo_marca_id"),
            ModelosMarcas.marca,
            ModelosMarcas.modelo,
            Comandos.id.label("comando_id"),
            Comandos.nome.label("comando_nome"),
            ModelosMarcasComando.comando_valor,
        )
        .join(
            ModelosMarcas,
            ModelosMarcas.id == ModelosMarcasComando.modelo_marcas,
        )
        .join(
            Comandos,
            Comandos.id == ModelosMarcasComando.comando,
        )
        .where(ModelosMarcas.id == modelo_marca_id)
        .order_by(Comandos.nome)
    )
    with SessionLocal() as session:
        return [
            dict(row) for row in session.execute(consulta).mappings().all()
        ]
