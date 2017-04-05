# -*- coding: UTF-8 -*-



import unittest

import json
from datetime import datetime


import elastic


TMP_JSON = "swarm.json"

         
class SchedulerTest(unittest.TestCase):
     
    def setUp(self):
        with open(TMP_JSON, "r") as fd:
            self.swarm = json.load(fd)


    def test_0(self):
        elastic.ElasticContainer.wrapp_swarm(self.swarm, datetime.today())
        
    def test_1(self):
        elastic.ElasticImages.wrapp_swarm(self.swarm, datetime.today())        



if __name__ == "__main__":
    unittest.main()
    

