from math import inf
import numpy as np
import random as rnd
import math
import pathlib

## Typing, helps me with intelisense and pylance
from typing import TypeVar
from typing import List, Tuple

from Bee import Bee, distance, distance_squared
from BeesAlgorithm import StandardAlgo, ImprovedAlgov1, ReducedParamAlgo

## Dataset
import pickle

# For visualization purposes
import cv2 as cv
visualization = False

# Stopping criteria for algo, i.e, ITER or NFE
from typing import Final
ITER : Final[int]   = 0
NFE : Final[int]    = 1


'''
Problem description : 
Distance matrix : dt
number Of Customers : nc
number Of AFS : na

Convention : Nodes : {depot, customers, afs nodes}

number Of Vehicles : m

                    |   pc : if node is customer node
Serving time :      |
                    |   pa : if node is depot or AFS

Rate : r (in gallons / mile)

Fuel capacity : Q (gallons)

Speed : s (miles / hr)

Max time : Tmax (hrs)
'''

'''
Global : Random permutions of nodes + random afs insertion      |
Local :                                                         |   At everypoint
1. afs -> permute                                               |   check feasibility
2. nodes -> standard local search of vrp                        |
'''

Dataset = [
    [
        (140, 90),
        
        (100, 100),
        (120, 110),
        (80, 180),
        (140, 180),
        (20, 160),
        (100, 160),
        (200, 10),
        (140, 140),
        (40, 120),
        (100, 120),
        (180, 100),
        (60, 80),
        (180, 60),
        (20, 40),
        (100, 40),
        (200, 40),
        (20, 20),
        (150, 150),
        (16, 20),

        (42, 160),
        (12, 20),
        (120, 200),
        (50, 50),
        (40, 60),
        (140, 110),
        (110, 40),
        (60, 160),
        (190, 10),
        (180, 150)
    ],
    [
        (135, 70),
        
        (100, 100),
        (120, 110),
        (80, 180),
        (140, 180),
        (20, 160),
        (100, 160),
        (200, 10),
        (140, 140),
        (40, 120),
        (100, 120),
        (180, 100),
        (60, 80),
        (180, 60),
        (20, 40),
        (100, 40),
        (200, 40),
        (20, 20),
        (150, 150),
        (16, 20),

        (42, 160),
        (12, 20),
        (120, 200),
        (50, 50),
        (40, 60),
        (140, 110),
        (110, 40),
        (60, 160),
        (190, 10),
        (180, 150)
    ],
    [
        (15, 70),
        
        (100, 100),
        (120, 110),
        (80, 180),
        (140, 180),
        (20, 160),
        (100, 160),
        (200, 10),
        (140, 140),
        (40, 120),
        (100, 120),
        (180, 100),
        (60, 80),
        (180, 60),
        (20, 40),
        (100, 40),
        (200, 40),
        (20, 20),
        (150, 150),
        (16, 20),

        (42, 160),
        (12, 20),
        (120, 200),
        (50, 50),
        (40, 60),
        (140, 110),
        (110, 40),
        (60, 160),
        (190, 10),
        (180, 150)
    ]
]

Helper = [
    [19, 10],
    [19, 10],
    [19, 10],
]

if __name__ == '__main__' : 
    import argparse

    parser = argparse.ArgumentParser(prog = 'gvrp_bees_algorithm',
    description = 'Solves the GVRP problem using bees algorithm',
    allow_abbrev = False)

    parser.add_argument('--ns', help = 'Number of scout bees to be used in the algorithm', default = 10, type = int)
    parser.add_argument('--nb', help = 'Number of best sites to be used in the algorithm', default = 9, type = int)
    parser.add_argument('--ne', help = 'Number of elite sites to be used in the algorithm', default = 5, type = int)
    parser.add_argument('--nrb', help = 'Number of bees in nb sites to be used in the algorithm', default = 10, type = int)
    parser.add_argument('--nre', help = 'Number of bees in ne sites to be used in the algorithm', default = 15, type = int)
    parser.add_argument('--stlim', help = 'Number of iterations before site abandonment, -1 for no site abandonment', default = 27, type = int)
    parser.add_argument('--alpha', help = 'Shrinking factor to be used in the algorithm', default = 0.9025, type = float)
    parser.add_argument('--T0', help = 'Initial Temperature in the improved algorithm', default = 1500, type = float)

    parser.add_argument('--nc', help = 'Number of customer nodes in the problem', default = 19, type = int)
    parser.add_argument('--na', help = 'Number of filling stations in the problem', default = 10, type = int)
    parser.add_argument('--m', help = 'Number of vehicles in the problem', default = 1, type = int)
    parser.add_argument('--dataset', help = 'ID of dataset to be used (which is already implemented in the code), -1 for random points', default = 0, type = int)
    parser.add_argument('--pc', help = 'Serving time of customer nodes in the problem', default = 15 / 60, type = float)
    parser.add_argument('--pa', help = 'Serving time of filling stations in the problem', default = 15 / 60, type = float)
    parser.add_argument('--r', help = 'Rate of fuel usage(unit / mile) in the problem', default = 0.2, type = float)
    parser.add_argument('--Q', help = 'Maximum fuel storage(unit) in the problem', default = 60, type = float)
    parser.add_argument('--s', help = 'Speed of vehicle(miles / hr) in the problem', default = 40, type = float)
    parser.add_argument('--Tmax', help = 'Maximum time of travel(hr) in the problem', default = 1000, type = float)

    parser.add_argument('--gui', help = 'Show the final path predicted by the algorithm', action = 'store_true')
    parser.add_argument('--useNFE', help = 'Whether to use NFE as stopping criteria or iterations', action = 'store_true')
    parser.add_argument('--n', help = 'Number of iterations / NFE to use', default = 60000, type = int)
    parser.add_argument('--log', help = 'Whether to write to logs', action = 'store_true')
    parser.add_argument('--basic', help = 'Whether to use Basic BA or standard', action = 'store_true')
    parser.add_argument('--improved', help = 'Whether to use improved BA or standard', action = 'store_true')
    parser.add_argument('--reduced', help = 'Whether to use 2 Parameter BA or Standard', action = 'store_true')

    parser = parser.parse_args()

    if parser.basic : 
        parser.stlim = -1

    Boundary = (250, 250)                         # (170, 170)
    
    points = []
    if parser.dataset == -1 :
        # Random points genertation
        minDst = 5
        for i in range(parser.nc + parser.na + 1) : 
            while True  : 
                x, y = rnd.randrange(0, Boundary[0]), rnd.randrange(0, Boundary[1])

                if len(points) == 0 or min(map(lambda _ : distance_squared(_, (x, y)), points)) > minDst ** 2 : 
                    break
            points.append((x, y))
    else : 
        if parser.dataset > 2 : 

            dataset_directory_path = str(pathlib.Path(__file__).parent.resolve()) + '/../Datasets/'
            ## For Erdogan
            # with open(dataset_directory_path + 'erdogan/erdogan_dataset.pickle', 'rb') as f :
            
            ## For Goeke
            with open(dataset_directory_path + 'Goeke/egoeke_dataset_lc_lr_lrc.pickle', 'rb') as f : 
                # print('Doing Goeke Lessgo')
                
                f_reader = pickle.load(f)

                f_reader = f_reader[parser.dataset - 3]
                points = f_reader['dataset']

                parser.nc = f_reader['customers']
                parser.na = f_reader['afs']

                parser.r = 1
                parser.Q = f_reader['battery capacity']
        else : 
            points = Dataset[parser.dataset]

            parser.nc = Helper[parser.dataset][0]
            parser.na = Helper[parser.dataset][1]

    print(parser.nc, parser.na)
    
    # Distance Matrix generation
    dt = np.zeros((parser.nc + parser.na + 1, parser.nc + parser.na + 1), dtype = float)
    for i in range(parser.nc + parser.na + 1) : 
        dt[i, i] = 0
        for j in range(i + 1, parser.nc + parser.na + 1) : 
            dt[i, j] = distance(points[i], points[j])
        for j in range(0, i) : 
            dt[i, j] = dt[j, i]
    
    problem_description = { 'distance_matrix' : dt,
                            'nc' : parser.nc,
                            'na' : parser.na,
                            'm' : parser.m,
                            'pc' : parser.pc,
                            'pa' : parser.pa,
                            'r' : parser.r,
                            'Q' : parser.Q,
                            's' : parser.s,
                            'Tmax' : parser.Tmax}
    
    if parser.improved : 
        algo = ImprovedAlgov1(parser.ns,
        parser.nb,
        parser.ne,
        parser.nrb,
        parser.nre,
        parser.stlim,
        parser.T0,
        parser.nc + parser.na + 1,
        parser.alpha,
        problem_description)
    elif parser.reduced :
        algo = ReducedParamAlgo(parser.ns,
        parser.nre,
        parser.stlim,
        parser.nc + parser.na + 1,
        parser.alpha,
        problem_description
        )
    else : 
        print('Using standard')
        algo = StandardAlgo(parser.ns,
        parser.nb,
        parser.ne,
        parser.nrb,
        parser.nre,
        parser.stlim,
        parser.nc + parser.na + 1,
        parser.alpha,
        problem_description)
    best_bee = algo.solve(parser.n, mode = NFE if parser.useNFE else ITER)

    if parser.log : 
        result_directory_path = str(pathlib.Path(__file__).parent.resolve()) + '/../Results/'
            
        with open(result_directory_path + 'logs.txt', 'a') as f: 
            f.write(str(best_bee.value) + '\n')
    else :
        print(best_bee)

    if parser.gui : 
        resolution = (900, 1500)
        multiplier = min(resolution[0] / Boundary[0], resolution[1] / Boundary[1])

        _points = []
        for point in points : 
            _point = int(point[1] * multiplier), int(point[0] * multiplier)
            _points.append(_point)
        
        im = np.zeros((resolution[0], resolution[1], 3), np.uint8)

        size = cv.getTextSize("GV Range / 2", cv.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]

        cv.putText(im, "GV Range / 2", (resolution[1] - 20 - size[0], 40 + int(multiplier * parser.Q / 5 / parser.r / 4 + size[1] / 2)), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 50, 200), lineType = cv.LINE_AA, bottomLeftOrigin=False)
        cv.line(im, (resolution[1] - 40 - size[0], 40), (resolution[1] - 40 - size[0], 40 + int(multiplier * parser.Q / 5 / parser.r / 2)), (255, 50, 200), thickness = 1, lineType = cv.LINE_AA)

        for i in range(len(best_bee) - 1) : 
            cv.line(im, _points[best_bee[i]], _points[best_bee[i + 1]], (255, 150, 150), 1, lineType = cv.LINE_AA)
        
        for _point in _points : 
            cv.circle(im, _point, 3, (100, 255, 100), -1, lineType = cv.LINE_AA)
            x_mul, y_mul = 1, 1
            if _point[0] > resolution[1] - 15 : 
                x_mul = -1
            if _point[1] < 15 : 
                y_mul = -2
            cv.putText(im, str(_points.index(_point)), (_point[0] + 7 * x_mul, _point[1] - 7 * y_mul), cv.FONT_HERSHEY_SIMPLEX, 0.6, (150, 255, 150), lineType = cv.LINE_AA)
        
        cv.imshow('Results', im)
        cv.waitKey(0)