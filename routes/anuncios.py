import csv

from flask import current_app, jsonify, request, session

from services.anuncios import atualizar_status_anuncio


def alterar_status(anuncio_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify(sucesso=False, mensagem="Faça login para alterar o anúncio."), 401

    dados = request.get_json(silent=True)
    status = dados.get("status") if isinstance(dados, dict) else None
    if status not in ("ativo", "pausado"):
        return jsonify(sucesso=False, mensagem="Informe um status válido."), 400

    try:
        resultado = atualizar_status_anuncio(anuncio_id, usuario_id, status)
    except (OSError, ValueError, csv.Error):
        current_app.logger.exception("Falha ao atualizar status do anúncio")
        return jsonify(sucesso=False, mensagem="Não foi possível atualizar o anúncio."), 500

    if resultado == "nao_encontrado":
        return jsonify(sucesso=False, mensagem="Anúncio não encontrado."), 404
    if resultado == "proibido":
        return jsonify(sucesso=False, mensagem="Você não pode alterar este anúncio."), 403
    return jsonify(sucesso=True, status=status), 200


def registrar_rotas_anuncios(app):
    app.add_url_rule(
        "/api/anuncios/<int:anuncio_id>/status",
        view_func=alterar_status,
        methods=["PATCH"],
    )
