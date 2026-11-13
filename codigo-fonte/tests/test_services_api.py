import os
import unittest
from datetime import datetime, timedelta

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
                    User(nome="Outra cliente", email="cliente2@example.test", senha_hash="x", tipo="cliente"),
                ]
            )
            db.session.commit()
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session["_user_id"] = "4"
            session["_fresh"] = True

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

    def test_cliente_consulta_servicos_sem_controles_ou_permissao_de_edicao(self):
        created = self.create_service()
        self.assertEqual(created.status_code, 201)
        service_id = created.json["id"]
        inactive_id = self.create_service(nome="Serviço inativo").json["id"]
        self.assertEqual(self.client.delete(f"/api/servicos/{inactive_id}").status_code, 204)
        with self.client.session_transaction() as session:
            session["_user_id"] = "1"
            session["_fresh"] = True

        page = self.client.get("/servicos")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Consulte os pre", page.data)
        self.assertNotIn(b"newServiceButton", page.data)
        self.assertNotIn(b"serviceDialog", page.data)

        catalog = self.client.get("/api/servicos")
        self.assertEqual(catalog.status_code, 200)
        self.assertEqual([service["id"] for service in catalog.json], [service_id])
        self.assertEqual(catalog.json[0]["preco"], "45.00")
        self.assertEqual(
            self.client.get("/api/servicos?incluir_inativos=true").status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                "/api/servicos",
                json={
                    "nome": "Novo serviço",
                    "preco": "30.00",
                    "duracao_minutos": 30,
                },
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.put(
                f"/api/servicos/{service_id}",
                json={
                    "nome": "Manicure alterada",
                    "preco": "30.00",
                    "duracao_minutos": 30,
                },
            ).status_code,
            403,
        )
        self.assertEqual(self.client.delete(f"/api/servicos/{service_id}").status_code, 403)
        self.assertEqual(
            self.client.get(f"/api/servicos/{service_id}").json["nome"],
            "Manicure",
        )
        self.assertEqual(
            app.test_client().post(
                "/api/servicos",
                json={
                    "nome": "Serviço sem sessão",
                    "preco": "30.00",
                    "duracao_minutos": 30,
                },
            ).status_code,
            401,
        )
        self.assertEqual(
            app.test_client().get("/api/servicos?incluir_inativos=true").status_code,
            401,
        )
        professional_client = app.test_client()
        with professional_client.session_transaction() as session:
            session["_user_id"] = "2"
            session["_fresh"] = True
        self.assertEqual(
            professional_client.post(
                "/api/servicos",
                json={
                    "nome": "Corte",
                    "preco": "50.00",
                    "duracao_minutos": 45,
                },
            ).status_code,
            403,
        )
        self.assertNotIn(b"newServiceButton", professional_client.get("/servicos").data)

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
        completed_at = (
            datetime.fromisoformat(started.json["iniciado_em"]) + timedelta(minutes=35)
        ).isoformat()

        completed = self.client.patch(
            f"/api/atendimentos/{appointment_id}/status",
            json={
                "status": "concluido",
                "concluido_em": completed_at,
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

    def test_customer_appointments_are_scoped_to_session_and_cannot_change_status(self):
        service_id = self.create_service().json["id"]
        own_appointment = self.create_appointment(service_id).json
        other_appointment = self.create_appointment(
            service_id,
            cliente_id=5,
            agendado_para="2026-10-09T12:00:00-03:00",
        ).json

        with self.client.session_transaction() as session:
            session["_user_id"] = "1"
            session["_fresh"] = True

        appointments = self.client.get("/api/atendimentos")
        self.assertEqual(appointments.status_code, 200)
        self.assertEqual([item["id"] for item in appointments.json], [own_appointment["id"]])
        self.assertEqual(
            self.client.get(f"/api/atendimentos/{other_appointment['id']}").status_code,
            404,
        )
        self.assertEqual(
            self.client.patch(
                f"/api/atendimentos/{own_appointment['id']}/status",
                json={"status": "em_atendimento"},
            ).status_code,
            403,
        )

    def test_customer_request_uses_session_customer_and_catalog_service_price(self):
        service = self.create_service().json
        with self.client.session_transaction() as session:
            session["_user_id"] = "1"
            session["_fresh"] = True

        response = self.client.post(
            "/api/atendimentos",
            json={
                "cliente_id": 5,
                "profissional_id": 2,
                "agendamento_id": 999,
                "agendado_para": "2026-10-09T10:00:00-03:00",
                "status": "concluido",
                "servicos": [
                    {
                        "servico_id": service["id"],
                        "profissional_id": 3,
                        "valor_cobrado": "0.01",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["cliente_id"], 1)
        self.assertEqual(response.json["status"], "aguardando")
        self.assertIsNone(response.json["agendamento_id"])
        self.assertEqual(response.json["servicos"][0]["profissional_id"], 2)
        self.assertEqual(response.json["servicos"][0]["valor_cobrado"], "45.00")

    def test_appointment_and_service_catalog_apis_require_authentication(self):
        anonymous = app.test_client()
        self.assertEqual(anonymous.get("/api/servicos").status_code, 401)
        self.assertEqual(anonymous.get("/api/servicos/1").status_code, 401)
        self.assertEqual(anonymous.get("/api/atendimentos").status_code, 401)
        self.assertEqual(anonymous.get("/api/atendimentos/1").status_code, 401)
        self.assertEqual(
            anonymous.post("/api/atendimentos", json={}).status_code,
            401,
        )
        self.assertEqual(
            anonymous.patch("/api/atendimentos/1/status", json={"status": "em_atendimento"}).status_code,
            401,
        )

    def test_module_pages_render_and_use_existing_user_records(self):
        with self.client.session_transaction() as session:
            session["_user_id"] = "4"
            session["_fresh"] = True

        services_page = self.client.get("/servicos")
        appointments_page = self.client.get("/atendimentos")
        menu_paths = ("/home", "/agenda", "/perfil", "/repasses")
        menu_pages = [self.client.get(path) for path in menu_paths]
        self.assertEqual(services_page.status_code, 200)
        self.assertIn(b"static/js/services.js", services_page.data)
        service_script = self.client.get("/static/js/services.js")
        self.assertIn(b"/api/servicos?incluir_inativos=true", service_script.data)
        service_script.close()
        self.assertEqual(appointments_page.status_code, 200)
        self.assertIn(b"Cliente", appointments_page.data)
        self.assertIn(b"Profissional", appointments_page.data)
        self.assertIn(b"static/js/appointments.js", appointments_page.data)
        for page in [services_page, appointments_page, *menu_pages]:
            self.assertNotIn(b"<span>Clientes</span>", page.data)
            self.assertNotIn(b"<span>Profissionais</span>", page.data)
        for path, page in zip(menu_paths, menu_pages):
            with self.subTest(path=path):
                self.assertIn(b'href="/agenda"', page.data)
        self.assertEqual(self.client.get("/agenda").status_code, 200)
        appointments_script = self.client.get("/static/js/appointments.js")
        self.assertIn(b"/api/atendimentos", appointments_script.data)
        appointments_script.close()

    def test_customer_appointments_page_only_exposes_own_customer_and_request_controls(self):
        with self.client.session_transaction() as session:
            session["_user_id"] = "1"
            session["_fresh"] = True

        page = self.client.get("/atendimentos")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Solicitar atendimento", page.data)
        self.assertNotIn(b'name="cliente_id"', page.data)
        self.assertNotIn(b"Outra cliente", page.data)
        self.assertNotIn(b"agendamento_id", page.data)
        script = self.client.get("/static/js/appointments.js")
        self.assertIn(b"data-user-type", page.data)
        self.assertIn(b"valor_cobrado", script.data)
        script.close()


if __name__ == "__main__":
    unittest.main()
