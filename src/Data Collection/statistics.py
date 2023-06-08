import sys
from subprocess import call
import os
import pathlib

from tqdm import tqdm

import argparse

current_directory = str(pathlib.Path(__file__).parent.resolve())
result_directory_path = str(pathlib.Path(__file__).parent.resolve()) + '/../../Results/'

parser = argparse.ArgumentParser(prog = 'stats',
    description = 'Helps in gathering stats quickly, by calling main.py',
    allow_abbrev = False)

parser.add_argument('--mode', help = 'Mode = 0 : Fetch\nMode = 1 : ANALYSE\nMode = 2 : CLEAR', default = 0, type = int)
parser.add_argument('--iterations', help = 'Number of fetch iterations', default = 100, type = int)

parser.add_argument('--ns', help = 'Overide ns', type = int)
parser.add_argument('--nb', help = 'Overide nb', type = int)
parser.add_argument('--ne', help = 'Overide ne', type = int)
parser.add_argument('--nrb', help = 'Overide nrb', type = int)
parser.add_argument('--nre', help = 'Overide nre', type = int)
parser.add_argument('--stlim', help = 'Overide stlim', type = int)
parser.add_argument('--alpha', help = 'Overide alpha', type = float)

parser.add_argument('--nc', help = 'Overide nc', type = int)
parser.add_argument('--na', help = 'Overide na', type = int)
parser.add_argument('--m', help = 'Overide m', type = int)
parser.add_argument('--dataset', help = 'Overide dataset', type = int)
parser.add_argument('--pc', help = 'Overide pc', type = float)
parser.add_argument('--pa', help = 'Overide pa', type = float)
parser.add_argument('--r', help = 'Overide r', type = float)
parser.add_argument('--Q', help = 'Overide Q', type = float)
parser.add_argument('--s', help = 'Overide s', type = float)
parser.add_argument('--Tmax', help = 'Overide Tmax', type = float)

parser.add_argument('--n', help = 'Overide n', type = int)

_args = parser.parse_args()

args = ['--{} {}'.format(data[0], data[1]).split() for data in _args._get_kwargs() if data[1] is not None and data[0] != 'mode' and data[0] != 'iterations']
args = [args[i // 2][i % 2] for i in range(2 * len(args))]

FETCH = 0
ANALYSE = 1
CLEAR = 2

FETCH_ITERATIONS = _args.iterations

mode = _args.mode

if mode is FETCH :
    bar = tqdm(range(FETCH_ITERATIONS), desc='Main', initial=0,  file=sys.stdout, leave=False, dynamic_ncols=True, smoothing=0, total=FETCH_ITERATIONS, disable=False, position=1, colour = 'green') 
    for i in bar : 
        call([sys.executable, os.path.join(str(pathlib.Path(__file__).parent.resolve()), '../', 'main.py'), '--log', '--useNFE'] + args)
elif mode is ANALYSE : 
    Values = []
    with open(result_directory_path + 'logs.txt', 'r') as f : 
        while True : 
            line = f.readline()
            if line == '' : 
                break
            val = float(line)
            Values.append(val)
    
    mean = sum(Values) / len(Values)
    rms = (sum(map(lambda x : x * x, Values)) / len(Values)) ** 0.5
    deviation = (rms ** 2 - mean ** 2) ** 0.5
    _min = min(Values)
    _max = max(Values)

    print(mean, rms, deviation, _min, _max)
else :
    with open(result_directory_path + 'logs.txt', 'w') as f : 
        pass
