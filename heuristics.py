"""
    *************
    heuristics.py
    *************
    =========================================

    A file used for useful function:


    Methods
    -------
        distance(lhs,rhs)
            Calculate the distance between left-hand-side (lhs) and right-hand-side (rhs). Lhs and rhs could be 
            the agent and the diamond
        
        location(entity)
            Define location as x,y,z triad
             
        dot(lhs,rhs)
            Dot product between left-hand-side (lhs) and right-hand-side (rhs)-
        
        diff(lhs,rhs)
            Coordinate difference between left-hand-side (lhs) and right-hand-side (rhs)
        
        magnitude(vec)
            Magnitude of a vector (vec) 
        
        normalize(vec)
            Normalize a vector (vec) 
        
        get_player_location(el)
            Returns Agent's location 
        
        get_closest_entity(el, entity_name)
            Returns distance from the closest entity 
        
        closest_cardinals(dir, obs)
            Returns closest cardinal, in order to plan the path (dir = direction, obs = observation)
        
        opposite_direction(dir)
            Returns opposite direction given a direction (dir = direction)
        
        random_direction(obs)
            Returns a random direction in order to implement a random strategy (useful in order to don't get stuck)
            (obs = observation)
       
        towards_item(obs)
            Returns the direction to follow in order to get to the item
            (obs = observation)
            
        """

#“Code is more often read than written.” --Guido Van Rossum
# author : Simone Azeglio

import random
import math


# utility functions

def distance(lhs, rhs):
    s = 0
    for i in range(len(lhs)):
        s += (lhs[i] - rhs[i]) ** 2
    return math.sqrt(s)


def location(entity):
    return entity['x'], entity['y'], entity['z']



def dot(lhs, rhs):
    s = 0
    for i in range(len(lhs)):
        s += lhs[i] * rhs[i]
    return s


def diff(lhs, rhs):
    return tuple([lhs[i] - rhs[i] for i in range(len(lhs))])


def magnitude(vec):
    magn = 0
    for i in range(len(vec)):
        magn += vec[i] * vec[i]
    return math.sqrt(magn)


def normalize(vec):
    m = magnitude(vec)
    return tuple([i / m for i in vec])


def get_player_location(el):
    for e in el:
        if e[u'name'] == u'SimoneBot':
            return location(e)

    return None


def get_closest_entity(el, entity_name):
    playerLoc = get_player_location(el)

    # A random and huge initialization
    closest_distance = 100000
    closest_entity = None

    for e in el:
        d = distance(location(e), playerLoc)
        if e[u'name'] != entity_name or d > closest_distance:
            continue

        closest_distance = d
        closest_entity = e

    if closest_entity == None:
        return None, (None, None, None)

    return closest_entity, diff(location(closest_entity), playerLoc)


def closest_cardinals(dir, obs):
    dir = normalize(dir)
    actions_list = []

    if obs.grid[1] == u'glowstone':
        actions_list.append(('movenorth 1', dot(dir, (0, 0, -1))))
    if obs.grid[3] == u'glowstone':
        actions_list.append(('movewest 1', dot(dir, (-1, 0, 0))))
    if obs.grid[5] == u'glowstone':
        actions_list.append(('moveeast 1', dot(dir, (1, 0, 0))))
    if obs.grid[7] == u'glowstone':
        actions_list.append(('movesouth 1', dot(dir, (0, 0, 1))))

    actions_list.sort(key=lambda d: d[1])
    return [a[0] for a in actions_list]


def opposite_direction(dir):
    if dir == 'movesouth 1':
        return 'movenorth 1'
    elif dir == 'moveeast 1':
        return 'movewest 1'
    elif dir == 'movenorth 1':
        return 'movesouth 1'
    return 'moveeast 1'


# heuristic functions
def random_direction(obs):
    actions_list = []
    if (obs.grid[1] == u'glowstone'):
        actions_list.append('movenorth 1')
    if (obs.grid[3] == u'glowstone'):
        actions_list.append('movewest 1')
    if (obs.grid[5] == u'glowstone'):
        actions_list.append('moveeast 1')
    if (obs.grid[7] == u'glowstone'):
        actions_list.append('movesouth 1')

    if len(actions_list) == 0:
        return "quit"

    a = random.randint(0, len(actions_list) - 1)
    return actions_list[a]


# Items smell -- So enemies and items are distinguishable
def towards_item(obs):
    closest_entity, dir = get_closest_entity(obs.entity_locations, u'diamond')

    if closest_entity == None:
        return random_direction(obs)

    return closest_cardinals(dir, obs)[-1]

5

