import unittest
import mock
from stubo.testing import DummyQueue


class TestModule(unittest.TestCase):
    def setUp(self):
        self.q = DummyQueue
        self.q_patch = mock.patch('stubo.ext.module.Queue', self.q)
        self.q_patch.start()

    def tearDown(self):
        import sys

        test_modules = [x for x in sys.modules.keys() if x.startswith('localhost_stubotest')]
        for mod in test_modules:
            del sys.modules[mod]
        self.q_patch.stop()

    def _get_module(self):
        from stubo.ext.module import Module

        return Module('localhost')

    def test_add_sys_module(self):
        import sys

        code, module = self._get_module().add_sys_module(
            'localhost_stubotest_foo',
            'print "hello"')
        self.assertEqual(sys.modules['localhost_stubotest_foo'], module)

    def test_remove_sys_module(self):
        import sys

        m = self._get_module()
        m.add_sys_module('localhost_stubotest_foo', 'x = "hello"')
        m.remove_sys_module('localhost_stubotest_foo')
        self.assertTrue('localhost_stubotest_foo' not in sys.modules.keys())

    def test_get_raises_if_source_not_found(self):
        from stubo.exceptions import HTTPServerError

        with self.assertRaises(HTTPServerError):
            self._get_module().get_sys_module('stubotest_bogus', 1)

    def test_get_lazyload(self):
        import sys

        m = self._get_module()
        m.add('stubotest_foo', 'x = "hello"')
        module = m.get_sys_module("stubotest_foo", 1)
        self.assertEqual(sys.modules['localhost_stubotest_foo_v1'], module)

    def test_get_raises_if_not_found(self):
        from stubo.exceptions import UserExitModuleNotFound

        m = self._get_module()
        with self.assertRaises(UserExitModuleNotFound):
            m.get('stubotest_bogus')

    def test_add(self):
        m = self._get_module()
        m.add('stubotest_bar', "x = 'hello'")
        self.assertEqual(m.get_source('stubotest_bar', 1), "x = 'hello'")

    def test_remove(self):
        m = self._get_module()
        m.add('stubotest_bar', "x = 'hello'")
        m.remove('stubotest_bar')
        self.assertEqual(m.get_source('stubotest_bar', 1), None)

    def test_get(self):
        import sys

        m = self._get_module()
        m.add('stubotest_xxx', "x = 'hello'")
        module = m.get('stubotest_xxx', version=1)
        self.assertEqual(sys.modules['localhost_stubotest_xxx_v1'], module)
