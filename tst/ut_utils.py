# -*- coding: UTF-8 -*-



import unittest




import utils




         
class SchedulerTest(unittest.TestCase):
     
    def setUp(self):
        pass
 
  

    def test_0(self):
        
        V = "registry.com:5000/test/demo:v1"
        res = utils.docker_image_parser(V)
        self.assertEqual(res, ('registry.com:5000', 'test/demo', 'v1'))
        
        V = "test/demo:v1"
        res = utils.docker_image_parser(V)
        self.assertEqual(res, (None, 'test/demo', 'v1'))

        V = "test/demo"
        res = utils.docker_image_parser(V)
        self.assertEqual(res, (None, 'test/demo', None))
        
        V = "hello-world:latest"
        res = utils.docker_image_parser(V)
        self.assertEqual(res, (None, 'hello-world', 'latest'))
        
        V = "demo:v1"
        res = utils.docker_image_parser(V)
        self.assertEqual(res, (None, 'demo', 'v1'))      

        V = "demo"
        res = utils.docker_image_parser(V)
        self.assertEqual(res, (None, 'demo', None))     
        

    def test_1(self):
        
        
        
        res = utils.human_size(10)
        self.assertEqual(res, "10 B")
        
        res = utils.human_size(10*1024)
        self.assertEqual(res, "10 KB")

        res = utils.human_size(10*1024*1024)
        self.assertEqual(res, "10 MB")
        
        res = utils.human_size(10*1024*1024*1024)
        self.assertEqual(res, "10 GB")
        
        res = utils.human_size(1025)
        self.assertEqual(res, "1 KB")
        

if __name__ == "__main__":
    unittest.main()
    

