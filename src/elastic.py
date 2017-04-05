# -*- coding: UTF-8 -*-



import pprint
import hashlib
import logging
import datetime
import elasticsearch


from addict import Dict
from elasticsearch import helpers

from utils import docker_image_parser

logger = logging.getLogger('swarmfetch')




class ElasticSwarmError(Exception):
    pass


class ElasticBase(object):
    
    UID_FIELD = []
    TIMESTAMP_FORMAT    = "%Y-%m-%dT%H:%M:%S.%f"
    INDEX_PREFIX        = "es-"
    TEMP_SUFFIX_DAILY   = "%Y.%m.%d"
    TEMP_SUFFIX_WEEKLY  = "%Y.%W"
    TEMP_SUFFIX_MONTHLY = "%Y.%m"
    TEMP_SUFFIX_YEARLY  = "%Y"    
    
    MAPPING_DYNAMIC = "strict"
    
    SEARCH_SIZE = 5000


    def __init__(self, host_config, index, doctype, test, frequency=None, debug=False):
        self._client = elasticsearch.Elasticsearch(host_config)
        self._index = self.INDEX_PREFIX + index
        if test :
            self._index = "test-" + self._index
        else:
            pass
        self._debug     = debug
        self._test      = test
        self._frequency = frequency
        self._doctype   = doctype
        self._indexed   = {}

        
    
    def trace(self, info):
        logger.debug(info)

 
    def info(self):
        self.trace("Elasticsearch server info")
        res = self._client.info()
        self.trace(pprint.pformat(res))    
        return res
        
    
    def ping(self):
        self.trace("Elasticsearch ping")
        res = self._client.ping()
        self.trace(res)
        return res
    
    @classmethod
    def format_ela_datetime(cls, datetimeobj):

        timestamp = datetime.datetime.strftime(datetimeobj, cls.TIMESTAMP_FORMAT)
        timestamp = timestamp[:-3]  # remove micro sec
        timestamp += "+01"          # Paris timezone 
        return timestamp

    @classmethod
    def parse_ela_datetime(cls, stringdate):
        stringdate = stringdate[:-3]
        return datetime.datetime.strptime(stringdate, cls.TIMESTAMP_FORMAT)

    @classmethod
    def timestamp_format(cls, timestamp):
        return datetime.datetime.strptime(timestamp, cls.TIMESTAMP_FORMAT)          

    @classmethod
    def temporal_index(cls, indexname, timestamp, temporalformat):
        timestamp = cls.parse_ela_datetime(timestamp)
        suffix = timestamp.strftime(temporalformat)
        return "{}-{}".format(indexname, suffix) 
        
    def manage_index(self): 
        self.trace("Update template")
        mapping = self.gen_mapping_body()
        body = self.gen_template_body(self._index, mapping, self._test, self._frequency)
        
        if self._debug:
            self.trace(pprint.pformat(body))
        self.put_template(self._index, body)
        if self._frequency:
            pass
        else:
            if self._client.indices.exists(index=self._index):
                self.trace("Index already exist")
                self.put_mapping(mapping)    
            else:
                self.trace("Index creation")
                self.create_index()            

    def create_index(self):
        self.trace("Create Index")
        res = self._client.indices.create(index=self._index)    
        self.trace(pprint.pformat(res))

    @classmethod
    def _gen_uid(cls, *param):
        data = [str(v) for v in param]
        return hashlib.md5("".join(data).encode()).hexdigest() 
    
    @classmethod
    def get_fields(cls):
        body = cls.gen_mapping_body()
        fields = {}
        for k,v in body["properties"].items():
            if k.startswith("@"):
                k = k.strip("@")            
            if "type" in v:
                fields[k] = v["type"]
            elif "properties" in v:
                fields[k] = {kk : vv["type"] for kk,vv in v["properties"].items()}
            else:
                raise ElasticSwarmError("{} : {}".format((k,v)))
        return fields
             
    @classmethod
    def _mapping_body(cls):
        raise NotImplementedError

    @classmethod
    def gen_mapping_body(cls):       
        body = cls._mapping_body()
        body.dynamic = cls.MAPPING_DYNAMIC
        bo = body.to_dict()
        bo["properties"]["@timestamp"] = bo["properties"].pop('timestamp')
        return bo

    @classmethod
    def gen_template_body(cls, index, mapping, test, frequency):       
        body =  Dict()
        if frequency is None:
            body.template = index
        else:
            body.template = "%s-*" % index
        body.settings = {"index.refresh_interval": "5s"}
        dynamic_templates = Dict()
        
        dynamic_templates.string_fields.mapping.omit_norms = True
        dynamic_templates.string_fields.mapping.type = "text"
        dynamic_templates.string_fields.mapping.fields.raw.ignore_above = 256
        dynamic_templates.string_fields.mapping.fields.raw.type = "keyword"
        dynamic_templates.string_fields.match_mapping_type = "string"

        dynamic_templates.string_fields.match   = "*"
        body.mappings["_default_"] = {"dynamic_templates":[dynamic_templates.to_dict()]} 
        body.mappings["_default_"].update(mapping)
            
        return body.to_dict()



    def trace_res(self, msg, res):
        self.trace("{} :".format(msg))
        self.trace("\n".join(["\t{} : {}".format(k, v) for k,v in res.items()]))             
        

    def put_settings(self, body):
        self.trace("Setting")
        self.trace("\t %s" % body)  
        res = self._client.indices.put_settings(index=self._index, body=body)
        self.trace_res("Put Setting", res)
        
        
    def put_template(self, name, body):     
        if self._debug:
            self.trace("Template")
            self.trace("\t {}".format(body))  
        res = self._client.indices.put_template(name=name, body=body)
        self.trace_res("Put template", res)

    
    def put_mapping(self, body):    
        if self._debug:
            self.trace("Mapping")
            self.trace("\t %s" % body)  
        res = self._client.indices.put_mapping(index=self._index, doc_type=self._doctype, body=body)
        if self._debug:
            self.trace_res("Put mapping", res)

        
    def _update(self, body, uid):
        res = self._client.update(index=self._index, doc_type=self._doctype, body=body, id=uid)
        self.trace(pprint.pformat(res))

        
    def index(self, body, uid):
        body = body.to_dict()
        body["@timestamp"] = body.pop('timestamp')         
        self.trace(pprint.pformat(body))
        if self._frequency is None: 
            indexname  = self._index
        else:
            indexname = self.temporal_index(self._index, body["@timestamp"], self._frequency)
         
        res = self._client.index(index=indexname, doc_type=self._doctype, body=body, id=uid)
        
        self.stat_add(indexname, res["_id"])
        self.trace_res("Index status", res)
        return res["_id"]


    @classmethod
    def _type_conv(cls, ttype, value):
        status = True
        if type(value) == type([]): 
            return (status, value)
        if value is None:
            value = None
        elif ttype == "keyword" or ttype == "text":
            value = str(value)
        elif ttype == "boolean":
            value = str(value)
            value = value.lower() in ("yes", "true", "t", "1")
        elif ttype == "float":
            value = float(value)
        elif ttype == "long" or ttype == "integer":
            value = int(value)                
        elif ttype == "date":
            datetimeobj = cls.parse_ela_datetime(value)
            value = cls.format_ela_datetime(datetimeobj)
        else:
            status = False
        return (status, value)

                
    def bulk_index(self, datas):
        bulk_data = []
        if len(datas) == 0:
            self.trace("No data")
            return
        for (body, uid) in datas:
            body = body.to_dict()
            body["@timestamp"] = body.pop('timestamp')         
            if self._frequency is None: 
                indexname  = self._index
            else:
                indexname = self.temporal_index(self._index, body["@timestamp"], self._frequency)
            action = {
                    '_op_type': 'index',
                    "_index": indexname,
                    "_type": self._doctype,
                    "_id": uid,
                    "_source": body
                    }
            bulk_data.append(action)
            
        try:    
            self.trace("Bulk : index={}, doc={}".format(indexname, len(bulk_data)))
            ans = helpers.bulk(self._client, bulk_data)
            self.trace(pprint.pformat(ans))
            
        except:
            self.trace("Bulk error")
            raise                


    def _add_doc(self, data):
        body = Dict()
        for name, ttype in self.get_fields().items():   
            try:
                value = data[name]
            except KeyError:
                value = None
            try:
                status, res = self._type_conv(ttype, value)
            except (TypeError, ValueError) as _ex:
                msg = "Error '{}' type={} value={}".format(name, ttype, value)
                self.trace(msg)
                raise ElasticSwarmError(msg)
            if status:
                value = res
            
            elif ttype == "object":
                pass 
            elif ttype == "nested":
                msg = "nested not supported"
                self.trace(msg)
                raise AssertionError(msg)            
            elif type(ttype) == type([]):
                msg = "list not supported"
                self.trace(msg)
                raise NotImplementedError(msg)
            elif type(ttype) == type({}):
                res = []
                for l in value:
                    d = {}
                    for nname, tttype in ttype.items():
                        v = l[nname]
                        status, v  = self._type_conv(tttype, v)
                        d[nname] = v
                    res.append(d)   
                value = res           
            else:
                msg = "Type not supported {}, {}".format(ttype, name)
                self.trace(msg)
                raise AssertionError(msg)
            body[name] = value
        uid = [data[f] for f in self.UID_FIELD]
        uid = self._gen_uid(*uid)
        return (body, uid)

    def add_doc(self, data):
        (body, uid) = self._add_doc(data)
        return self.index(body, uid)   
    

    def add_docs(self, datas):
        bulk = []
        for data in datas: 
            bulk.append(self._add_doc(data))
        self.bulk_index(bulk)
            
    def get_index_for_search(self):
        if self._frequency is None:
            index = self._index
        else:
            index = self._index + "-*"
        return index 
    

    def stat_add(self, index, _id):
        if index in self._indexed:
            pass
        else:
            self._indexed[index] = []
        self._indexed[index].append(_id)
        
    def stat_get(self):
        return self._indexed
    





class ElasticContainer(ElasticBase):
    INDEX_CONTAINER        = "container"
    DOCTYPE_CONTAINER       = "ec"
    UID_FIELD = ["timestamp", "node_name", "id"]

    def __init__(self, host_config, test=False):               
        super().__init__(host_config, self.INDEX_CONTAINER, self.DOCTYPE_CONTAINER, test, frequency=None)
        
 
    @classmethod
    def _mapping_body(cls):    
        body = Dict()
        body.properties.timestamp.type      = 'date'
        body.properties.timestamp.format    = "date_time" 
        body.properties.node_name.type      = "keyword"
        body.properties.id.type             = "keyword"
        body.properties.short_id.type       = "keyword"
        body.properties.image.type          = "keyword"
        body.properties.short_image.type    = "keyword"
        body.properties.name.type           = "keyword"
        body.properties.status.type         = "keyword"
        body.properties.command.type        = "keyword"      
        body.properties.cpu_percent.type    = "float"
        body.properties.memory_usage.type   = "long"     
        body.properties.cpu_percent.type    = "float"          
        body.properties.fetch_time.type     = "float"
        body.properties.uptime.type         = "float"
        body.properties.image_short_id.type  = "keyword"
        
        body.properties.error.type          = "text"
        
        return body        


    @classmethod    
    def get_fields_input(cls):
        fields =  super().get_fields_input()
        return fields    

    def add_doc(self, data):
        data = dict(data)      
        _repo, name, tag = docker_image_parser(data["image"])
        data["short_image"] = "{}:{}".format(name, tag)        
        data["image_short_id"] = "{}/{}".format(data["short_image"], data["short_id"]) 
        return super().add_doc(data)  


    @staticmethod
    def wrapp_swarm(swarm, timestamp):
        datas = []
        for node_name, value in swarm["status_nodes"].items():
            containers = value["containers"]
            for container_id, container in containers.items():
                data = {}
                data["timestamp"] = ElasticBase.format_ela_datetime(timestamp)                
                data["node_name"] = node_name
                
                if "error" in container:
                    data["error"] = container["error"]
                else:
                    data["id"] = container_id
                    data["short_id"] = container["short_id"]
                    data["image"] = container["image"]
                    data["name"] = container["name"]
                    data["status"] = container["status"]
                    data["command"] = " ".join(container["command"])
                    data["cpu_percent"] = container["cpu_percent"]
                    data["memory_usage"] = container["memory_usage"]
                    data["cpu_percent"] = container["cpu_percent"]
                    data["fetch_time"] = container["fetch_time"]
                    data["uptime"] = container["uptime"]
                    
                datas.append(data)
        return datas


    def add_from_swarm(self, swarm, timestamp):
        datas = self.wrapp_swarm(swarm, timestamp)
        for data in datas:
            self.add_doc(data)
        






class ElasticImages(ElasticBase):
    INDEX_IMAGES         = "images"
    DOCTYPE_IMAGES       = "ei"
    UID_FIELD = ["timestamp", "node_name"]

    def __init__(self, host_config, test=False):               
        super().__init__(host_config, self.INDEX_IMAGES, self.DOCTYPE_IMAGES, test, frequency=None)
                    
    @classmethod
    def _mapping_body(cls):    
        body = Dict()
        body.properties.timestamp.type                              = 'date'
        body.properties.timestamp.format                            = "date_time" 
        body.properties.node_name.fields.raw.type                   = "keyword"
        body.properties.node_name.type                              = "text"
        body.properties.images_count.type                           = "integer"                 
        body.properties.images_size.type                            = "long"        
        body.properties.images.properties.image_id.fields.raw.type  = "keyword"
        body.properties.images.properties.image_id.type             = "text"
        body.properties.images.properties.image_id_short.fields.raw.type  = "keyword"
        body.properties.images.properties.image_id_short.type       = "text"
        body.properties.images.properties.label.fields.raw.type     = "keyword"     
        body.properties.images.properties.label.type                = "text"      
        body.properties.images.properties.size.type                 = "long"       
        body.properties.error.type                                  = "text"
              
        return body        

    @classmethod    
    def get_fields_input(cls):
        fields =  super().get_fields_input()
        return fields    

    def add_doc(self, data):
        data = dict(data)      
        return super().add_doc(data)    

    def add_from_swarm(self, swarm, timestamp):
        datas = self.wrapp_swarm(swarm, timestamp)
        for data in datas:
            self.add_doc(data)
    
    @staticmethod
    def wrapp_swarm(swarm, timestamp):
        datas = []
        for node_name, value in swarm["images_nodes"].items():
            images = value["images"]
            data = {}
            
            data["timestamp"] = ElasticBase.format_ela_datetime(timestamp)
            data["node_name"] = node_name
            
            if "error" in value:
                data["error"] = value["error"]
            else:
                data["images_size"] = value["total_size"]
                data["images_count"] = value["count"]
                di = []
                for image_id, image in images.items():
                    dd = {}
                    dd["image_id"] = image_id
                    dd["image_id_short"] = image["short_id"]
                    dd["label"] = image["RepoTags"][0]
                    dd["size"] = image["Size"]
                    di.append(dd)
                data["images"] = di
                datas.append(data)
        return datas














