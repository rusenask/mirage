import unittest
import mock
from stubo.testing import DummyTracker, DummyRequestHandler


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.patch = mock.patch('stubo.service.admin.Tracker', DummyTracker)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_get_tracks(self):
        from stubo.service.admin import get_tracks

        response = get_tracks(DummyRequestHandler(), '', '', False, 0, 100,
                              '', 0, False, '')
        self.assertEqual(response['_filter'], {'function': '',
                                               'host': 'localhost'})
        self.assertEqual(response['_skip'], 0)
        self.assertEqual(response['_limit'], 100)

    def test_get_tracks_with_args(self):
        from stubo.service.admin import get_tracks
        import datetime

        dt = datetime.datetime(2013, 12, 11, 13, 0, 0)
        response = get_tracks(DummyRequestHandler(), 'xyz', 'mangle', True, 50, 1000,
                              dt.strftime('%Y-%m-%d %H:%M:%S'), 200, True, 'get/response')
        self.assertEqual(response['_filter'], {
            'function': 'get/response',
            'scenario': {'$regex': 'xyz'},
            'request_params.session': {'$regex': 'mangle'},
            'start_time': {'$lt': dt},
            'duration_ms': {'$gt': 200},
            'return_code': {'$ne': 200}
        })
        self.assertEqual(response['_skip'], 50)
        self.assertEqual(response['_limit'], 1000)

    def test_get_tracks_with_bad_dt(self):
        from stubo.service.admin import get_tracks
        from stubo.exceptions import HTTPClientError

        with self.assertRaises(HTTPClientError):
            get_tracks(DummyRequestHandler(), '', '', False, 50, 1000,
                       '13-12-11', 0, False, '')

    def test_get_track(self):
        from stubo.service.admin import get_track

        response = get_track(DummyRequestHandler(), 123)
        self.assertEqual(response, None)
