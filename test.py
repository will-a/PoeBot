import unittest
from bot import get_url_info

class TestPoeBot(unittest.TestCase):

    def test_get_url_info_alphanum(self):
        url_res, uid_res = get_url_info('https://pobb.in/3F8Ot7vXFll1')
        self.assertEqual(url_res, 'pobb.in')
        self.assertEqual(uid_res, '3F8Ot7vXFll1')

    def test_get_url_info_hyphen(self):
        url_res, uid_res = get_url_info('https://pobb.in/OlGEX2hMf8-g')
        self.assertEqual(url_res, 'pobb.in')
        self.assertEqual(uid_res, 'OlGEX2hMf8-g')
