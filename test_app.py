import unittest
from unittest.mock import patch

import app


class FakeCursor:
    def __init__(self):
        self.queries = []
        self.total_loads = 0

    def execute(self, query, parameters=None):
        self.queries.append((query, parameters))
        if parameters is not None:
            self.total_loads += parameters[0]

    def fetchone(self):
        return (self.total_loads,)

    def close(self):
        pass


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def close(self):
        self.closed = True


class RecordLoadsTests(unittest.TestCase):
    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def test_records_load_amount_and_returns_total(self):
        connection = FakeConnection()
        with patch.object(app, "get_database_connection", return_value=connection):
            response = self.client.post("/api/loads", json={"loads": 3})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"total_loads": 3})
        self.assertEqual(
            connection.cursor_instance.queries[0][1],
            (3, 3),
        )
        self.assertTrue(connection.committed)
        self.assertTrue(connection.closed)

    def test_rejects_non_positive_or_non_integer_loads(self):
        for value in (0, -1, 1.5, True, "2", None):
            with self.subTest(value=value):
                response = self.client.post("/api/loads", json={"loads": value})
                self.assertEqual(response.status_code, 400)

    def test_rejects_missing_loads(self):
        response = self.client.post("/api/loads", json={})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
