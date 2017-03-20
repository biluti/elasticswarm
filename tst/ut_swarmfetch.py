# -*- coding: UTF-8 -*-



import unittest

import swarmfetch

import pprint

import eventlet.db_pool

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
        

        




if __name__ == "__main__":
    unittest.main()
    



