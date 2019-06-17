""" ******
    cli.py
    ******
    ============================

    A file used for everything related to world, algorithms and files selection from terminal:

    Methods
    -------
        valid_algorithms()
            Shows valid algorithms (genetic and hillclimbing so far) and description

        get_algorithm(alg_selected)
            Returns a strategy based on the selected algorithm
            (alg_selected could be one of the valid algorithms)

        build_maze_filepath(maze)
            It gets the filepath of the choosen .xml file

        algorithms_list()
            Create list of algorithms for the parse_args() method

        parse_args()
            Returns a triad : world (maze), algorithm and ouput file.
            In this way it specifies the specific configuration.
            The output file is used in order to let the agent build a memory and
            to plot the fitness function

        """

#“Code is more often read than written.” --Guido Van Rossum
# author : Simone Azeglio

import argparse
import time
import os

from algorithms.genetic import genetic
from algorithms.algorithm import algorithm
from algorithms.hillclimbing import climber

import heuristics

"""
        

"""

def valid_algorithms():  # dictionary format 'algorithm name': 'algorithm description'
    return {
        "genetic": "genetic algorithm operating on strings of movement heuristics",
        "hillclimb": "hillclimbing algorithm operating on strings of movement heuristics"
    }


def get_algorithm(alg_selected):
    if alg_selected == "genetic":
        return genetic([heuristics.towards_item,  heuristics.random_direction]) #heuristics.away_from_enemy,
    elif alg_selected == "hillclimb" or alg_selected == "hillclimbing":
        return climber([heuristics.towards_item,  heuristics.random_direction]) # heuristics.away_from_enemy,
    else:
        pass

    return None


def build_maze_filepath(maze):
    if not maze.lower().endswith(".xml"):
        maze += ".xml"
    if not maze.lower().startswith("mazes/"):
        maze = "mazes/" + maze

    return maze


def algorithms_list():
    l = "available algorithms:\n"

    valid = valid_algorithms()
    maxNameLength = 0
    for alg in valid:
        if len(alg) + 3 > maxNameLength:  # extra 3 spaces of padding
            maxNameLength = len(alg) + 3

    for alg in valid:
        l += ("  " + alg.ljust(maxNameLength) + valid[alg] + "\n")

    return l


def parse_args():

    parser = argparse.ArgumentParser(
        description="Agent learns to navigate a maze in Minecraft using local search algorithms",
        epilog=algorithms_list(),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("maze", help="specifies the maze XML file")
    parser.add_argument("algorithm", help="specifies the name of the algorithm")

    args = parser.parse_args()
    maze = build_maze_filepath(args.maze)
    alg = get_algorithm(args.algorithm)
    out_file = "/logs/log_" + args.algorithm + "_" + str(time.time()) + ".csv" # /Users/simoneazeglio/MalmoPlatform/Python_Examples/Econofisica/source/
    if not os.path.exists("logs"):
        os.makedirs("logs")

    algorithm.log_file = out_file

    if alg == None:
        print("ERROR: You must specify a valid algorithm.")
        print("Use the --help command to see a list of available algorithms.")

        exit(1)

    return maze, alg, out_file

