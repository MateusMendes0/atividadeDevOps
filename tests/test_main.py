import unittest

from fastapi.testclient import TestClient

from main import app


class HelloTests(unittest.TestCase):
    def test_hello_retorna_a_mensagem_em_texto(self):
        with TestClient(app) as client:
            response = client.get("/hello")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Hello World 2")
        self.assertTrue(response.headers["content-type"].startswith("text/plain"))


if __name__ == "__main__":
    unittest.main()
