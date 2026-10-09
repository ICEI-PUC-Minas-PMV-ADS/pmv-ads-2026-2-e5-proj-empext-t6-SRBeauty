import os
import unittest

database_url_before_import = os.environ.get("DATABASE_URL")
os.environ["DATABASE_URL"] = "sqlite://"
from app import User, app, db  # noqa: E402
if database_url_before_import is None:
    os.environ.pop("DATABASE_URL", None)
else:
    os.environ["DATABASE_URL"] = database_url_before_import


class ServicesApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        with app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add_all(
                [
                    User(nome="Cliente", email="cliente@example.test", senha_hash="x", tipo="cliente"),
                    User(nome="Profissional", email="prof@example.test", senha_hash="x", tipo="profissional"),
                    User(nome="Outra profissional", email="prof2@example.test", senha_hash="x", tipo="profissional"),
                    User(nome="Proprietária", email="dona@example.test", senha_hash="x", tipo="proprietario"),
                ]
            )
            db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def create_service(self, **overrides):
        payload = {
            "nome": "Manicure",
            "descricao": "Esmaltação",
            "preco": "45.00",
            "duracao_minutos": 40,
        }
        payload.update(overrides)
        return self.client.post("/api/servicos", json=payload)

    def create_appointment(self, service_id, **overrides):
        payload = {
            "cliente_id": 1,
            "profissional_id": 2,
            "agendado_para": "2026-10-09T10:00:00-03:00",
            "servicos": [{"servico_id": service_id}],
        }
        payload.update(overrides)
        return self.client.post("/api/atendimentos", json=payload)

    def test_service_crud_and_soft_delete(self):
        created = self.create_service()
        self.assertEqual(created.status_code, 201)
        service_id = created.json["id"]
        self.assertEqual(self.client.get(f"/api/servicos/{service_id}").status_code, 200)
        self.assertEqual(self.client.get("/api/servicos").json[0]["nome"], "Manicure")

        updated = self.client.put(
            f"/api/servicos/{service_id}",
            json={
                "nome": "Manicure premium",
                "descricao": "",
                "preco": "55.50",
                "duracao_minutos": 50,
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json["preco"], "55.50")

        deleted = self.client.delete(f"/api/servicos/{service_id}")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get("/api/servicos").json, [])
        self.assertFalse(self.client.get("/api/servicos?incluir_inativos=true").json[0]["ativo"])

    def test_service_input_validation(self):
        for body in (
            {"nome": "", "preco": 10, "duracao_minutos": 20},
            {"nome": "Serviço", "preco": -1, "duracao_minutos": 20},
            {"nome": "Serviço", "preco": 1, "duracao_minutos": 0},
            {"nome": "Serviço", "preco": "1.001", "duracao_minutos": 20},
        ):
            with self.subTest(body=body):
                self.assertEqual(self.client.post("/api/servicos", json=body).status_code, 400)

    def test_appointment_snapshots_historical_price_and_service_details(self):
        service = self.create_service().json
        appointment = self.create_appointment(service["id"])
        self.assertEqual(appointment.status_code, 201)
        self.assertEqual(appointment.json["servicos"][0]["valor_cobrado"], "45.00")
        self.assertEqual(appointment.json["servicos"][0]["nome_servico"], "Manicure")

        self.client.put(
            f"/api/servicos/{service['id']}",
            json={"nome": "Manicure atualizada", "descricao": "", "preco": "70", "duracao_minutos": 60},
        )
        details = self.client.get(f"/api/atendimentos/{appointment.json['id']}").json
        self.assertEqual(details["servicos"][0]["valor_cobrado"], "45.00")
        self.assertEqual(details["servicos"][0]["nome_servico"], "Manicure")

    def test_appointment_rejects_invalid_references_and_service_data(self):
        service_id = self.create_service().json["id"]
        invalid = [
            {"cliente_id": 4},
            {"profissional_id": 1},
            {"servicos": []},
            {"agendado_para": "2026-10-09T10:00:00"},
            {"servicos": [{"servico_id": 999}]},
        ]
        for override in invalid:
            with self.subTest(override=override):
                response = self.create_appointment(service_id, **override)
                self.assertEqual(response.status_code, 400)

    def test_status_progression_and_completion_details(self):
        service_id = self.create_service().json["id"]
        appointment_id = self.create_appointment(service_id).json["id"]

        invalid = self.client.patch(
            f"/api/atendimentos/{appointment_id}/status", json={"status": "concluido"}
        )
        self.assertEqual(invalid.status_code, 409)

        started = self.client.patch(
            f"/api/atendimentos/{appointment_id}/status", json={"status": "em_atendimento"}
        )
        self.assertEqual(started.status_code, 200)
        self.assertIsNotNone(started.json["iniciado_em"])

        completed = self.client.patch(
            f"/api/atendimentos/{appointment_id}/status",
            json={
                "status": "concluido",
                "concluido_em": "2026-10-09T10:35:00-03:00",
                "duracao_real_minutos": 35,
                "observacoes": "Atendimento concluído.",
            },
        )
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.json["duracao_real_minutos"], 35)
        self.assertEqual(completed.json["observacoes"], "Atendimento concluído.")
        self.assertEqual(
            self.client.patch(
                f"/api/atendimentos/{appointment_id}/status",
                json={"status": "em_atendimento"},
            ).status_code,
            409,
        )

    def test_item_can_identify_another_executing_professional_and_charged_price(self):
        service_id = self.create_service().json["id"]
        appointment = self.create_appointment(
            service_id,
            servicos=[{"servico_id": service_id, "profissional_id": 3, "valor_cobrado": "39.90"}],
        )
        self.assertEqual(appointment.status_code, 201)
        self.assertEqual(appointment.json["servicos"][0]["profissional_id"], 3)
        self.assertEqual(appointment.json["servicos"][0]["valor_cobrado"], "39.90")

    def test_module_pages_render_and_use_existing_user_records(self):
        with self.client.session_transaction() as session:
            session["_user_id"] = "4"
            session["_fresh"] = True

        services_page = self.client.get("/servicos")
        appointments_page = self.client.get("/atendimentos")
        self.assertEqual(services_page.status_code, 200)
        self.assertIn(b"static/js/services.js", services_page.data)
        service_script = self.client.get("/static/js/services.js")
        self.assertIn(b"/api/servicos?incluir_inativos=true", service_script.data)
        service_script.close()
        self.assertEqual(appointments_page.status_code, 200)
        self.assertIn(b"Cliente", appointments_page.data)
        self.assertIn(b"Profissional", appointments_page.data)
        self.assertIn(b"static/js/appointments.js", appointments_page.data)
        appointments_script = self.client.get("/static/js/appointments.js")
        self.assertIn(b"/api/atendimentos", appointments_script.data)
        appointments_script.close()


if __name__ == "__main__":
    unittest.main()
