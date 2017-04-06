# -*- coding: UTF-8 -*-



import unittest

 
import json
import os.path
from datetime import datetime


import elastic




JSON = os.path.join(os.path.dirname(__file__), "swarm.json")


         
class SchedulerTest(unittest.TestCase):
     
    def setUp(self):
        with open(JSON, "r") as fd:
            self.swarm = json.load(fd)


    def test_0(self):
        elastic.ElasticContainer.wrapp_swarm(self.swarm, datetime.today())
        
    def test_1(self):
        elastic.ElasticImages.wrapp_swarm(self.swarm, datetime.today())        



if __name__ == "__main__":
    unittest.main()
    

