#! /usr/bin/python3
# -*- coding: UTF-8 -*-


import os
import sys
import json 
import time
import logging
import argparse
from datetime import datetime
from jinja2 import Template




import swarmfetch  
import elastic
import scheduler

logger = logging.getLogger('swarmfetch')




def get_update_time():
    return datetime.today()


        
    


def run(swarm_addr, html, elastic_host, refresh_time=1):

    REFRESH_IMAGE = 30
    REFRESH_CONTAINER = 5
    
    
    sc = scheduler.Scheduler()
    sc.add("image", REFRESH_IMAGE)
    sc.add("container", REFRESH_CONTAINER)
    
    ei = elastic.ElasticImages(elastic_host)
    ei.ping()
    ei.manage_index()

    ec = elastic.ElasticContainer(elastic_host)
    ec.ping()
    ec.manage_index()

    sm = swarmfetch.SwarmMetrics(swarm_addr)
    while True:
        ret = sm.fetch_metrics_greenpool()
        reti = sm.fetch_images_greenpool()
        ret["images_nodes"] = reti
        
        with open('/tmp/dump.json', 'w') as fd:
            fd.write(json.dumps(ret, indent=4))

        with open('/tmp/dump.json', "r") as fd:
            swarm = json.load(fd)
    
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template.html'), "r") as fd:
            tmpl = Template(fd.read())
    
        tmpl.globals['human_size'] = swarmfetch.human_size

        now = get_update_time()
        now_formated = now.strftime("%Y-%m-%d @ %H:%M:%S")

        if sc.is_time("image"):
            ei.add_from_swarm(swarm, now)
            sc.update_time("image")

        if sc.is_time("container"):
            ec.add_from_swarm(swarm, now)
            sc.update_time("container")

        
        res = tmpl.render(swarm_addr=swarm_addr, swarm_infos={}, swarm=swarm, update_time=now_formated)
        logger.debug("Update time {}".format(now_formated))

        
        pathfile = os.path.join(html, "index.html")
        logger.debug("Write html {}".format(pathfile))
        with open(pathfile, "w") as fd:
            fd.write(res)

        time.sleep(refresh_time)
    




if __name__ == '__main__':


    hand = logging.StreamHandler()
     
    hand.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s'))
    rootLogger = logging.getLogger("swarmfetch")
    rootLogger.setLevel(logging.DEBUG)
    rootLogger.addHandler(hand)

    parser = argparse.ArgumentParser()
    parser.add_argument('swarm_addr')
    parser.add_argument('html')
    parser.add_argument('elastic_host')
    args = parser.parse_args()
    
    logger.info(args.swarm_addr)
    logger.info(args.html)
    logger.info(args.elastic_host)
    
    elastic_host = json.loads(args.elastic_host)
      
    while True:
        try:
            run(args.swarm_addr, args.html, elastic_host)
        except KeyboardInterrupt:
            print("exit")
            sys.exit()
         
    
    
    
    


    

    

        


