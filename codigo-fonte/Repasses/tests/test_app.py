import os
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

os.environ["DATABASE_URL"] = "sqlite://"

from app import (  # noqa: E402
    Appointment,
    AppointmentService,
    CategoriaRepasse,
    Service,
    User,
    app,
    db,
)


class RepassesIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()
            self.owner = User(
                nome="Proprietária",
                email="dona@example.test",
                senha_hash="x",
                tipo="proprietario",
            )
            self.client_user = User(
                nome="Cliente",
                email="cliente@example.test",
                senha_hash="x",
                tipo="cliente",
            )
            self.manicure = User(
                nome="Ana Manicure",
                email="ana@example.test",
                senha_hash="x",
                tipo="profissional",
            )
            self.hairdresser = User(
                nome="Bia Cabeleireira",
                email="bia@example.test",
                senha_hash="x",
                tipo="profissional",
            )
            db.session.add_all([self.owner, self.client_user, self.manicure, self.hairdresser])
            db.session.flush()
            manicure_service = Service(
                nome="Manicure",
                descricao="",
                preco=Decimal("100.00"),
                duracao_minutos=40,
            )
            hair_service = Service(
                nome="Corte",
                descricao="",
                preco=Decimal("200.00"),
                duracao_minutos=60,
            )
            db.session.add_all([manicure_service, hair_service])
            db.session.flush()
            db.session.add_all([
                CategoriaRepasse(profissional_id=self.manicure.id, categoria="manicure"),
                CategoriaRepasse(profissional_id=self.hairdresser.id, categoria="cabeleireira"),
            ])
            self.add_completed_service(self.manicure, manicure_service, "100.00")
            self.add_completed_service(self.hairdresser, hair_service, "200.00")
            db.session.commit()
            self.owner_id = self.owner.id
            self.manicure_id = self.manicure.id
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session["_user_id"] = str(self.owner_id)
            session["_fresh"] = True

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def add_completed_service(self, professional, service, value):
        completed_at = datetime(2026, 10, 14, 15, tzinfo=timezone.utc)
        appointment = Appointment(
            cliente_id=self.client_user.id,
            profissional_id=professional.id,
            agendado_para=completed_at - timedelta(hours=1),
            iniciado_em=completed_at - timedelta(minutes=45),
            concluido_em=completed_at,
            duracao_real_minutos=45,
            status="concluido",
        )
        db.session.add(appointment)
        db.session.flush()
        db.session.add(AppointmentService(
            atendimento_id=appointment.id,
            servico_id=service.id,
            profissional_id=professional.id,
            nome_servico=service.nome,
            valor_cobrado=Decimal(value),
            duracao_prevista_minutos=service.duracao_minutos,
        ))

    def test_lista_repasses_calculados_de_atendimentos_concluidos(self):
        before = self.client.get("/api/repasses?semana_inicio=2026-10-12")
        self.assertEqual(before.status_code, 200)
        self.assertEqual(before.json["itens"], [])

        generated = self.client.post(
            "/api/repasses/gerar",
            json={"semana_inicio": "2026-10-12"},
        )
        self.assertEqual(generated.status_code, 200)
        self.assertEqual(generated.json["criados"], 2)
        generated_again = self.client.post(
            "/api/repasses/gerar",
            json={"semana_inicio": "2026-10-12"},
        )
        self.assertEqual(generated_again.status_code, 200)
        self.assertEqual(generated_again.json["criados"], 0)

        response = self.client.get("/api/repasses?semana_inicio=2026-10-12")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total_pendente"], 80.0)
        self.assertEqual(
            [item["valor_repasse"] for item in response.json["itens"]],
            [20.0, 60.0],
        )
        self.assertEqual(
            [item["status"] for item in response.json["itens"]],
            ["pendente", "pendente"],
        )

    def test_confirma_pagamentos_em_lote_e_impede_repeticao(self):
        self.client.post("/api/repasses/gerar", json={"semana_inicio": "2026-10-12"})
        pendentes = self.client.get("/api/repasses?semana_inicio=2026-10-12").json["itens"]
        ids = [item["id"] for item in pendentes]
        payload = {"semana_inicio": "2026-10-12", "repasses": ids}

        confirmed = self.client.post("/api/repasses/pagamentos-lote", json=payload)

        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(confirmed.json["total_pago"], 80.0)
        self.assertEqual(
            [item["status"] for item in confirmed.json["itens"]],
            ["pago", "pago"],
        )
        repeated = self.client.post("/api/repasses/pagamentos-lote", json=payload)
        self.assertEqual(repeated.status_code, 409)

    def test_exporta_relatorio_csv_da_semana(self):
        self.client.post("/api/repasses/gerar", json={"semana_inicio": "2026-10-12"})
        itens = self.client.get("/api/repasses?semana_inicio=2026-10-12").json["itens"]
        manicure = next(item for item in itens if item["profissional"] == "Ana Manicure")
        paid = self.client.post(
            "/api/repasses/pagamentos-lote",
            json={"semana_inicio": "2026-10-12", "repasses": [manicure["id"]]},
        )
        self.assertEqual(paid.status_code, 200)

        response = self.client.get("/api/repasses/relatorio.csv?semana_inicio=2026-10-12")
        content = response.get_data(as_text=True).lstrip("\ufeff")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.mimetype.startswith("text/csv"))
        self.assertIn('attachment; filename="relatorio_repasses_2026-10-12_2026-10-18.csv"', response.headers["Content-Disposition"])
        self.assertIn("Ana Manicure", content)
        self.assertIn("Bia Cabeleireira", content)
        self.assertIn(";Pago;", content)
        self.assertIn(";Pendente;", content)
        self.assertIn("Total pago;20,00", content)
        self.assertIn("Total pendente;60,00", content)

    def test_lote_invalido_nao_confirma_parcialmente(self):
        self.client.post("/api/repasses/gerar", json={"semana_inicio": "2026-10-12"})
        pending = self.client.get("/api/repasses?semana_inicio=2026-10-12").json["itens"][0]

        response = self.client.post(
            "/api/repasses/pagamentos-lote",
            json={
                "semana_inicio": "2026-10-12",
                "repasses": [pending["id"], 9999],
            },
        )

        self.assertEqual(response.status_code, 409)
        after = self.client.get("/api/repasses?semana_inicio=2026-10-12").json
        self.assertEqual(after["total_pendente"], 80.0)

    def test_crud_cria_edita_e_cancela_repasse(self):
        created = self.client.post(
            "/api/repasses",
            json={"semana_inicio": "2026-10-12", "profissional_id": self.manicure_id},
        )
        self.assertEqual(created.status_code, 201)
        repasse_id = created.json["id"]
        self.assertEqual(created.json["status"], "pendente")

        duplicate = self.client.post(
            "/api/repasses",
            json={"semana_inicio": "2026-10-12", "profissional_id": self.manicure_id},
        )
        self.assertEqual(duplicate.status_code, 409)

        updated = self.client.put(
            f"/api/repasses/{repasse_id}",
            json={
                "quantidade_servicos": 2,
                "base_calculo": "120.00",
                "valor_repasse": "24.00",
                "status": "pago",
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json["quantidade_servicos"], 2)
        self.assertEqual(updated.json["valor_repasse"], 24.0)
        self.assertEqual(updated.json["status"], "pago")
        self.assertIsNotNone(updated.json["pago_em"])

        deleted = self.client.delete(f"/api/repasses/{repasse_id}")
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(deleted.json["status"], "cancelado")
        self.assertIsNotNone(deleted.json["cancelado_em"])
        report = self.client.get("/api/repasses?semana_inicio=2026-10-12").json
        self.assertEqual(report["total_pendente"], 0.0)
        self.assertEqual(report["total_pago"], 0.0)
        self.assertEqual(report["itens"][0]["status"], "cancelado")

    def test_exclui_repasse_definitivamente(self):
        created = self.client.post(
            "/api/repasses",
            json={"semana_inicio": "2026-10-12", "profissional_id": self.manicure_id},
        )
        self.assertEqual(created.status_code, 201)
        repasse_id = created.json["id"]

        deleted = self.client.delete(f"/api/repasses/{repasse_id}/definitivo")

        self.assertEqual(deleted.status_code, 204)
        report = self.client.get("/api/repasses?semana_inicio=2026-10-12").json
        self.assertNotIn(repasse_id, [item["id"] for item in report["itens"]])
        repeated = self.client.delete(f"/api/repasses/{repasse_id}/definitivo")
        self.assertEqual(repeated.status_code, 404)

    def test_categoria_de_profissional_e_autorizacao(self):
        response = self.client.get("/api/repasses/profissionais")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["categoria"] for item in response.json], ["manicure", "cabeleireira"])

        page = self.client.get("/repasses")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Pendentes e pagos", page.data)
        home = self.client.get("/home")
        self.assertIn(b'href="/repasses"', home.data)

        updated = self.client.put(
            f"/api/repasses/profissionais/{self.manicure_id}/categoria",
            json={"categoria": "cabeleireira"},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json["percentual"], 30)

        anonymous = app.test_client().get("/repasses")
        self.assertEqual(anonymous.status_code, 302)
        anonymous_report = app.test_client().get("/api/repasses/relatorio.csv?semana_inicio=2026-10-12")
        self.assertEqual(anonymous_report.status_code, 302)

        self.assertEqual(
            self.client.put(
                f"/api/repasses/profissionais/{self.manicure_id}/categoria",
                json={"categoria": "invalida"},
            ).status_code,
            400,
        )

    def test_semana_precisa_comecar_na_segunda(self):
        response = self.client.get("/api/repasses?semana_inicio=2026-10-13")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
