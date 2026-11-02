"""Executable checks derived from the submitted URS, with isolated sample data."""
import tempfile
import time
import unittest
from pathlib import Path

from bookbridge import create_app


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = {"TESTING": True, "DATABASE": str(Path(self.temp.name) / "test.sqlite"), "SECRET_KEY": "test-only-secret"}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.key = 0
        self.login("customer1")

    def tearDown(self):
        self.temp.cleanup()

    def login(self, identity):
        token = self.client.get("/api/session").get_json()["csrf_token"]
        response = self.client.post("/api/session", json={"identity_id": identity}, headers={"X-CSRF-Token": token})
        self.assertEqual(response.status_code, 200, response.get_json())
        self.token = self.client.get("/api/session").get_json()["csrf_token"]

    def mutate(self, path, payload=None, method="post", expected=(200, 201)):
        response = getattr(self.client, method)(path, json=payload or {}, headers={"X-CSRF-Token": self.token})
        self.assertIn(response.status_code, expected, (path, response.status_code, response.get_json()))
        return response.get_json()

    def book(self, book_id=1):
        result = self.client.get(f"/api/books/{book_id}")
        self.assertEqual(result.status_code, 200)
        data = result.get_json()
        return data.get("book", data)

    def reserve(self, quantity=2, book_id=1, request_key=None, expected=(200, 201)):
        self.key += 1
        result = self.mutate("/api/reservations", {"book_id": book_id, "quantity": quantity, "request_key": request_key or f"test-request-{self.key}"}, expected=expected)
        return result.get("reservation", result)

    def test_at01_catalogue_receipts_and_discovery(self):
        books = self.client.get("/api/books").get_json()["books"]
        self.assertEqual(len(books), 20)
        self.login("staff1")
        added = self.mutate("/api/books", {"title": "Acceptance Book", "author": "Sample Author", "category": "Testing", "price": "12.50", "available_quantity": 5, "is_listed": True})["book"]
        self.mutate(f"/api/books/{added['id']}/receipts", {"quantity": 3})
        self.assertEqual(self.book(added["id"])["available_quantity"], 8)
        for value in [0, -1, 1.5, "", True]:
            self.mutate(f"/api/books/{added['id']}/receipts", {"quantity": value}, expected=(400, 422))
        self.assertEqual(self.book(added["id"])["available_quantity"], 8)
        for price in ["NaN", "Infinity", "-1", "1.234"]:
            self.mutate(f"/api/books/{added['id']}", {"price": price}, method="patch", expected=(400, 422))
        self.login("customer1")
        found = self.client.get("/api/books?q=Sample+Author&category=Testing").get_json()["books"]
        self.assertEqual([b["id"] for b in found], [added["id"]])
        for sort, reverse in [("price_asc", False), ("price_desc", True)]:
            prices = [b["price_cents"] for b in self.client.get(f"/api/books?sort={sort}").get_json()["books"]]
            self.assertEqual(prices, sorted(prices, reverse=reverse))
        self.assertEqual(self.client.get("/api/books?q=nonexistentzzzz").get_json()["books"], [])

    def test_at02_create_once_and_preserve_price(self):
        reservation = self.reserve(request_key="double-click")
        again = self.reserve(request_key="double-click")
        self.assertEqual(reservation["id"], again["id"])
        self.assertEqual(reservation["amount_cents"], 6000)
        self.assertEqual(reservation["unit_price_cents"], 3000)
        self.assertEqual(reservation["status"], "Pending collection")
        self.assertEqual(self.book()["available_quantity"], 3)
        self.assertEqual(len(self.client.get("/api/reservations").get_json()["reservations"]), 1)
        self.reserve(quantity=1, request_key="double-click", expected=(409,))
        self.assertEqual(self.book()["available_quantity"], 3)

    def test_at03_invalid_quantities_do_not_change_stock(self):
        for value in ["", 0, -1, 1.5, 6, True, None]:
            self.reserve(quantity=value, expected=(400, 409, 422))
        self.assertEqual(self.book()["available_quantity"], 5)
        self.assertEqual(self.client.get("/api/reservations").get_json()["reservations"], [])
        self.assertEqual(self.book(19)["available_quantity"], 0)
        self.reserve(book_id=19, quantity=1, expected=(400, 409, 422))

    def test_at04_owner_only_cancel_restore_once(self):
        reservation = self.reserve()
        rid = reservation["id"]
        self.login("customer2")
        self.assertIn(self.client.get(f"/api/reservations/{rid}").status_code, (403, 404))
        self.mutate(f"/api/reservations/{rid}/cancel", expected=(403, 404))
        self.assertEqual(self.book()["available_quantity"], 3)
        self.login("customer1")
        self.mutate(f"/api/reservations/{rid}/cancel")
        repeated = self.mutate(f"/api/reservations/{rid}/cancel", expected=(409,))
        self.assertIn("already cancelled", repeated["error"])
        self.assertEqual(self.book()["available_quantity"], 5)
        self.assertEqual(self.client.get("/api/reservations").get_json()["reservations"][0]["status"], "Cancelled")

    def test_at05_collection_keeps_price_and_stock(self):
        reservation = self.reserve()
        self.login("staff1")
        self.mutate("/api/books/1", {"price": "50.00"}, method="patch")
        self.mutate(f"/api/reservations/{reservation['id']}/complete")
        repeated = self.mutate(f"/api/reservations/{reservation['id']}/complete", expected=(409,))
        self.assertIn("already completed", repeated["error"])
        self.assertEqual(self.book()["available_quantity"], 3)
        result = self.client.get("/api/summary").get_json()
        self.assertEqual((result["completed_quantity"], result["amount_cents"], result["count"]), (2, 6000, 1))
        self.login("customer1")
        self.mutate(f"/api/reservations/{reservation['id']}/cancel", expected=(400, 409))

    def test_at06_unlist_preserves_pending_records_and_roles(self):
        first = self.reserve(quantity=1)
        second = self.reserve(quantity=1)
        self.mutate("/api/books/1/receipts", {"quantity": 1}, expected=(403,))
        self.mutate("/api/books/1", {"title": "No"}, method="patch", expected=(403,))
        self.mutate(f"/api/reservations/{first['id']}/complete", expected=(403,))
        self.assertEqual(self.client.get("/api/summary").status_code, 403)
        self.login("staff1")
        self.mutate("/api/books/1", {"is_listed": False}, method="patch")
        self.mutate(f"/api/reservations/{second['id']}/complete")
        self.login("customer1")
        self.assertNotIn(1, [b["id"] for b in self.client.get("/api/books").get_json()["books"]])
        self.reserve(quantity=1, expected=(400, 404, 409, 422))
        self.mutate(f"/api/reservations/{first['id']}/cancel")
        self.assertEqual(len(self.client.get("/api/reservations").get_json()["reservations"]), 2)
        self.login("staff1")
        self.assertEqual(self.book()["available_quantity"], 4)

    def test_at07_owner_scoping_and_status_filters(self):
        first = self.reserve(quantity=1)
        self.login("customer2")
        second = self.reserve(quantity=1)
        own = self.client.get("/api/reservations").get_json()["reservations"]
        self.assertEqual([r["id"] for r in own], [second["id"]])
        self.login("staff1")
        self.assertEqual(len(self.client.get("/api/reservations").get_json()["reservations"]), 2)
        self.mutate(f"/api/reservations/{first['id']}/complete")
        completed = self.client.get("/api/reservations?status=Completed").get_json()["reservations"]
        self.assertEqual([r["id"] for r in completed], [first["id"]])
        self.assertEqual(self.client.get("/api/reservations?status=Cancelled").get_json()["reservations"], [])

    def test_at08_summary_excludes_pending_and_cancelled(self):
        first = self.reserve(quantity=2)
        self.login("staff1")
        self.mutate("/api/books/1", {"price": "20.00"}, method="patch")
        self.login("customer1")
        second = self.reserve(quantity=1)
        pending = self.reserve(quantity=1)
        cancelled = self.reserve(quantity=1)
        self.mutate(f"/api/reservations/{cancelled['id']}/cancel")
        self.login("staff1")
        self.mutate(f"/api/reservations/{first['id']}/complete")
        self.mutate(f"/api/reservations/{second['id']}/complete")
        summary = self.client.get("/api/summary").get_json()
        self.assertEqual((summary["completed_quantity"], summary["amount_cents"], summary["count"]), (3, 8000, 2))
        self.assertEqual(self.client.get("/api/summary").get_json(), summary)
        self.assertEqual(self.book()["available_quantity"], 1)

    def test_at09_persistence_and_api_response_at_sample_capacity(self):
        self.login("staff1")
        self.mutate("/api/books/1/receipts", {"quantity": 100})
        self.login("customer1")
        for i in range(100):
            reservation = self.reserve(quantity=1)
            if i % 3 == 0:
                self.mutate(f"/api/reservations/{reservation['id']}/cancel")
            elif i % 3 == 1:
                self.login("staff1")
                self.mutate(f"/api/reservations/{reservation['id']}/complete")
                self.login("customer1")
        start = time.perf_counter()
        before = self.client.get("/api/reservations").get_json()["reservations"]
        self.assertEqual(len(before), 100)
        self.assertLess(time.perf_counter() - start, 3)
        stock = self.book()["available_quantity"]
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.login("customer1")
        after = self.client.get("/api/reservations").get_json()["reservations"]
        self.assertEqual(before, after)
        self.assertEqual(stock, self.book()["available_quantity"])
        self.assertEqual(len(self.client.get("/api/books").get_json()["books"]), 20)

    def test_csrf_and_no_overselling(self):
        self.assertEqual(self.client.post("/api/reservations", json={"book_id": 1, "quantity": 1, "request_key": "bad-csrf"}).status_code, 403)
        self.assertEqual(self.client.post("/api/reservations", json={}, headers={"X-CSRF-Token": "invalid-\u4e2d"}).status_code, 403)
        self.reserve(quantity=5)
        self.login("customer2")
        self.reserve(quantity=1, expected=(400, 409, 422))
        self.assertEqual(self.book()["available_quantity"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
