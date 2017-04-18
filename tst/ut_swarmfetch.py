# -*- coding: UTF-8 -*-



import unittest

import swarmfetch

import pprint



SWARM_ADDR = 'server:2375'

SYSTEM_STATUS = [ ['Role', 'primary'],
                    ['Strategy', 'spread'],
                    ['Filters', 'health, port, dependency, affinity, constraint'],
                    ['Nodes', '4'],
                    [' X1', '172.20.20.22:4243'],
                    ['  └ Status', 'Healthy'],
                    ['  └ Containers', '1'],
                    ['  └ Reserved CPUs', '0 / 8'],
                    ['  └ Reserved Memory', '0 B / 16.4 GiB'],
                    ['  └ Labels', 'executiondriver=, kernelversion=3.19.0-58-generic, operatingsystem=Ubuntu 14.04.4 LTS, storagedriver=overlay'],
                    ['  └ Error', '(none)'],
                    ['  └ UpdatedAt', '2017-02-21T08:53:14Z'],
                    [' X2', '172.20.20.37:4243'],
                    ['  └ Status', 'Healthy'],
                    ['  └ Containers', '1'],
                    ['  └ Reserved CPUs', '0 / 8'],
                    ['  └ Reserved Memory', '0 B / 16.4 GiB'],
                    ['  └ Labels', 'executiondriver=, kernelversion=3.19.0-58-generic, operatingsystem=Ubuntu 14.04.4 LTS, storagedriver=overlay'],
                    ['  └ Error', '(none)'],
                    ['  └ UpdatedAt', '2017-02-21T08:53:34Z'],
                    [' X4', '172.20.20.47:4243'],
                    ['  └ Status', 'Healthy'],
                    ['  └ Containers', '2'],
                    ['  └ Reserved CPUs', '0 / 16'],
                    ['  └ Reserved Memory', '0 B / 16.34 GiB'],
                    ['  └ Labels', 'executiondriver=, kernelversion=4.2.8-040208-generic, operatingsystem=Ubuntu 14.04.4 LTS, storagedriver=overlay'],
                    ['  └ Error', '(none)'],
                    ['  └ UpdatedAt', '2017-02-21T08:53:18Z'],
                    [' X3', '172.20.20.52:4243'],
                    ['  └ Status', 'Healthy'],
                    ['  └ Containers', '1'],
                    ['  └ Reserved CPUs', '0 / 16'],
                    ['  └ Reserved Memory', '0 B / 16.35 GiB'],
                    ['  └ Labels', 'executiondriver=, kernelversion=3.19.0-59-generic, operatingsystem=Ubuntu 14.04.4 LTS, storagedriver=overlay'],
                    ['  └ Error', '(none)'],
                    ['  └ UpdatedAt', '2017-02-21T08:53:41Z'],  ]



class TestSwarmMetrics(unittest.TestCase):
    
    def setUp(self):
        pass
 
 
    def test_0(self):
        sm = swarmfetch.SwarmMetrics(SWARM_ADDR)
        swarm, nodes = sm._parse_swarm_systemstatus(SYSTEM_STATUS)
        pprint.pprint(swarm)
        pprint.pprint(nodes)
        
        
    def test_1(self):
        sm = swarmfetch.SwarmMetrics(SWARM_ADDR)
        swarm, nodes = sm._parse_swarm_systemstatus({})
        pprint.pprint(swarm)
        pprint.pprint(nodes)        
        
    def test_2(self):
        sm = swarmfetch.SwarmMetrics(SWARM_ADDR)
        param = ("test", "172.20.20.20:4243")
        sm.get_metrics_node_green(param)
        
        
    def test_3(self):
               
        node_systemtime = "2017-03-29T14:22:04.705449558+02:00"
        started_at      = "2017-03-29T12:05:28.619791993Z"
        finished_at     = "0001-01-01T00:00:00Z"
        status          = "running"
        
        res = swarmfetch.SwarmMetrics.run_time(node_systemtime, started_at, finished_at, status)
        self.assertEqual(res, 996.085658)        
        
    def test_4(self):
               
        node_systemtime = "0"
        started_at      = "2017-03-29T12:05:28.619791993Z"
        finished_at     = "0001-01-01T00:00:00Z"
        status          = "running"
        
        res = swarmfetch.SwarmMetrics.run_time(node_systemtime, started_at, finished_at, status)
        self.assertEqual(res, None)              
        

    def test_5(self):
               
        node_systemtime = "0"
        started_at      = "0001-01-01T00:00:00Z"
        finished_at     = "0001-01-01T00:00:00Z"
        status          = "created"
        
        res = swarmfetch.SwarmMetrics.run_time(node_systemtime, started_at, finished_at, status)
        self.assertEqual(res, None)   


    def test_6(self):
               
        node_systemtime = "2017-04-18T13:59:29.092462102+02:00"
        started_at      = "0001-01-01T00:00:00Z"
        finished_at     = "0001-01-01T00:00:00Z"
        status          = "running"
        
        res = swarmfetch.SwarmMetrics.run_time(node_systemtime, started_at, finished_at, status)
        self.assertEqual(res, None)   
        

if __name__ == "__main__":
    unittest.main()
    



