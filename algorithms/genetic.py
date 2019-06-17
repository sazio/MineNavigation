"""
	**********
	genetic.py
	**********
	=============================================



	Pseudocode for the creation of a new population:
	
	fittest = four top scoring strings within the population
	for i in range(population_size):
  		parent1 = random.choice(fittest)
 		parent2 = random.choice(fittest)

  		offspring = parent1[crossover:] + parent2[:crossover]
  		for heuristic in offspring:
    		5% chance to mutate heuristic to another one
  		population.append(offspring)

       
       """

#“Code is more often read than written.” --Guido Van Rossum
# author : Simone Azeglio

import sys
import os

sys.path.append(os.path.dirname(__file__))

import random

from algorithm import algorithm



class genetic(algorithm):
	"""A class used to define the genetic algorithm:

	Attributes
	----------
	set_actions(str)
       		list of possible actions the agent can take

       set_gen_size(int)
       		Size of the generation, each generation is a list of strategies (t = towards the entity, the diamond ; r = random move).
       		Each generation has 8 list strategies in this model

       set_str_len(int)
       		Length of the list, it starts with an average (gaussian distribution) of length 5

       set_sel_frac(double)
       		Sets the selected fraction of the most 4 top high-scoring strings in order to generate strings in the next iteration


       set_mut_prob(double)
       		Mutation probability of the genetic algorithm (p = 0.05)

    Methods
    -------

       next_generation
       		Creates next generation of strategies. It finds the best scores in the population, it selects the top 4 high-scoring strings
       		in order to generate the next generation of strings.

       process_score(score)
       		Keeps track of how the score changes and improves at each iteration

       get_action(obs)
       		Returns an action based on observations and on a policy which considers the previous methods


	"""
	def __init__(self, set_actions, set_gen_size = 8, set_str_len= 5, set_sel_frac = .5, set_mut_prob = .05):
		super(genetic, self).__init__(set_actions)

		self.generation_size = set_gen_size
		self.str_len = set_str_len
		self.selection_fraction = int(set_sel_frac * self.generation_size)
		self.mutation_probability = set_mut_prob

		self.iteration = 0
		self.move = 0

		self.scores = [0] * self.generation_size

		self.population = []
		for i in range(self.generation_size):

			gaussian_len = int(random.gauss(self.str_len, self.str_len / 2.5))
			if gaussian_len < 1:
				gaussian_len = 1

			actions = []
			for j in range(0, gaussian_len):
				actions.append(random.choice(self.possible_actions))

			self.population.append(actions)

	def next_generation(self):
		print ("Creating next generation...")
		new_population = []
		best_scores = []
		fittest = []

		#find the best scores in the population
		for i, s in enumerate(reversed(sorted(self.scores))):
			if i > self.selection_fraction:
				break
			best_scores.append(s)

		#now select every string in the population that has one of the best scores
		for i, p in enumerate(self.population):
			if self.scores[i] in best_scores:
				fittest.append((p, self.scores[i]))

		#now generate the next generation of heuristic function strings
		for i in range(self.generation_size):
			first_parent = random.choice(fittest)[0]
			second_parent = random.choice(fittest)[0]

			crossover = random.random()
			first_crossover = int(crossover * (len(first_parent) - 1))
			second_crossover = int(crossover * (len(second_parent) - 1))

			child = first_parent[:first_crossover] + second_parent[second_crossover:]
			for i, action in enumerate(child): # small chance that the string will mutate
				will_mutate = random.random()
				if will_mutate < self.mutation_probability:
					child[i] = random.choice(self.possible_actions)

			new_population.append(child)

		self.population = new_population
		self.scores = [0] * self.generation_size

		return fittest

	def process_score(self, score):
		self.scores[self.iteration % self.generation_size] = score

		self.iteration += 1
		self.move = 0

		print("Next action string: " + str([f.__name__[0] for f in self.population[self.iteration % self.generation_size]]))

		scores = [(1, score, self.population[self.iteration % self.generation_size])]

		if self.iteration % self.generation_size == 0:
			fittest = self.next_generation()
			scores.extend([(0, s, p) for p, s in fittest])

		return scores


	def get_action(self, obs):
		policy = self.population[self.iteration % self.generation_size]
		action = policy[self.move % len(policy)](obs)

		self.move += 1
		return action


