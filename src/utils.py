# -*- coding: UTF-8 -*-



import math
import inspect
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
    try:
        return humanize.naturaltime(datetime.timedelta(seconds=sec))
    except OverflowError as ex:
        return "Error {} sec".format(sec)


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


def inspect_traceback(exception):
    CALL_DEPTH = 1
    DEFAULT = dict.fromkeys(["path", "line", "function", "code"], "no info")
    traceback = inspect.trace()
    stack = []
    try :
        for index in range(CALL_DEPTH, len(traceback)):
            stack.append(dict(DEFAULT))
            stack[-1]["path"]      = traceback[index][1]
            stack[-1]["line"]      = traceback[index][2]
            stack[-1]["function"]  = traceback[index][3]
            stack[-1]["code"]      = str(traceback[index][4][0]).strip("\n\r")
    except Exception:
        pass
    des = {}
    des["stack"]            = stack
    des["exception_info"]   = str(exception)
    des["exception_class"]  = exception.__class__.__name__
    return des


def trace_traceback(des):
    dis = "Exception \n"
    for sline in des["stack"] :
        dis += "    File \"%s\", line %d, in %s\n" % (sline["path"], sline["line"], sline["function"])
        dis += "        %s\n" % (sline["code"])
    dis += "    %s\n" % (des["exception_class"])
    dis += "    %s\n" % (des["exception_info"])
    return dis



