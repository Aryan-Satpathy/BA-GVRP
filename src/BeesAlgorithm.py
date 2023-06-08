from math import inf
import numpy as np
import random as rnd
import math

## Typing, helps me with intelisense and pylance
from typing import TypeVar
from typing import List, Tuple

from Bee import Bee

## Dataset
import pickle

# For visualization purposes
import cv2 as cv
visualization = False

# Stopping criteria for algo, i.e, ITER or NFE
from typing import Final
ITER : Final[int]   = 0
NFE : Final[int]    = 1

class StandardAlgo : 
    nfe = 0
    def __init__(self, ns : int, nb : int, ne : int, nrb : int, nre : int, stlim : int, ngh : int, alpha : float, problem_statement : dict) : 
        # Algo description
        self.ns     = ns
        self.nb     = nb
        self.ne     = ne
        self.nrb    = nrb
        self.nre    = nre
        self.stlim  = stlim
        self.ngh    = ngh
        self.alpha  = alpha
        
        # Problem description
        self.distance_matrix    = problem_statement['distance_matrix']
        self.nc                 = problem_statement['nc']
        self.na                 = problem_statement['na']
        self.m                  = problem_statement['m']
        self.pc                 = problem_statement['pc']
        self.pa                 = problem_statement['pa']
        self.r                  = problem_statement['r']
        self.Q                  = problem_statement['Q']
        self.s                  = problem_statement['s']
        self.Tmax               = problem_statement['Tmax']
    def check_validity(self, bee) -> Tuple[bool, float, float] : 
        '''
        Checks if the given bee is valid, i.e, it satisfies fuel capacity constraints.
        Returns is_valid : bool, time : float, distance : float
        '''

        StandardAlgo.nfe += 1

        fuel = self.Q
        err = 0
        time = 0.0
        distance = 0
        for i in range(1, len(bee)) : 
            if bee[i - 1] == bee[i] : 
                return False, time, distance
            d = self.distance_matrix[bee[i - 1], bee[i]]
            distance += d
            fuel -= d * self.r
            time += d / self.s
            # if fuel < 0 : 
            #     return False, time, distance
            
            if bee[i] == 0  or bee[i] > self.nc :   # Depot / AFS
                if fuel < 0:
                    err -= fuel
                fuel = self.Q
                time += self.pa
            else :                                  # Customer
                time += self.pc
            
        return True, time, distance + err * 500
    def check_validity_no_cap(self, bee) -> Tuple[bool, float, float] : 
        '''
        Checks if the given bee is valid, i.e, it satisfies fuel capacity constraints.
        Returns is_valid : bool, time : float, distance : float
        '''

        StandardAlgo.nfe += 1

        fuel = self.Q
        err = 0
        time = 0.0
        distance = 0
        for i in range(1, len(bee)) : 
            if bee[i - 1] == bee[i] : 
                return False, time, distance
            d = self.distance_matrix[bee[i - 1], bee[i]]
            distance += d
            fuel -= d * self.r
            time += d / self.s
            if fuel < 0 : 
                return False, time, distance
            
            if bee[i] == 0  or bee[i] > self.nc :   # Depot / AFS
                if fuel < 0:
                    err -= fuel
                fuel = self.Q
                time += self.pa
            else :                                  # Customer
                time += self.pc
            
        return True, time, distance + err * 50
    def solve(self, num_iterations = 100, mode = ITER) -> Bee : 
        iter_counter = 0
        StandardAlgo.nfe = 0

        best_bee = None

        population = []
        try :
            # Get ns scout bees + nb random bees
            # if self.stlim == -1 : 
            #     population = Bee.randomPermutations(self, self.ns, False) + Bee.randomPermutations(self, self.nb, ensure = True) # Bee.randomPermutations(self, self.nb, ensure = True)
            # else :
            #     population = Bee.randomPermsWithGreedyAFS(self, self.ns + self.nb)
            
            population = Bee.randomPermutations(self, self.ns, ensure = False) + Bee.randomPermutations(self, self.nb, ensure = True) # Bee.randomPermutations(self, self.nb, ensure = True)
            
            # if mode is NFE : 
            #     iter_counter += self.ns + self.nb

            # Select best nb bees out of it

            print('Created population')
            population = sorted(population)[ : self.nb]
 
            while iter_counter < num_iterations and (StandardAlgo.nfe < num_iterations or mode is ITER) : 
                iter_counter += 1
                deleted = 0
                for i in range(len(population)) :
                    i -= deleted 
                    bee = population[i]

                    if bee.n_localsearch == self.stlim or bee.shrink_multiplier * self.ngh < 1 : 
                        # Abandon site
                        del(population[i])
                        deleted += 1
                    else :
                        # Local search 
                        local_search_operator = rnd.randint(0, 4 if self.stlim == -1 else 5)

                        local_bees = []
                        if local_search_operator == 0 : 
                            local_bees = bee.swap(self.nre if i < self.ne else self.nrb)
                        elif local_search_operator == 1 : 
                            local_bees = bee.reverse(self.nre if i < self.ne else self.nrb)
                        elif local_search_operator == 2 : 
                            local_bees = bee.insertion(self.nre if i < self.ne else self.nrb)
                        elif local_search_operator == 3 : 
                            local_bees = bee.permuteAFS(self.nre if i < self.ne else self.nrb)
                        elif local_search_operator == 4 :
                            local_bees = bee.removeAFS(self.nre if i < self.ne else self.nrb)
                        else : 
                            local_bees = bee.replaceAFS(self.nre if i < self.ne else self.nrb)
                        
                        # if mode is NFE : 
                        #     iter_counter += self.nre if i < self.ne else self.nrb
                        
                        best_local = bee if len(local_bees) == 0 else min(local_bees)
                        if best_local < bee : 
                            population[i] = best_local
                        else : 
                            # bee.n_localsearch += 1                
                            bee.shrink_multiplier *= 1 if self.stlim == -1 else self.alpha 

                # Send out the scouts
                if self.stlim == -1 : 
                    population += Bee.randomPermutations(self, self.ns + deleted) #  + Bee.randomPermutations(self, deleted, ensure = True)
                else :
                    population += Bee.randomPermsWithGreedyAFS(self, self.ns + deleted)

                # if mode is NFE : 
                #     iter_counter += self.ns + deleted - 1               # 1 is already added at the beginning of the loop

                # Keep the best nb sites
                population = sorted(population)[ : self.nb]
        except KeyboardInterrupt : 
            pass

        best_bee = Bee.empty() if len(population) == 0 else min(population)
        
        return best_bee

class ImprovedAlgov1 (StandardAlgo) : 
    nfe = 0
    def __init__(self, ns: int, nb: int, ne: int, nrb: int, nre: int, stlim : int, T0 : float, ngh: int, alpha: float, problem_statement: dict):
        super().__init__(ns, nb, ne, nrb, nre, stlim, ngh, alpha, problem_statement)
        self.T0 = T0
    def check_validity(self, bee) -> Tuple[bool, float, float] :
        ImprovedAlgov1.nfe += 1
        return super().check_validity(bee)
    def solve(self, num_iterations=100, mode=ITER) -> Bee:
        iter_counter = 0
        ImprovedAlgov1.nfe = 0

        best_bee = None

        population = []
        try :
            # Get ns scout bees + nb random bees
            if self.stlim == -1 : 
                population = Bee.randomPermutations(self, self.ns) + Bee.randomPermutations(self, self.nb, ensure = True)
            else :
                population = Bee.randomPermsWithGreedyAFS(self, self.ns + self.nb)
            # if mode is NFE : 
            #     iter_counter += self.ns + self.nb

            # Select best nb bees out of it
            population = sorted(population)[ : self.nb]
 
            while iter_counter < num_iterations and (ImprovedAlgov1.nfe < num_iterations or mode is ITER) : 
                iter_counter += 1
                deleted = 0
                for i in range(len(population)) :
                    i -= deleted 
                    bee = population[i]

                    if bee.n_localsearch == self.stlim or bee.shrink_multiplier * self.ngh < 1 : 
                        # Abandon site
                        del(population[i])
                        deleted += 1
                    else :
                        # Local search 
                        local_search_operator = rnd.randint(0, 4 if self.stlim == -1 else 5)

                        local_bees = []
                        if local_search_operator == 0 : 
                            local_bees = bee.swap(self.nre if i < self.ne else self.nrb)
                        elif local_search_operator == 1 : 
                            local_bees = bee.reverse(self.nre if i < self.ne else self.nrb)
                        elif local_search_operator == 2 : 
                            local_bees = bee.insertion(self.nre if i < self.ne else self.nrb)
                        elif local_search_operator == 3 : 
                            local_bees = bee.permuteAFS(self.nre if i < self.ne else self.nrb)
                        elif local_search_operator == 4 :
                            local_bees = bee.removeAFS(self.nre if i < self.ne else self.nrb)
                        else : 
                            local_bees = bee.replaceAFS(self.nre if i < self.ne else self.nrb)
                        
                        # if mode is NFE : 
                        #     iter_counter += self.nre if i < self.ne else self.nrb
                        
                        best_local = bee if len(local_bees) == 0 else min(local_bees)
                        if best_local < bee : 
                            population[i] = best_local
                        else : 
                            # Simulated Annealing
                            if self.stlim == -1 :
                                # T = self.T0 / (bee.n_localsearch + 1)
                                # T = self.T0 * (40 - bee.n_localsearch) / 40
                                T = self.T0 / (1 + math.log(bee.n_localsearch + 1))
                            else : 
                                # T = self.T0 * (self.stlim - bee.n_localsearch) / self.stlim
                                T = self.T0 / (1 + math.log(bee.n_localsearch + 1))
                            w = math.exp((bee.value - best_local.value) / T)
                            s = rnd.random()

                            if s < w : 
                                population[i] = best_local
                            else : 
                                # bee.n_localsearch += 1                
                                bee.shrink_multiplier *= 1 if self.stlim == -1 else self.alpha 

                # Send out the scouts
                if self.stlim == -1 : 
                    population += Bee.randomPermutations(self, self.ns + deleted) #  + Bee.randomPermutations(self, deleted, ensure = True)
                else :
                    population += Bee.randomPermsWithGreedyAFS(self, self.ns + deleted)

                # if mode is NFE : 
                #     iter_counter += self.ns + deleted - 1               # 1 is already added at the beginning of the loop

                # Keep the best nb sites
                population = sorted(population)[ : self.nb]
        except KeyboardInterrupt : 
            pass

        best_bee = Bee.empty() if len(population) == 0 else min(population)
        
        return best_bee

class ReducedParamAlgo(StandardAlgo) : 
    nfe = 0
    def __init__(self, ns: int, nre: int, stlim: int, ngh : int, alpha: float, problem_statement: dict):
        super().__init__(ns, 0, 0, 0, nre, stlim, ngh, alpha, problem_statement)
    def check_validity(self, bee) -> Tuple[bool, float, float]:
        return super().check_validity(bee)
    def solve(self, num_iterations=100, mode=ITER) -> Bee:
        iter_counter = 0
        ReducedParamAlgo.nfe = 0

        best_bee = None

        population = []
        try :
            # Get ns scout bees + nb random bees
            if self.stlim == -1 : 
                population = Bee.randomPermutations(self, self.ns, ensure = True)
            else :
                population = Bee.randomPermsWithGreedyAFS(self, self.ns)
            
            # if mode is NFE : 
            #     iter_counter += self.ns + self.nb

            # Select best nb bees out of it
            population = sorted(population) # [ : self.nb]

            w_max = self.nre
            w_min = 1
 
            while iter_counter < num_iterations and (StandardAlgo.nfe < num_iterations or mode is ITER) : 
                iter_counter += 1
                deleted = 0
                for i in range(len(population)) :
                    i -= deleted 
                    bee = population[i]
                    
                    bee.rank_multiplier = (i + 1) / len(population)

                    if bee.n_localsearch == self.stlim or bee.shrink_multiplier * self.ngh * bee.rank_multiplier < 1 : 
                        # Abandon site
                        del(population[i])
                        deleted += 1
                    else :
                        # Local search 
                        local_search_operator = rnd.randint(0, 4 if self.stlim == -1 else 5)

                        num_bees = int(w_max - (w_max - w_min) / len(population) * i)  

                        local_bees = []
                        if local_search_operator == 0 : 
                            local_bees = bee.swap(num_bees)
                        elif local_search_operator == 1 : 
                            local_bees = bee.reverse(num_bees)
                        elif local_search_operator == 2 : 
                            local_bees = bee.insertion(num_bees)
                        elif local_search_operator == 3 : 
                            local_bees = bee.permuteAFS(num_bees)
                        elif local_search_operator == 4 :
                            local_bees = bee.removeAFS(num_bees)
                        else : 
                            local_bees = bee.replaceAFS(num_bees)
                        
                        # if mode is NFE : 
                        #     iter_counter += self.nre if i < self.ne else self.nrb
                        
                        best_local = bee if len(local_bees) == 0 else min(local_bees)
                        if best_local < bee : 
                            best_local.rank_multiplier = (i + 1) / len(population)
                            population[i] = best_local
                        else : 
                            # bee.n_localsearch += 1                
                            bee.shrink_multiplier *= 1 if self.stlim == -1 else self.alpha 

                # Send out the scouts
                if self.stlim == -1 : 
                    population += Bee.randomPermutations(self, self.ns - len(population)) #  + Bee.randomPermutations(self, deleted, ensure = True)
                else :
                    population += Bee.randomPermsWithGreedyAFS(self, self.ns - len(population))

                # if mode is NFE : 
                #     iter_counter += self.ns + deleted - 1               # 1 is already added at the beginning of the loop

                # Keep the best nb sites
                population = sorted(population) # [ : self.nb]
        except KeyboardInterrupt : 
            pass

        best_bee = Bee.empty() if len(population) == 0 else min(population)
        
        return best_bee