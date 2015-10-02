import unittest
import mock
from stubo.testing import DummyTracker, DummyRequestHandler


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.patch = mock.patch('stubo.service.admin.Tracker', DummyTracker)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_get_track(self):
        from stubo.service.admin import get_track

        response = get_track(DummyRequestHandler(), 123)
        self.assertEqual(response, None)
