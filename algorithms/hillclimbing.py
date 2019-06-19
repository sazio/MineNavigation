# “Code is more often read than written.” --Guido Van Rossum
#  author : Simone Azeglio


""" ***************
    hillclimbing.py
    ***************
    ==================================================

    After scoring the first string, the algorithm runs a mission for each string adjacent to the first string in the search space.
    An adjacent string is a string which differs by only one addition of a heuristic from the string, removal of a heuristic, or change of a heuristic.
    After scoring every adjacent string, the algorithm chooses the string with the best score. It then explores the adjacent strings to that string,
    choosing the best one of those, and so on. These incremental improvements allow the algorithm to find heuristic strings that produce higher and higher scores.

    Added *Simulated Annealing* feature!
    The purpose of this probabilistic behavior is to maximize the space that the hill-climbing algorithm explores.
    Rather than sticking with whatever seems locally optimal,  the hill-climbing algorithm may find even better strings
    in areas of the search space that, at first glance, seemed sub-optimal.

    **Pseudocode for hillclimbing:**

        *while True:*
            *for string adjacent to current_string:*
                *if score(string) > score(current_string):*
                    *best_string = string*

            *current_string = best_string*


    **Pseudocode for Simulated Annealing:**

        *while True:*
            *prob = probability that we choose a suboptimal choice*

            *eps = random.random()*

            *cooling_rate = 0.5*

            *neighbors = every string adjacent to current_string*

            *if eps < p:*
                *string = random.choice(neighbors)*
            *else:*
                *for string adjacent to current_string:*
                    *if score(string) > score(current_string):*
                         *best_string = string*

                *current_string = best_string*

                *prob \*= cooling_rate*

"""


import random

from algorithm import algorithm

class climber(algorithm):
    """A class used to define the hillclimbing algorithm:


    Attributes
    ----------

        set_actions(str)
            List of possible actions the agent can take

        init_eps(double)
            Minimum reduction in the function before termination (Simulated Annealing - https://www.aero.iitb.ac.in/~rkpant/webpages/DefaultWebApp/salect.pdf)

        set_cooling(double)
            Cooling rate (Simulated Annealing - https://www.aero.iitb.ac.in/~rkpant/webpages/DefaultWebApp/salect.pdf)


    Methods
    -------

        generate_local_space()
            Starting from a string it performs the three possible operations on heuristics creating a local search space.
            After that it starts the Simulated Annealing algorithm

        pick_next_string()
            It selects the next string, starting from the best score string and looking around that one in the search space

        process_score(score)
            Keeps track of how the score changes for ending in the same block. It returns a combination of score and
            current string heuristics

        get_action(obs)
            Returns action based on heuristics string (which is based on observations)



    """
    def __init__(self, set_actions, init_eps=0.0, set_cooling=1.0):#, init_str=[]):
        super(climber, self).__init__(set_actions)

        self.h_str = [random.choice(set_actions)]
        self.possible_actions = set_actions

        self.eps = init_eps
        self.cooling_rate = set_cooling

        self.local_space = self.generate_local_space()

        self.neighbor_scores = []
        self.move = 0
        self.space_index = 0

        self.anneal = False

    def generate_local_space(self):

        space = [self.h_str]

        for i in range(0, len(self.h_str)):  # add all remove changes
            r = list(self.h_str)
            del r[i]
            if len(r) > 0:
                space.append(r)

        for i in range(0, len(self.h_str)):  # add all mutate changes
            for h in self.possible_actions:
                if self.h_str[i] != h:
                    m = list(self.h_str)
                    m[i] = h
                    space.append(m)

        for i in range(0, len(self.h_str) + 1):  # add all insertion changes
            for h in self.possible_actions:
                a = list(self.h_str)
                a.insert(i, h)
                space.append(a)

        space = [list(x) for x in set(tuple(x) for x in space)]
        random.shuffle(space)

        # roll for annealing here
        r = random.random()
        if (r < self.eps):
            self.anneal = True

        # temperature schedule update
        self.eps *= self.cooling_rate

        return space

    def pick_next_string(self):

        self.space_index = 0

        best_score = 0
        best_neighbor = None  # find the neighbor with the best score, then start looking from there

        for i, s in enumerate(self.neighbor_scores):
            if s > best_score:
                best_score = s
                best_neighbor = self.local_space[i]

        print("Best neighbor's score: " + str(best_score))

        self.h_str = best_neighbor
        self.neighbor_scores = []

        self.local_space = self.generate_local_space()

        return best_score

    def process_score(self, score):

        print("String: " + str([h.__name__[0] for h in self.local_space[self.space_index]]))

        current_str = self.local_space[self.space_index]

        self.neighbor_scores.append(score)
        self.space_index += 1
        self.move = 0

        if (self.anneal == True):
            self.anneal = False
            self.pick_next_string()
            return [(0, score, current_str)]
        elif self.space_index >= len(self.local_space):  # if we have searched all neighbors
            best_score = self.pick_next_string()
            return [(1, score, current_str), (0, best_score, self.h_str)]

        return [(1, score, current_str)]

    def get_action(self, obs):
        curr_str = self.local_space[self.space_index]
        a = curr_str[self.move % len(curr_str)]

        self.move += 1
        return a(obs)
