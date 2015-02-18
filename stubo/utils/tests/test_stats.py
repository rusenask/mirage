import unittest
                
class TestStats(unittest.TestCase):
    
    def _get_cls(self):
        from stubo.utils.stats import StatsdStats
        return StatsdStats()
    
    def _get_statsd(self):
        return DummyStatsClient()
    
    def test_ctor(self):
        self.assertTrue(self._get_cls()) 
        
    def test_send(self):
        stats = self._get_cls()
        settings = dict(statsd_client=self._get_statsd(),
                        cluster_name='mycluster')
        from datetime import datetime
        track = dict(function='get/response',
                     scenario='first',
                     start_time=datetime.now(),
                     return_code=200,
                     server='my.server',
                     request_size=32,
                     host='somehost:8001',
                     session='first_1',
                     response_size=14,
                     duration_ms=8,
                     stubo_response='Hello 2 World',
                     remote_ip='1.2.3.4')
        self.assertEqual(len(settings['statsd_client'].data), 0) 
        stats.send(settings, track)  
        self.assertEqual(len(settings['statsd_client'].data), 1)
        expected = """mycluster.somehost:8001.stuboapi.get_response.latency:8|ms
mycluster.somehost:8001.stuboapi.get_response.sent:32|g
mycluster.somehost:8001.stuboapi.get_response.received:14|g
mycluster.somehost:8001.stuboapi.get_response.success:1|c
mycluster.somehost:8001.client.1_2_3_4:1|c"""
        self.assertEqual(settings['statsd_client'].data[0], expected) 
        
from statsd import StatsClient

class DummyStatsClient(StatsClient):
    
    def __init__(self):
        super(DummyStatsClient, self).__init__()
        self.data = []
    
    def _send(self, data):
        super(DummyStatsClient, self)._send(data)
        self.data.append(data)        