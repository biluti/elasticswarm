# -*- coding: UTF-8 -*-



import math
import datetime
import humanize

def human_size(nbytes):
    SUFFIXES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    rank = int((math.log10(nbytes)) / 3)
    rank = min(rank, len(SUFFIXES) - 1)
    human = nbytes / (1024.0 ** rank)
    f = ('{:.2f}'.format(human)).rstrip('0').rstrip('.')
    return '{} {}'.format(f, SUFFIXES[rank])
  

def human_uptime(sec):
    return humanize.naturaltime(datetime.timedelta(seconds=sec))




def docker_image_parser(image_name):
    tag = None
    repo = None
    name = None
    part = image_name.split(":")
    if len(part) == 1:
        name = image_name
    elif len(part) == 2:
        name = part[0]
        tag = part[1]
    elif len(part) == 3:
        port = part[1].split("/")[0]
        repo = part[0] + ":" + port
        name = part[1][len(port)+1:]
        tag = part[2]
    else:
        pass        
    return repo, name, tag




