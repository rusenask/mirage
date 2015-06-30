import unittest

class TestCalcDelay(unittest.TestCase):

    def _get_delay(self, policy):
        from stubo.service.delay import Delay
        return Delay.parse_args(policy)
    
    def test_fixed(self):
        delay = self._get_delay(dict(delay_type='fixed', milliseconds=5))
        self.assertTrue(delay is not None)
        self.assertEqual(delay.calculate(), 5.0)
        
    def test_variable(self):
        delay = self._get_delay(dict(delay_type='normalvariate', mean=1, stddev=5))
        self.assertTrue(delay is not None)
        self.assertTrue(delay.calculate() >= 0)
        
    def test_weighted(self):
        delay = self._get_delay(dict(delay_type='weighted', delays='fixed,30000,5:normalvariate,1000,1000,15:normalvariate,500,1000,70'))
        self.assertTrue(delay is not None)  
        self.assertTrue(delay.calculate() >= 0)  
        
    def test_unknown(self):
        self.assertEqual(None, self._get_delay(dict(delay_type='bogus')))    