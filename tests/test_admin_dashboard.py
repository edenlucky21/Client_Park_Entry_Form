import unittest
from app import app


class AdminDashboardTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_admin_dashboard_shows_download_pdf_action(self):
        response = self.client.get('/admin')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'View / Print', response.data)
        self.assertIn(b'Download PDF', response.data)


if __name__ == '__main__':
    unittest.main()
