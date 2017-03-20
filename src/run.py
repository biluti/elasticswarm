#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import os
import json 
import time
import logging
import argparse
from datetime import datetime
from jinja2 import Template

import swarmfetch  


logger = logging.getLogger('swarmfetch')




def get_update_time():
    now = datetime.today()
    return now.strftime("%Y-%m-%d @ %H:%M:%S")


def run(swarm_addr, html, refresh_time=1):

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
        
        
        update_time = get_update_time()
        res = tmpl.render(swarm_addr=swarm_addr, swarm_infos={}, swarm=swarm, update_time=update_time)
        logger.debug("Update time {}".format(update_time))
        
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
    args = parser.parse_args()
    print(args.swarm_addr)
    print(args.html)
        
        
      
    while True:
        try:
            run(args.swarm_addr, args.html)
        except KeyboardInterrupt:
            print("exit")
            sys.exit()
         
    
    
    
    


    

    

        


