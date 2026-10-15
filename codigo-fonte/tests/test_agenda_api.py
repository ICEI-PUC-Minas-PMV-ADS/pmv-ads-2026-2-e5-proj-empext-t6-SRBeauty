import os
import unittest

database_url_before_import = os.environ.get("DATABASE_URL")
os.environ["DATABASE_URL"] = "sqlite://"
from app import User, app, db  # noqa: E402
if database_url_before_import is None:
    os.environ.pop("DATABASE_URL", None)
else:
    os.environ["DATABASE_URL"] = database_url_before_import


class AgendaApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        with app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add_all(
                [
                    User(nome="Cliente", email="cliente-agenda@example.test", senha_hash="x", tipo="cliente"),
                    User(nome="Profissional", email="prof-agenda@example.test", senha_hash="x", tipo="profissional"),
                    User(nome="Outra profissional", email="prof2-agenda@example.test", senha_hash="x", tipo="profissional"),
                    User(nome="Proprietária", email="dona-agenda@example.test", senha_hash="x", tipo="proprietario"),
                ]
            )
            db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login_as(self, user_id):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(user_id)
            session["_fresh"] = True

    def create_service(self, duration=60):
        return self.client.post(
            "/api/servicos",
            json={
                "nome": "Corte",
                "descricao": "",
                "preco": "50.00",
                "duracao_minutos": duration,
            },
        ).json["id"]

    def create_appointment(self, service_id, at="2026-10-09T10:00:00-03:00", **overrides):
        payload = {
            "cliente_id": 1,
            "profissional_id": 2,
            "agendado_para": at,
            "servicos": [{"servico_id": service_id}],
        }
        payload.update(overrides)
        return self.client.post("/api/atendimentos", json=payload)

    def test_schedule_crud_multiple_intervals_and_overlap_validation(self):
        self.login_as(4)
        morning = {
            "profissional_id": 2,
            "dia_semana": 4,
            "inicio": "09:00",
            "fim": "12:00",
        }
        created = self.client.post("/api/horarios", json=morning)
        self.assertEqual(created.status_code, 201)
        schedule_id = created.json["id"]
        afternoon = {**morning, "inicio": "13:00", "fim": "18:00"}
        self.assertEqual(self.client.post("/api/horarios", json=afternoon).status_code, 201)
        overlapping = {**morning, "inicio": "11:30", "fim": "14:00"}
        self.assertEqual(self.client.post("/api/horarios", json=overlapping).status_code, 409)
        self.assertEqual(self.client.get("/api/horarios?profissional_id=2").json[0]["dia_semana_nome"], "Sexta-feira")

        updated = self.client.put(
            f"/api/horarios/{schedule_id}",
            json={**morning, "inicio": "08:30", "fim": "12:00"},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json["inicio"], "08:30")
        self.assertEqual(self.client.delete(f"/api/horarios/{schedule_id}").status_code, 204)
        self.assertEqual(len(self.client.get("/api/horarios?profissional_id=2").json), 1)

    def test_schedule_batch_creates_same_interval_for_multiple_weekdays_atomically(self):
        self.login_as(4)
        payload = {
            "profissional_id": 2,
            "dias_semana": [0, 1, 2, 3, 4, 5],
            "inicio": "09:00",
            "fim": "18:00",
        }
        created = self.client.post("/api/horarios/lote", json=payload)
        self.assertEqual(created.status_code, 201)
        self.assertEqual([item["dia_semana"] for item in created.json], [0, 1, 2, 3, 4, 5])
        self.assertEqual(len(self.client.get("/api/horarios?profissional_id=2").json), 6)

        conflict = self.client.post(
            "/api/horarios/lote",
            json={**payload, "dias_semana": [0, 6], "inicio": "10:00", "fim": "11:00"},
        )
        self.assertEqual(conflict.status_code, 409)
        schedules = self.client.get("/api/horarios?profissional_id=2").json
        self.assertEqual(len(schedules), 6)
        self.assertNotIn(6, [item["dia_semana"] for item in schedules])

    def test_appointment_rejects_overlapping_duration_and_accepts_adjacent_slot(self):
        service_id = self.create_service(duration=60)
        first = self.create_appointment(service_id)
        self.assertEqual(first.status_code, 201)
        same_minute_other_offset = self.create_appointment(
            service_id, at="2026-10-09T13:00:00Z"
        )
        self.assertEqual(same_minute_other_offset.status_code, 409)
        overlap = self.create_appointment(service_id, at="2026-10-09T10:30:00-03:00")
        self.assertEqual(overlap.status_code, 409)
        exact_end = self.create_appointment(service_id, at="2026-10-09T11:00:00-03:00")
        self.assertEqual(exact_end.status_code, 201)

    def test_schedule_enforces_day_and_lunch_gap_for_bookings(self):
        self.login_as(4)
        self.client.post(
            "/api/horarios",
            json={"profissional_id": 2, "dia_semana": 4, "inicio": "09:00", "fim": "12:00"},
        )
        self.client.post(
            "/api/horarios",
            json={"profissional_id": 2, "dia_semana": 4, "inicio": "13:00", "fim": "18:00"},
        )
        service_id = self.create_service(duration=60)
        crosses_lunch = self.create_appointment(service_id, at="2026-10-09T11:30:00-03:00")
        self.assertEqual(crosses_lunch.status_code, 409)
        outside_shift = self.create_appointment(service_id, at="2026-10-09T18:00:00-03:00")
        self.assertEqual(outside_shift.status_code, 409)
        within_shift = self.create_appointment(service_id, at="2026-10-09T13:00:00-03:00")
        self.assertEqual(within_shift.status_code, 201)

    def test_blocks_crud_and_prevent_bookings(self):
        self.login_as(4)
        payload = {
            "profissional_id": 2,
            "inicio": "2026-10-09T14:00:00-03:00",
            "fim": "2026-10-09T16:00:00-03:00",
            "motivo": "Consulta médica",
        }
        created = self.client.post("/api/bloqueios", json=payload)
        self.assertEqual(created.status_code, 201)
        block_id = created.json["id"]
        self.assertEqual(created.json["motivo"], "Consulta médica")
        service_id = self.create_service(duration=30)
        self.assertEqual(
            self.create_appointment(service_id, at="2026-10-09T15:00:00-03:00").status_code,
            409,
        )
        updated = self.client.put(
            f"/api/bloqueios/{block_id}",
            json={**payload, "inicio": "2026-10-09T16:00:00-03:00", "fim": "2026-10-09T17:00:00-03:00"},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.delete(f"/api/bloqueios/{block_id}").status_code, 204)

    def test_daily_weekly_views_and_role_scoping(self):
        service_id = self.create_service(duration=30)
        self.assertEqual(self.create_appointment(service_id).status_code, 201)
        self.login_as(4)
        daily = self.client.get("/api/agenda/diaria?data=2026-10-09")
        self.assertEqual(daily.status_code, 200)
        self.assertEqual(daily.json["eventos"][0]["tipo"], "atendimento")
        self.assertEqual(daily.json["eventos"][0]["cliente_nome"], "Cliente")
        weekly = self.client.get("/api/agenda/semanal?semana=2026-10-09&profissional_id=2")
        self.assertEqual(weekly.status_code, 200)
        self.assertEqual(weekly.json["inicio"], "2026-10-05")

        self.login_as(2)
        own_agenda = self.client.get("/api/agenda/diaria?data=2026-10-09")
        self.assertEqual(own_agenda.status_code, 200)
        self.assertEqual(
            self.client.get("/api/agenda/diaria?data=2026-10-09&profissional_id=3").status_code,
            403,
        )
        agenda_page = self.client.get("/agenda")
        self.assertEqual(agenda_page.status_code, 200)
        self.assertIn(b"static/js/agenda.js", agenda_page.data)
        agenda_script = self.client.get("/static/js/agenda.js")
        self.assertEqual(agenda_script.status_code, 200)
        agenda_script.close()

        self.login_as(1)
        self.assertEqual(self.client.get("/api/agenda/diaria").status_code, 403)
        self.assertEqual(self.client.get("/agenda").status_code, 403)

    def test_agenda_endpoints_require_authentication(self):
        self.assertEqual(self.client.get("/api/agenda/diaria").status_code, 401)
        self.assertEqual(self.client.get("/api/horarios").status_code, 401)


if __name__ == "__main__":
    unittest.main()
