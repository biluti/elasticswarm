# -*- coding: UTF-8 -*-


import time
import unittest









import scheduler


if True:
    import logging
    hand = logging.StreamHandler()
    hand.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s'))
    rootLogger = logging.getLogger("swarmfetch")
    rootLogger.setLevel(logging.DEBUG)
    rootLogger.addHandler(hand)



         
class SchedulerTest(unittest.TestCase):
     
    def setUp(self):
        pass
 
  
    def test_0(self):
        
        sc = scheduler.Scheduler()
        
        sc.add("image", 2)
        sc.add("container", 1)
        self.assertEqual( sc.is_time("image"), True)
        self.assertEqual( sc.is_time("container"), True)
        sc.update_time("container")
        sc.is_time("container")
        self.assertEqual( sc.is_time("container"), False)
        time.sleep(2)
        self.assertEqual( sc.is_time("image"), True)
        self.assertEqual( sc.is_time("container"), True)        

        
        
        
        

if __name__ == "__main__":
    unittest.main()
    

