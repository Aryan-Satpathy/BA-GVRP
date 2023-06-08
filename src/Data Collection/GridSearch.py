import sys
from subprocess import call, check_output
import os
import pathlib

import csv

current_dir = str(pathlib.Path(__file__).parent.resolve())
result_directory_path = str(pathlib.Path(__file__).parent.resolve()) + '/../../Results/'

MULTIPROCESS = True

def combine (list1 : list, list2 : list) -> list : 
    out = []
    for item1 in list1 : 
        for item2 in list2 : 
            if type(item1) == list : 
                _out = item1 + [item2]
            else :
                _out = [item1, item2]
            out.append(_out)
    return out

parameter_names = ['ns', 'nb'] # , 'nrb'] # , 'stlim', 'alpha']

parameter_space = [
    [5, 10, 20], # ns
    [7, 8, 9, 10, 11], # nb
    ]# [5, 10, 20],
    # ]

combinations = parameter_space[0]

for i in range(1, len(parameter_names)) : 
    combinations = combine(combinations, parameter_space[i])

from tqdm import tqdm

bar = tqdm(range(len(combinations)), desc='Grid Search', initial=0,  file=sys.stdout, leave=True, dynamic_ncols=True, smoothing=0, total=len(combinations), disable=False, position=0, colour = 'green') 

with open(result_directory_path + 'Data.csv', 'w') as f : 
    csv_f = csv.writer(f)

    fields = parameter_names + ['mean', 'rms', 'deviation', 'min', 'max']
    csv_f.writerow(fields)

    if not MULTIPROCESS : 
        call([sys.executable, os.path.join(os.path.dirname(__file__), 'statistics.py'), '--mode', '2'])

    for i in bar : 
        # ns, nb, nrb = tuple(combinations[i])
        ns, nb = tuple(combinations[i])
        nrb = ns // 2 # if ns == 20 else ns
        
        ne = nb // 2
        nre = int(nrb * 1.5)

        if MULTIPROCESS : 
            call([sys.executable, os.path.join(os.path.dirname(__file__), 'statistics_multiprocessing.py'), '--ns', str(ns), '--nb', str(nb), '--ne', str(ne), '--nrb', str(nrb), '--nre', str(nre), '--iterations', '50', '--iD', str(i)])
        else :
            call([sys.executable, os.path.join(os.path.dirname(__file__), 'statistics.py'), '--ns', str(ns), '--nb', str(nb), '--ne', str(ne), '--nrb', str(nrb), '--nre', str(nre), '--iterations', '50'])
        
        if MULTIPROCESS : 
            out = check_output([sys.executable, os.path.join(os.path.dirname(__file__), 'statistics_multiprocessing.py'), '--mode', '1', '--iD', str(i)])
        else :
            out = check_output([sys.executable, os.path.join(os.path.dirname(__file__), 'statistics.py'), '--mode', '1'])
        out = out.decode('utf-8')
        out = out.split()
        mean, rms, deviation, _min, _max = tuple(out)
        csv_f.writerow([ns, nb, nrb, mean, rms, deviation, _min, _max])

        if MULTIPROCESS : 
            call([sys.executable, os.path.join(os.path.dirname(__file__), 'statistics_multiprocessing.py'), '--mode', '2', '--iD', str(i)])
        else :     
            call([sys.executable, os.path.join(os.path.dirname(__file__), 'statistics.py'), '--mode', '2'])