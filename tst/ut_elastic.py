# -*- coding: UTF-8 -*-



import unittest



import elastic



DATA  = {       
         
        "timestamp"     : "2017-03-21T15:10:47.978+01",
        "node_name"     : "X1",
        "node_ip"       : "172.20.20.20",
        "image_id"      : "sha256:7003800150",
        "size"          : 5000000,
        }    
        


import logging

hand = logging.StreamHandler()
hand.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s'))
rootLogger = logging.getLogger("swarmfetch")
rootLogger.setLevel(logging.DEBUG)
rootLogger.addHandler(hand)



HOST_PROD = [{"host":"parvnlbes01prd", "port":9200, "http_auth":('elastic', 'aonI9Eifii'),}]


         
class ElasticImagesTest(unittest.TestCase):
     
    def setUp(self):
         
        #trace = None
         
        self.da = elastic.ElasticImages(HOST_PROD, test=True)
        self.da.manage_index()
 
  
    def test_0(self):
        self.da.add_doc(DATA)
        self.assertEqual({'test-es-images': [u'9e628c57f731a2f391d26133248e8c31']}, self.da.stat_get())
 
  
    def test_1(self):
         
        import json
        with open('/tmp/dump.json', "r") as fd:
            swarm = json.load(fd)
        from datetime import datetime
        self.da.add_from_swarm(swarm, datetime.today())


#          
# class ElasticContainerTest(unittest.TestCase):
#     
#     def setUp(self):
#         
#         #trace = None
#         
#         self.da = elastic.ElasticContainer(HOST_PROD, test=True)
#         self.da.manage_index()
#         
#         
#     def test_2(self):
#         
#         import json
#         with open('/tmp/dump.json', "r") as fd:
#             swarm = json.load(fd)
#         from datetime import datetime
#         self.da.add_from_swarm(swarm, datetime.today())
# 
# 
# 
#        

if __name__ == "__main__":
    unittest.main()
    

