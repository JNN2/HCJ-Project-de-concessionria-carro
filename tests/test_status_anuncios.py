import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import app


class StatusAnunciosTest(unittest.TestCase):
    def setUp(self):
        self.diretorio = tempfile.TemporaryDirectory()
        self.addCleanup(self.diretorio.cleanup)
        self.caminho = Path(self.diretorio.name) / "veiculos.csv"
        self.colunas = ["id", "status", "usuario_id", "outro"]
        self.registros = [
            {"id": "1", "status": "ativo", "usuario_id": "10", "outro": "preservar"},
            {"id": "2", "status": "pausado", "usuario_id": "20", "outro": "também"},
        ]
        self.gravar()
        caminho_csv = patch("services.anuncios.CAMINHO_CSV", self.caminho)
        caminho_csv.start()
        self.addCleanup(caminho_csv.stop)
        app.config.update(TESTING=True)
        self.cliente = app.test_client()

    def gravar(self):
        with self.caminho.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=self.colunas)
            escritor.writeheader()
            escritor.writerows(self.registros)

    def ler(self):
        with self.caminho.open(encoding="utf-8", newline="") as arquivo:
            return list(csv.DictReader(arquivo))

    def autenticar(self, usuario_id=10):
        with self.cliente.session_transaction() as sessao:
            sessao["usuario_id"] = usuario_id

    def alterar(self, anuncio_id=1, status="pausado"):
        return self.cliente.patch(f"/api/anuncios/{anuncio_id}/status", json={"status": status})

    def test_pausar_e_reativar_preserva_demais_dados(self):
        self.autenticar()
        resposta = self.alterar()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["status"], "pausado")
        registros = self.ler()
        self.assertEqual(registros[0], {**self.registros[0], "status": "pausado"})
        self.assertEqual(registros[1], self.registros[1])
        self.assertEqual(self.alterar(status="ativo").json["status"], "ativo")
        self.assertEqual(self.ler(), self.registros)

    def test_rejeita_requisicoes_sem_permissao_ou_invalidas(self):
        self.assertEqual(self.alterar().status_code, 401)
        self.autenticar()
        self.assertEqual(self.alterar(anuncio_id=2).status_code, 403)
        self.assertEqual(self.alterar(anuncio_id=999).status_code, 404)
        self.assertEqual(self.alterar(status="excluido").status_code, 400)
        self.assertEqual(self.cliente.patch("/api/anuncios/1/status", json=[]).status_code, 400)
        self.assertEqual(self.ler(), self.registros)

    def test_anuncio_antigo_sem_proprietario_nao_pode_ser_alterado(self):
        self.colunas = ["id", "status", "outro"]
        self.registros = [{"id": "1", "status": "ativo", "outro": "antigo"}]
        self.gravar()
        self.autenticar()
        self.assertEqual(self.alterar().status_code, 403)
        self.assertEqual(self.ler(), self.registros)

    def test_erro_de_gravacao_nao_altera_arquivo(self):
        self.autenticar()
        with patch("services.anuncios.os.replace", side_effect=OSError("falha")):
            self.assertEqual(self.alterar().status_code, 500)
        self.assertEqual(self.ler(), self.registros)
        self.assertEqual(list(self.caminho.parent.glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
