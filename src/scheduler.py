# -*- coding: UTF-8 -*-


import time
import logging

logger = logging.getLogger('swarmfetch')



class Scheduler(object):
    
    def __init__(self):
        self.period = {}
        self.last = {}
        
    def get_time(self):
        return time.time()
        
    def add(self, name, period):
        logger.debug("Scheduler [{}] add period {}".format(name, period))
        self.period[name] = period
        self.last[name] = None
        
    def is_time(self, name):
        if self.last[name] is None:
            ret = True
            logger.debug("Scheduler [{}] no last value => is_time=True".format(name))
        else:
            delta = self.get_time() - self.last[name]
            ret = delta >= self.period[name]
            logger.debug("Scheduler [{}] delta={} => is time={}".format(name, delta, ret))
        return ret
    
    def update_time(self, name):
        logger.debug("Scheduler [{}] update_time".format(name))
        self.last[name] = time.time()
        
                
        
    
        
        
        