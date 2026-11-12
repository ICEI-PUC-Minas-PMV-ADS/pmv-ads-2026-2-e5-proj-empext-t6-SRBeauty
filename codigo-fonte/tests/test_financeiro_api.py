import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import inspect


database_url_before_import = os.environ.get("DATABASE_URL")
os.environ["DATABASE_URL"] = "sqlite://"
from app import ConfiguracaoTaxa, FechamentoCaixa, Movimentacao, User, app, db  # noqa: E402
from financeiro import (  # noqa: E402
    FormaPagamento,
    inicializar_taxas_padrao,
    migrar_banco_financeiro_legado,
)
if database_url_before_import is None:
    os.environ.pop("DATABASE_URL", None)
else:
    os.environ["DATABASE_URL"] = database_url_before_import


class FinanceiroApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()
            self.professional = User(
                nome="Profissional",
                email="prof-financeiro@example.test",
                senha_hash="x",
                tipo="profissional",
            )
            self.owner = User(
                nome="Proprietária",
                email="dona-financeiro@example.test",
                senha_hash="x",
                tipo="proprietario",
            )
            db.session.add_all([self.professional, self.owner])
            db.session.commit()
            self.professional_id = self.professional.id
            self.owner_id = self.owner.id
            inicializar_taxas_padrao(db, ConfiguracaoTaxa, FormaPagamento)

        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session["_user_id"] = str(self.owner_id)
            session["_fresh"] = True

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_fluxo_financeiro_relatorios_e_pdf(self):
        finance_page = self.client.get("/financeiro")
        reports_page = self.client.get("/relatorios")
        self.assertEqual(finance_page.status_code, 200)
        self.assertIn(b'const API_BASE = "/api"', finance_page.data)
        self.assertEqual(reports_page.status_code, 200)
        self.assertIn(b'const API_BASE = "/api"', reports_page.data)
        self.assertEqual(len(self.client.get("/api/financeiro/taxas").json), 4)
        with app.app_context():
            main_tables = inspect(db.engines[None]).get_table_names()
            self.assertIn("repasses_registros", main_tables)
            self.assertIn("categorias_repasse", main_tables)
            self.assertIn("movimentacoes", main_tables)
            self.assertIn("fechamentos_caixa", main_tables)
            self.assertIn("configuracao_taxas", main_tables)

        movement = self.client.post(
            "/api/financeiro/movimentacao",
            json={
                "tipo": "entrada",
                "profissional": "Ana",
                "descricao": "Manicure",
                "categoria": "Manicure",
                "forma_pagamento": "cartao_debito",
                "valor": 100,
            },
        )
        self.assertEqual(movement.status_code, 200)
        self.assertEqual(movement.json["taxa_cartao"], 1.99)
        self.assertEqual(movement.json["valor_liquido"], 98.01)

        expense = self.client.post(
            "/api/financeiro/movimentacao",
            json={
                "tipo": "saida",
                "descricao": "Conta de água",
                "categoria": "Despesa",
                "forma_pagamento": "pix",
                "valor": 20,
            },
        )
        self.assertEqual(expense.status_code, 200)
        self.assertEqual(expense.json["taxa_cartao"], 0)

        report = self.client.get("/api/relatorios/consolidado").json
        self.assertEqual(report["faturamento_mensal"], 100)
        self.assertEqual(report["total_despesas"], 20)
        self.assertEqual(report["saldo_liquido"], 78.01)
        self.assertEqual(report["total_atendimentos"], 1)

        closing = self.client.post("/api/financeiro/fechamento").json
        self.assertEqual(closing["saldo_liquido"], 78.01)
        pdf = self.client.get("/api/relatorios/exportar-pdf")
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf.mimetype, "application/pdf")
        self.assertTrue(pdf.data.startswith(b"%PDF"))

    def test_validacao_de_entradas_e_periodo(self):
        invalid_movement = self.client.post(
            "/api/financeiro/movimentacao",
            json={
                "tipo": "entrada",
                "descricao": "Valor inválido",
                "categoria": "Serviço",
                "forma_pagamento": "pix",
                "valor": -1,
            },
        )
        self.assertEqual(invalid_movement.status_code, 400)
        self.assertEqual(
            self.client.get("/api/relatorios/consolidado?mes=13&ano=2026").status_code,
            400,
        )
        self.assertEqual(
            self.client.put(
                "/api/financeiro/taxas",
                json={"taxas": [{"forma_pagamento": "desconhecido", "percentual": 1}]},
            ).status_code,
            400,
        )
        self.assertEqual(len(self.client.get("/api/financeiro/taxas").json), 4)

    def test_migra_banco_financeiro_preservando_ids_e_sem_reimportar(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho_origem = Path(diretorio) / "salao_financeiro.db"
            origem = sqlite3.connect(caminho_origem)
            origem.executescript(
                """
                CREATE TABLE movimentacoes (
                    id INTEGER PRIMARY KEY, tipo VARCHAR(7), profissional VARCHAR,
                    descricao VARCHAR, categoria VARCHAR, forma_pagamento VARCHAR(14),
                    valor_bruto FLOAT, taxa_cartao FLOAT, valor_liquido FLOAT, data DATETIME
                );
                CREATE TABLE fechamentos_caixa (
                    id INTEGER PRIMARY KEY, data_fechamento DATE UNIQUE,
                    total_entradas FLOAT, total_saidas FLOAT, total_taxas FLOAT,
                    saldo_liquido FLOAT, data_hora_registro DATETIME
                );
                CREATE TABLE configuracao_taxas (
                    forma_pagamento VARCHAR(14) PRIMARY KEY, percentual FLOAT
                );
                INSERT INTO movimentacoes VALUES (
                    47, 'ENTRADA', 'Ana', 'Manicure', 'Manicure', 'CARTAO_DEBITO',
                    100, 2.25, 97.75, '2026-10-10 10:00:00'
                );
                INSERT INTO fechamentos_caixa VALUES (
                    9, '2026-10-10', 100, 0, 2.25, 97.75, '2026-10-10 20:00:00'
                );
                INSERT INTO configuracao_taxas VALUES
                    ('PIX', 0), ('DINHEIRO', 0), ('CARTAO_DEBITO', 2.25), ('CARTAO_CREDITO', 3.99);
                """
            )
            origem.close()

            with app.app_context():
                primeira = migrar_banco_financeiro_legado(
                    db,
                    Movimentacao,
                    FechamentoCaixa,
                    ConfiguracaoTaxa,
                    caminho_origem,
                )
                self.assertEqual(primeira, {"movimentacoes": 1, "fechamentos": 1, "taxas": 1})
                movement = db.session.get(Movimentacao, 47)
                self.assertEqual(movement.valor_liquido, 97.75)
                segunda = migrar_banco_financeiro_legado(
                    db,
                    Movimentacao,
                    FechamentoCaixa,
                    ConfiguracaoTaxa,
                    caminho_origem,
                )
                self.assertEqual(segunda, {"movimentacoes": 0, "fechamentos": 0, "taxas": 0})

    def test_paginas_e_api_restritas_a_proprietaria(self):
        anonymous = app.test_client()
        self.assertEqual(anonymous.get("/financeiro").status_code, 302)
        with self.client.session_transaction() as session:
            session["_user_id"] = str(self.professional_id)
            session["_fresh"] = True

        self.assertEqual(self.client.get("/relatorios").status_code, 403)
        self.assertEqual(self.client.get("/api/financeiro/taxas").status_code, 403)


if __name__ == "__main__":
    unittest.main()
