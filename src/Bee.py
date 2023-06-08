from math import inf
import numpy as np
import random as rnd
import math

## Typing, helps me with intelisense and pylance
from typing import TypeVar
from typing import List, Tuple
Bee = TypeVar('Bee')

## Dataset
import pickle

# For visualization purposes
import cv2 as cv
visualization = False

# Stopping criteria for algo, i.e, ITER or NFE
from typing import Final
ITER : Final[int]   = 0
NFE : Final[int]    = 1

def distance(x, y) : 
    return math.sqrt((y[0] - x[0]) ** 2 + (y[1] - x[1]) ** 2)

def distance_squared(x, y) : 
    return (y[0] - x[0]) ** 2 + (y[1] - x[1]) ** 2

class Bee : 
    ## Internals
    def __init__(self, algo = None, path = None, value = -inf, time = inf) : 
        self.value = value
        self.path = path
        self.time = time
        self.algo = algo
        self.is_valid = True
        self.n_localsearch = 0
        self.shrink_multiplier = 1
        self.rank_multiplier = 1
    def __str__(self) -> str : 
        return "Bee(valid = {}, {}, {})".format(self.is_valid, self.path, self.value)
    def __repr__(self) -> str:
        return str(self)
    def __gt__(self, other) -> bool :
        return self.value > other.value
    def __lt__(self, other) -> bool :
        return self.value < other.value
    def __ge__(self, other) -> bool :
        return self.value >= other.value
    def __le__(self, other) -> bool :
        return self.value <= other.value
    def __eq__(self, other) -> bool :
        return self.value == other.value
    def __getitem__(self, key) : 
        '''
        Standard list like get item, where a Bee object is return if key is slice, otherwise only the node at the particular index is returned
        '''
        if type(key) is int : 
            return self.path[key]
        else : 
            bee = Bee(algo = self.algo, path = self.path[key])
            bee.evaluate()
            return bee
    def __setitem__(self, key, value) : 
        '''
        If index is provided, value of node at the index is changed.
        If slice is provided, 
        '''
        if type(key) is int :       # Was list
            self.path[key] = value
        else :
            self.path[key] == value if type(value) is list else value.path
        return value
    def __delitem__(self, key) : 
        return self.path.__delitem__(key)
    def __len__(self) : 
        return len(self.path)
    def copy(self) -> Bee : 
        other = Bee(self.algo, self.path if self.path is None else self.path.copy())
        other.is_valid = self.is_valid
        other.value = self.value
        other.time = self.time
        return other
    
    ## Private methods
    def setPath(self, path) : 
        self.path = path
    def evaluate(self) : 
        self.is_valid, self.time, self.value = self.algo.check_validity(self)
        return self.is_valid, self.time, self.value
    def evaluateVal(self) : 
        if self.path == None : 
            return self.value
        self.value = 0
        for i in range(len(self.path) - 1) : 
            self.value += distance(self[i + 1], self[i])
        return self.value
    
    ## Local Search Methods
    def swap(self, n) -> List[Bee] : 
        '''
        Returns n bees where 2 nodes are swapped in path
        eg. if bee(self) is [6, 4, 5, 3, 0, 2, 1]
        possible return value is [6, 4, 2, 3, 0, 5, 1]
        '''
        bees = []
        max_size = min(int(self.algo.ngh * self.shrink_multiplier * self.rank_multiplier), len(self) - 2)

        for i in range(n) : 
            bee = self.copy()
            a, size = rnd.choice(range(1, len(bee) - 1)), rnd.choice(range(0, max(1, max_size))) 
            b = min(len(bee) - 2, a + size)
            bee[a], bee[b] = bee[b], bee[a]             # Swap
            bee.evaluate()
            if bee.is_valid : 
                bees.append(bee)

        self.n_localsearch += 1
        return bees
    def reverse(self, n) -> List[Bee] : 
        '''
        Returns n bees where the sequence between 2 nodes are reversed in path
        eg. if bee(self) is [6, 4, 5, 3, 0, 2, 1]
        possible return value is [6, 4, 2, 0, 3, 5, 1]
        '''
        bees = []
        max_size = min(int(self.algo.ngh * self.shrink_multiplier * self.rank_multiplier), len(self) - 2)

        for i in range(n) : 
            bee = self.copy()
            # a, b = rnd.choice(range(1, len(bee) - 1)), rnd.choice(range(1, len(bee) - 1)) 
            # a, b = min(a, b), max(a, b)
            a, size = rnd.choice(range(1, len(bee) - 1)), rnd.choice(range(0, max(1, max_size))) 
            b = min(len(bee) - 2, a + size)
            bee.path[a : b + 1] = bee.path[b : a - 1 : - 1]       # Reverse
            bee.evaluate()
            if bee.is_valid : 
                bees.append(bee)

        self.n_localsearch += 1
        return bees
    def insertion(self, n) -> List[Bee] :
        '''
        Returns n bees where node at some index in path is inserted elsewhere in the path
        eg. if bee(self) is [6, 4, 5, 3, 0, 2, 1]
        possible return value is [6, 4, 2, 5, 3, 0, 1]
        '''
        bees = []
        max_size = min(int(self.algo.ngh * self.shrink_multiplier * self.rank_multiplier), len(self) - 2)

        for i in range(n) : 
            bee = self.copy()
            # a, b = rnd.choice(range(1, len(bee) - 1)), rnd.choice(range(1, len(bee) - 1))
            a, size = rnd.choice(range(1, len(bee) - 1)), rnd.choice(range(0, max(1, max_size))) 
            b = min(len(bee) - 2, a + size)
            if size == 0 : # a == b : 
                bees.append(bee)
                continue
            bee.path.insert(b, bee.path.pop(a))         # Insert
            bee.evaluate()
            if bee.is_valid : 
                bees.append(bee)

        self.n_localsearch += 1
        return bees
    def permuteAFS(self, n) -> List[Bee] : 
        '''
        Returns n bees where the AFS nodes and depo visits only are permuted.
        eg. if bee(self) is [6, 3, 5, 0, 1, 2, 4] and number of customer nodes = 3
        So one possible return value could be [4, 3, 6, 0, 1, 2, 5].
        '''
        AFSstart = self.algo.nc + 1
        bees = []
        
        for i in range(n) : 
            bee = self.copy()
            AFSlist = [j for j in range(len(bee)) if (bee[j] >= AFSstart or bee[j] == 0) and j != 0 and j != len(bee) - 1]
            # for j in range(len(bee)) :
            #     node = bee[j]
            #     if node >= AFSstart :                   # node indices >= AFSstart are AFS
            #         AFSlist.append(j)
            if len(AFSlist) == 0:
                continue
            a = rnd.randint(0, len(AFSlist) - 1)
            AFSlist = AFSlist[a : a + int(self.algo.na / (self.algo.na + self.algo.nc + 1) * self.algo.ngh * self.shrink_multiplier * self.rank_multiplier)]
            _AFSlist = rnd.sample(AFSlist, len(AFSlist))
            _AFSlist = [bee[i] for i in _AFSlist]
            for j in range(len(AFSlist)) : 
                bee[AFSlist[j]] = _AFSlist[j]
            bee.evaluate()
            if bee.is_valid :
                bees.append(bee)

        self.n_localsearch += 1
        return bees
    def removeAFS(self, n) -> List[Bee] :
        '''
        Returns n bees where the AFS nodes and depo visits only are randomly removed.
        eg. if bee(self) is [6, 3, 5, 0, 1, 2, 4] and number of customer nodes = 3
        So one possible return value could be [6, 3, 0, 1, 2].
        '''
        AFSstart = self.algo.nc + 1
        bees = []
        
        for i in range(n) : 
            bee = self.copy()
            AFSlist = [j for j in range(len(bee)) if (bee[j] >= AFSstart or bee[j] == 0) and j != 0 and j != len(bee) - 1]

            if len(AFSlist) == 0: 
                continue

            a = rnd.randint(0, len(AFSlist) - 1)
            AFSlist = AFSlist[a : a + int(self.algo.na / (self.algo.na + self.algo.nc + 1) * self.algo.ngh * self.shrink_multiplier * self.rank_multiplier)]
            
            deleted = 0
            for i in range(len(AFSlist)) : 
                choice = rnd.random() > 0.5
                if choice : 
                    del bee.path[AFSlist[i] - deleted]
                    deleted += 1
            bee.evaluate()
            if bee.is_valid : 
                bees.append(bee)
        
        self.n_localsearch += 1
        return bees
    def replaceAFS(self, n) -> List[Bee] :
        '''
        Returns n bees where the AFS nodes and depo visits only are randomly replaced by another AFS or depot.
        eg. if bee(self) is [6, 3, 5, 0, 1, 2, 4] and number of customer nodes = 3
        So one possible return value could be [6, 3, 6, 0, 1, 2, 0].
        '''
        AFSstart = self.algo.nc + 1
        bees = []

        for i in range(n) : 
            bee = self.copy()
            AFSlist = [j for j in range(len(bee)) if (bee[j] >= AFSstart or bee[j] == 0) and j != 0 and j != len(bee) - 1]

            if len(AFSlist) == 0:
                continue

            a = rnd.randint(0, len(AFSlist) - 1)
            AFSlist = AFSlist[a : a + int(self.algo.na / (self.algo.na + self.algo.nc + 1) * self.algo.ngh * self.shrink_multiplier)]
            
            for j in range(len(AFSlist)) : 
                bee[AFSlist[j]] = rnd.choice([0] + list(range(AFSstart, AFSstart + self.algo.na)))
            
            bee.evaluate()
            if bee.is_valid : 
                bees.append(bee)

        self.n_localsearch += 1
        return bees

    ## Global Search
    @staticmethod
    def randomPermutations(algo, n, ensure = False) -> List[Bee] : 
        '''
        Returns n bees with random permutations and random AFS insertions.
        ensure = True ensures that n valid bees are returned, no matter the wait time
        '''
        AFSstart = algo.nc + 1
        AFSend = algo.nc + algo.na
        bees = []

        count = 0
        # _n = 0              # Debug param, remove it
        while count != n : 
            # _n += 1         # Debug param, remove it
            # print(count)
            path_without_afs = [0] + rnd.sample(range(1, AFSstart), AFSstart - 1)
            random_depot_insertions = rnd.sample(range(1, AFSstart - 1), rnd.randint(0, algo.m - 1))
            random_afs_insertions = rnd.sample([_ for _ in range(1, AFSstart) if _ not in random_depot_insertions], rnd.randint(0, AFSstart - len(random_depot_insertions) - 1))

            path = []
            for j in range(AFSstart) : 
                path += [path_without_afs[j]]
                if j in random_depot_insertions : 
                    path += [0]
                    random_depot_insertions.remove(j)
                else : 
                    while j in random_afs_insertions  : 
                        path += [rnd.randint(AFSstart, AFSend)]
                        random_afs_insertions.remove(j)                 
            path += [0]                                 # path ends at depot

            bee = Bee(algo = algo, path = path)
            bee.evaluate()
            if bee.is_valid :
                count += 1 
                bees.append(bee)
            else : 
                count += 0 if ensure else 1

        # print(_n)
        return bees
    def randomPermsWithGreedyAFS(algo, n) -> List[Bee] : 
        AFSstart = algo.nc + 1
        AFSend = algo.nc + algo.na
        bees = []

        for _ in range(n) : 
            algo.nfe += 1
            path_without_afs = [0] + rnd.sample(range(1, AFSstart), AFSstart - 1) + [0]
            d = 0
            val = 0
            time = 0
            
            i = 0
            num_afs = 0
            while i < algo.nc + 1 + num_afs : 
                current_d = algo.distance_matrix[path_without_afs[i], path_without_afs[i + 1]]

                if d + current_d > algo.Q / algo.r:
                    if d == 0:
                        time += algo.pc
                        val += current_d
                        time += current_d / algo.s
                        i += 1
                        continue  

                    closest_AFS = min(list(range(AFSstart, AFSend + 1)) + [0], key = lambda x : algo.distance_matrix[path_without_afs[i], x])
                    current_d = algo.distance_matrix[path_without_afs[i], closest_AFS]
                    d = 0
                    num_afs += 1
                    path_without_afs.insert(i + 1, closest_AFS)
                    time += algo.p
                else:
                    time += algo.pc
                
                val += current_d
                time += current_d / algo.s
                i += 1

                # print(i)
                # _d = algo.distance_matrix[path_without_afs[i], path_without_afs[i + 1]]
                # d += _d
                # if d == 0:
                #     time += algo.pc
                #     val += _d
                #     time += _d / algo.s
                #     i += 1
                #     continue
                # if d > algo.Q / algo.r : 
                #     closest_AFS = min(list(range(AFSstart, AFSend + 1)) + [0], key = lambda x : algo.distance_matrix[path_without_afs[i], x])
                #     _d = algo.distance_matrix[path_without_afs[i], closest_AFS]
                #     d = 0
                #     num_afs += 1
                #     path_without_afs.insert(i + 1, closest_AFS)
                #     time += algo.pa
                # else : 
                #     time += algo.pc
                # val += _d
                # time += _d / algo.s
                # i += 1
            
            bee = Bee(algo, path=path_without_afs)
            bee.evaluate()
            bees.append(bee)
        
        return bees

    ## Static methods
    @staticmethod
    def empty() : 
        return Bee(None, [], 0)