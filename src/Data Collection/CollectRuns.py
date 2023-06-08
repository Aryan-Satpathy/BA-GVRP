import sys
from subprocess import call, check_output
import os
import pathlib

import multiprocessing as mp

import pickle

def call_worker(args) : 
    # call([sys.executable, os.path.join(os.path.dirname(__file__), 'beesalgoalter.py'), '--log', '--useNFE'] + args)
    out = check_output([sys.executable, os.path.join(os.path.dirname(__file__), 'beesalgoalter.py'), '--useNFE'] + args)
    out = out.decode('utf-8')
    return out

dataset_directory_path = str(pathlib.Path(__file__).parent.resolve()) + '/../../Datasets/'
result_directory_path = str(pathlib.Path(__file__).parent.resolve()) + '/../../Results/'

path = dataset_directory_path + 'Goeke/egoeke_dataset_lc_lr_lrc.pickle'
dest_path = result_directory_path + 'BasicReduced/'

NumberOfRuns = 100

# args = []
args = ['--basic', '--reduced']
# args = ['--improved']

with open(path, 'rb') as f:
    f_reader = pickle.load(f)
    
    for i in range(len(f_reader)):
        dataset = f_reader[i]

        filename = dataset['filename']
        offset_dataset = 3 + i
        args += ['--dataset', str(offset_dataset)]

        pool = mp.Pool(8)
    
        results = []
        for i in range(NumberOfRuns) : 
            results.append(pool.apply_async(call_worker, (args, )))

        pool.close()
        pool.join()

        results = [result.get() for result in results]
        
        # Format : 'Bee(valid = {}, {}, {})".format(self.is_valid, self.path, self.value)'
        results = [result[12 : -2] for result in results]
        results = [result.split(', ')[-1] for result in results]

        with open(dest_path + r'{}.txt'.format(filename), 'w') as f : 
            for result in results :
                f.write(result + '\n')

    exit()