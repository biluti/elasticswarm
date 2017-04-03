elasticswarm
=========

.. image:: https://travis-ci.org/biluti/elasticswarm.svg?branch=master



Run localy :
 run.py swarm:2375 /htmlgen/ '[{"port":9200,"host":"elastic_server","http_auth":["elastic","changeme"]}]'
 
Run in Docker:
 docker run -d -p 80:80 elasticswarm/elasticswarm swarm:2375 '[{"port": 9200, "host": "elastic_server"}]'
 
 