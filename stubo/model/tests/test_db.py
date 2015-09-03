import unittest


class TestFunctions(unittest.TestCase):
    def test_coerce_mongo_param(self):
        from stubo.model.db import coerce_mongo_param

        self.assertEqual(8001, coerce_mongo_param('port', '8001'))
        self.assertEqual(8001, coerce_mongo_param('port', 8001))
        self.assertEqual(10, coerce_mongo_param('max_pool_size', '10'))
        self.assertEqual(True, coerce_mongo_param('tz_aware', 'true'))
        self.assertEqual(True, coerce_mongo_param('tz_aware', True))
        self.assertEqual(False, coerce_mongo_param('tz_aware', 0))
        self.assertEqual(0, coerce_mongo_param('bogus', 0))

    def test_get_connection(self):
        from stubo.model.db import get_connection

        conn = get_connection({'host': 'localhost', 'max_pool_size': 20, 'port': 27017})
        self.assertEqual(conn.host, 'localhost')
        self.assertEqual(conn.port, 27017)
        self.assertEqual(conn.max_pool_size, 20)

    def test_get_connection_with_db(self):
        from stubo.model.db import get_connection, default_env

        conn = get_connection()
        self.assertEqual(conn.name, default_env['db'])
