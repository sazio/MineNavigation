"""
	************
	algorithm.py
	************

	=================================================


        """


#“Code is more often read than written.” --Guido Van Rossum
# author : Simone Azeglio

import abc # https://docs.python.org/3/library/abc.html
import argparse
import cli
import time
import os


# Just in case it doesn't work
# class algorithm(object):

class algorithm():
	"""A class used to define an algorithm and its actions:

    Attributes
 	----------

    Methods
    -------
        process_score(score)
        	*@abc.abstractmethod*
        	After specifying the algorithm, while running the program, it processes
        	the score by following the current algorithm rule (*genetic, hillclimb*)

        set_score(score)
        	When each run of a mission is ended it sets the score and it saves the score in a
        	*.csv* file (useful for plotting the fitness function)

        get_action(obs)
        	*@abc.abstractmethod*
        	It gets the action that the agent has to perform from the specific algorithm (*genetic, hillclimb*)

	"""
	log_file = "" # static field, set in cli --> smth wrong with this

	def __init__(self, set_actions):
		self.possible_actions = set_actions

	@abc.abstractmethod
	def process_score(self, score):
		raise NotImplementedError


	def set_score(self, score):
		log_lines = self.process_score(score)

		########
		## Having some issues here, not sure to implement an @abc method in cli.py
		## Parse Args from cli.py --> Some issues ... Need to figure out how to solve them

		parser = argparse.ArgumentParser(
			description="Agent learns to navigate a maze in Minecraft using local search algorithms",
			epilog=cli.algorithms_list(),
			formatter_class=argparse.RawTextHelpFormatter
		)

		parser.add_argument("maze", help="specifies the maze XML file")
		parser.add_argument("algorithm", help="specifies the name of the algorithm")

		args = parser.parse_args()
		maze = cli.build_maze_filepath(args.maze)
		alg = cli.get_algorithm(args.algorithm)
		out_file = "/Users/simoneazeglio/MalmoPlatform/Python_Examples/Econofisica/Project/logs/log_" + args.algorithm + "_" + ".csv"
			# + str(time.time()) + ".csv"  #
		if not os.path.exists("logs"):
			os.makedirs("logs")

		algorithm.log_file = out_file

		########

		with open(algorithm.log_file, "a+") as log:
			for logging_level, sc, st in log_lines:
				h_str = str([h.__name__[0] for h in st]).replace(',', '')
				log.write(str(logging_level) + "," + h_str + "," + str(sc) + "\n")

	@abc.abstractmethod
	def get_action(self, obs):
		raise NotImplementedError