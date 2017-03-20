# -*- coding: UTF-8 -*-


import eventlet
eventlet.monkey_patch(os=False)



import time
import docker
import pprint
import logging

import eventlet.db_pool as db_pool # avoid catching classes that do not inherit from BaseException is not allowed



logger = logging.getLogger('swarmfetch')

def human_size(nbytes):
    import math
    SUFFIXES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    rank = int((math.log10(nbytes)) / 3)
    rank = min(rank, len(SUFFIXES) - 1)
    human = nbytes / (1024.0 ** rank)
    f = ('%.2f' % human).rstrip('0').rstrip('.')
    return '%s %s' % (f, SUFFIXES[rank])
  
  

class SwarmMetrics(object):

    TIMEOUT_SWARM   = 2
    TIMEOUT_NODE    = 2
    TIMEOUT_STAT    = 10
        
    def __init__(self, swarm_addr):
        self._swarm_addr = swarm_addr
        self._swarm_cli = docker.DockerClient(base_url=self._swarm_addr, timeout=self.TIMEOUT_SWARM)
        self._cache_cpu = {}
        self._pool = eventlet.GreenPool(20)
        
    @staticmethod
    def _sub_dict(data, keys):
        return {k:data[k] for k in keys if k in data}
    
    @staticmethod
    def _parse_swarm_systemstatus(systemstatus):
        nodes = {}
        swarm = {}
        cur_node = None
        node_count = None
        if systemstatus is None:
            return swarm, nodes
        
        for ss in systemstatus:
            if ss[0] == "Nodes":
                node_count = int(ss[1])
                continue
            if node_count is None:
                swarm[ss[0]] = ss[1]
                continue
            if ss[0].startswith("  └ "):
                nodes[cur_node][ss[0].replace("└", "").replace(" ", "")] = ss[1]
            else:
                cur_node = ss[0].strip(" ")
                nodes[cur_node] = {}
                nodes[cur_node]["url"] = ss[1]
        return swarm, nodes


    def get_swarm_metrics(self):
        swarm_metrics = {}
        swarm_metrics["swarm_version"] = self._swarm_cli.version()
        swarm_info  = self._swarm_cli.info()
        swarm_metrics["status_swarm"], swarm_metrics["status_nodes"] = self._parse_swarm_systemstatus(swarm_info["SystemStatus"])        
        swarm_metrics["status_swarm"].update(self._sub_dict(swarm_info, ["Containers", "ContainersPaused", "ContainersRunning", "ContainersStopped", "NCPU", "MemTotal", "Images"]))
        swarm_metrics["status_swarm"]["nodes"] = len(swarm_metrics["status_nodes"])
        return swarm_metrics



    def fetch_metrics(self):
        swarm_metrics = self.get_swarm_metrics()
        for name, nodes in swarm_metrics["status_nodes"].items():
            logger.debug("Update {}".format(name))
            metrics = self.get_metrics_node(nodes["url"])
            nodes.update(metrics)
        return swarm_metrics
        

    def get_metrics_node_green(self, param):
        
        try:
            return param[0], self.get_metrics_node(param[1])
        except db_pool.ConnectTimeout as ex :      
            return param[0], {"error": str(ex), "containers":{}}        
        except Exception as ex :    
            return param[0], {"error": str(ex), "containers":{}}        
        
    
    def fetch_metrics_greenpool(self):
        swarm_metrics = self.get_swarm_metrics()        
        vecs = [[name, node["url"]] for name, node in swarm_metrics["status_nodes"].items()]
        for name, metrics in self._pool.imap(self.get_metrics_node_green, vecs):
            logger.debug("Update {}".format(name))
            swarm_metrics["status_nodes"][name].update(metrics)
        return swarm_metrics

    def get_images_node_green(self, param):
        try:
            return param[0], self.get_images_node(param[1])
        except db_pool.ConnectTimeout as ex :      
            return param[0], {"error": str(ex), "images":{}}        
        except Exception as ex :    
            return param[0], {"error": str(ex), "images":{}}        
            


    def fetch_images_greenpool(self):
        swarm_metrics = self.get_swarm_metrics()        
        swarm_images = {}
        vecs = [[name, node["url"]] for name, node in swarm_metrics["status_nodes"].items()]
        for name, images in self._pool.imap(self.get_images_node_green, vecs):
            logger.debug("Update {}".format(name))
            swarm_images[name] = images
        return swarm_images
    


    @classmethod
    def pprint(cls, swarm_metrics):
        data = {}
        for name, nodes in swarm_metrics["status_nodes"].items():
            data[name] = {}
            data[name].update(cls._sub_dict(nodes, [' Reserved CPUs', ' Reserved Memory', ' Status', 'fetch_time']))
            data[name]["containers"] = {}
                          
            for cid, container in nodes["containers"].items():
                data[name]["containers"][cid] = container
                data[name]["containers"][cid]["command"] = " ".join(data[name]["containers"][cid]["command"])
                
                memory_usage = data[name]["containers"][cid]["memory_usage"]
                if memory_usage is not None:
                    memory_usage = human_size(memory_usage)
                data[name]["containers"][cid]["memory_usage"] = memory_usage
                
                cpu_percent= data[name]["containers"][cid]["cpu_percent"]
                if cpu_percent is not None:
                    cpu_percent = "{:.0f}".format(cpu_percent)
                data[name]["containers"][cid]["cpu_percent"] = cpu_percent
 
        pprint.pprint(data, width=180)
                

    def get_metrics_nodes(self, urls):
        return [self.get_metrics_node(url) for url in urls]

             

    def get_images_node(self, url):
        logger.debug("get_images_node : {}".format(url) )
        node_cli = docker.DockerClient(base_url=url, timeout=2)
        node_images = node_cli.images.list(all=False)
        images = {}
        images["images"] = {}
        total_size = 0
        for node_image in node_images:
            if len(node_image.tags) == 0: 
                continue
            else:
                images["images"][node_image.id] = {}
                images["images"][node_image.id]["RepoTags"]   = node_image.attrs.get("RepoTags", None)
                images["images"][node_image.id]["Size"]       = node_image.attrs.get("Size", None)
                images["images"][node_image.id]["Labels"]     = node_image.attrs.get("Labels", None)
                images["images"][node_image.id]["short_id"]   = node_image.short_id
                 
                
                if images["images"][node_image.id]["Size"] is not None:
                    total_size += images["images"][node_image.id]["Size"]
        images["count"] = len(images["images"])        
        images["total_size"] = total_size
        return images
            




    def get_metrics_node(self, url):
        logger.debug("get_metrics_node : {}".format(url) )
        node = {}
        containers = {}
        start_node = time.time()
        url = "tcp://" + url 
        node_cli = docker.DockerClient(base_url=url, timeout=self.TIMEOUT_NODE)
        
        if not node_cli.ping():
            logger.debug("Ping fail : {}".format(url))
            raise Exception("Ping fail : {}".format(url))
            
        version = node_cli.version()
        info = node_cli.info()
        info.pop("Swarm")
        info.update(version)
        node["info"] = info
        
        for con in node_cli.containers.list(all=True):
            start_con = time.time()
            cid = con.id
            containers[cid] = {}
            containers[cid]["name"]     = con.name
            containers[cid]["status"]   = con.status
            containers[cid]["short_id"] = con.short_id
            containers[cid]["command"]  = con.attrs["Config"]["Cmd"]
            containers[cid]["image"]    = con.attrs["Config"]["Image"] 
            containers[cid]["started_at"]  = con.attrs["State"]["StartedAt"]
            containers[cid]["finished_at"]  = con.attrs["State"]["FinishedAt"]
            logger.debug("Container : {}".format(containers[cid]) )
            stat = self.container_stat(con)
            containers[cid].update(stat)
            containers[cid]["fetch_time"] = time.time() - start_con
        node["fetch_time"] = time.time() - start_node
        node["containers"] = containers
        return node
        
        
    def container_stat(self, con):
        logger.debug("container_stat : {} {}".format(con.id, con.name))
        stats = {}
        stats["cpu_percent"] = None
        stats["memory_usage"] = None
        
        if con.status != "running":
            logger.debug("container not running : no stats")
            return stats
        try:
            con_stats = con.stats(decode=True, stream=False)
        except ValueError as ex :
            logger.debug(ex)
            logger.debug("stats parsing issue")
            return stats            
            
        except Exception as ex:
            logger.debug(ex)
            logger.debug("container no info")
            return stats
            
        try:
            memory_usage =  con_stats["memory_stats"]["usage"]
        except KeyError:
            memory_usage = None
            logger.debug("No cached value")
            
        stats["memory_usage"] = memory_usage
            
        try:
            total_usage         = con_stats["cpu_stats"]["cpu_usage"]["total_usage"]
            system_cpu_usage    = con_stats["cpu_stats"]["system_cpu_usage"]
            per_cpu_usage       = con_stats["cpu_stats"]["cpu_usage"]["percpu_usage"]
        except KeyError:
            total_usage = None
            system_cpu_usage = None
            per_cpu_usage = None
        cpu_percent = self.calculate_cpu_percent(con.id, total_usage, system_cpu_usage, per_cpu_usage)
        if cpu_percent is None:
            stats = self.container_stat(con) 
        else:
            stats["cpu_percent"]    = cpu_percent        
        
        return stats
        
        

    def calculate_cpu_percent(self, cid, total_usage, system_cpu_usage, per_cpu_usage):
        if total_usage is None or system_cpu_usage is None or per_cpu_usage is None:
            self._cache_cpu.pop(cid, None)                          # invalid cache
            return None
        
        cp = self._cache_cpu.pop(cid, None)                         # get cache prev value
        self._cache_cpu[cid] = [total_usage, system_cpu_usage]      # put value in cache
        if cp is None:                                                         
            return None  
        
        total_usage_prev        = cp[0]
        system_cpu_usage_prev   = cp[1]  
        cpu_delta       = total_usage - total_usage_prev
        system_delta    = system_cpu_usage - system_cpu_usage_prev
        if system_delta > 0.0 and cpu_delta > 0.0 :
            cpu_percent = (cpu_delta / system_delta) * len(per_cpu_usage) * 100.0
        else:
            cpu_percent = 0
        return cpu_percent





  
  
  
  
  
  



