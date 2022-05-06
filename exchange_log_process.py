
from exchange_lib import *
import os
def readOriginFile(path='./origin_logs'):
    ls = []
    for f in os.listdir(path): 
        f_name = os.path.join(path, f)
        if '_body' in f_name:
            with open(f_name, 'r') as ff:
                ls.append(ff.read())
    return ls


lp = LogProcess("./logs.npy")
lp.remove()
logs = readOriginFile()[3:]
for log in logs:
    lp.write(item=log, times=3)
lp.save()