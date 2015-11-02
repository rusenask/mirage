import unittest

class HashTests(unittest.TestCase):

    def _makeOne(self):
        from stubo.cache import RedisCacheBackend
        import redis
        h = RedisCacheBackend(redis.Redis('localhost'))
        self.name = '_testh'
        return h
    
    def tearDown(self):
        h = self._makeOne()
        h.server.delete(self.name) 
      
    def test_set(self):
        h = self._makeOne()
        h.set(self.name, 'mykey', {'1' : 'hello'})
        self.assertTrue(h.server.hlen(self.name) == 1)
        
    def test_setget(self):
        h = self._makeOne()
        h.set(self.name, 'mykey', 'hello')
        self.assertEqual(h.get(self.name, 'mykey'), 'hello')  
        
    def test_len(self):
        h = self._makeOne()
        h.set(self.name, 'mykey', '1')
        h.set(self.name, 'mykey2', '2')
        self.assertEqual(h.server.hlen(self.name), 2)  
        
    def test_modify(self):
        h = self._makeOne()
        h.set(self.name, 'mykey', '1')
        h.set(self.name, 'mykey', '2')
        self.assertEqual(h.get(self.name, 'mykey'), '2')      
        
    def test_no_value_returns_none(self):
        h = self._makeOne()
        self.assertEqual(h.get(self.name, 'mykey'), None)
        
    def test_setget_unicode(self):
        h = self._makeOne()
        s = u'Olympic Games : Boxing : London 2012 \u2013 Boxing Welter Weight Men : 2012-08-12T12:00:00'
        h.set(self.name, 'mykey', s)
        self.assertEqual(h.get(self.name, 'mykey'), s) 
        
    def test_setget_unicode_and_ascii(self):
        h = self._makeOne()
        s = u'Olympic Games : Boxing : London 2012 \u2013 Boxing Welter Weight Men : 2012-08-12T12:00:00'
        msg = (999, s, {'1': 'hello', '2' : [3,4]})
        h.set(self.name, 'mykey', msg)
        self.assertEqual(h.get(self.name, 'mykey')[1], s)      
        
    def test_setget_complex(self):
        h = self._makeOne()
        msg = (999, 'hello', {'1': 'hello', '2' : [3,4]})
        h.set(self.name, 'mykey', msg)
        msg_back = h.get(self.name, 'mykey')       
        self.assertEqual(msg_back[0], 999)
        self.assertEqual(msg_back[1], 'hello')
        self.assertEqual(msg_back[2], {'1': 'hello', '2' : [3,4]})

class QueueTests(unittest.TestCase):

    def _makeOne(self):
        from stubo.cache.queue import Queue
        import redis
        q = Queue('_testq', redis.Redis('localhost'))
        return q
    
    def tearDown(self):
        q = self._makeOne()
        q.server.delete(q.name) 
      
    def test_put(self):
        q = self._makeOne()
        q.put({'1' : 'hello'})
        self.assertTrue(len(q) == 1)
        
    def test_putget(self):
        q = self._makeOne()
        q.put('hello')
        self.assertEqual(q.get(), 'hello')  
        
    def test_len(self):
        q = self._makeOne()
        q.put('1')
        q.put('2')
        self.assertTrue(len(q) == 2)  
        
    def test_empty_get(self):
        q = self._makeOne()
        self.assertEqual(q.get(1), None)
        self.assertEqual(q.get(), None)
        
    def test_putget_unicode(self):
        q = self._makeOne()
        s = u'Olympic Games : Boxing : London 2012 \u2013 Boxing Welter Weight Men : 2012-08-12T12:00:00'
        q.put(s)
        self.assertEqual(q.get(), s) 
        
    def test_putget_unicode_and_ascii(self):
        q = self._makeOne()
        s = u'Olympic Games : Boxing : London 2012 \u2013 Boxing Welter Weight Men : 2012-08-12T12:00:00'
        msg = (999, s, {'1': 'hello', '2' : [3,4]})
        q.put(msg)
        self.assertEqual(q.get()[1], s)      
        
    def test_putget_complex(self):
        q = self._makeOne()
        msg = (999, 'hello', {'1': 'hello', '2' : [3,4]})
        q.put(msg)
        msg_back = q.get()       
        self.assertEqual(msg_back[0], 999)
        self.assertEqual(msg_back[1], 'hello')
        self.assertEqual(msg_back[2], {'1': 'hello', '2' : [3,4]})
        
    def test_iter(self):
        q = self._makeOne()
        q.put(1)
        q.put(2)
        result = [x for x in q]
        self.assertEqual([1,2], result)
        self.assertTrue(len(q) == 2) 
        
    def test_iter_with_start(self):
        q = self._makeOne()
        for i in range(10):
            q.put(i)
        from stubo.cache.queue import QueueIterator
        qiter = QueueIterator(q, 5)
        result = [x for x in qiter]
        self.assertEqual(range(5,10), result)
        self.assertTrue(len(q) == 10)   
        
           
        
            
         
           
    
        
   