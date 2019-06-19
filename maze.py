"""		*******
		maze.py
		*******

		====================================

		**Main file** - it runs the mission
		
		Basically, after loading the world (*.xml* file) it starts with two concatenated while statements (formally the mission is a concatenated while statement).
		The second one represents each run. In the end it calculates the score and it saves a *.csv* file (log file) by setting the selected algorithm's score.
		We used *time.sleep(2)* in order to avoid issues related to items counting (stochastics fluctuations in time are significant and most of the times the set_score
		function wouldn't work because of that, compromising the learning process) 

"""

#“Code is more often read than written.” --Guido Van Rossum
# author : Simone Azeglio


import MalmoPython
import time

from cli import parse_args
from mission import mission

if __name__ == "__main__":
	mazeXMLFile, alg, out = parse_args()

	m = mission()
	m.load(mazeXMLFile)



	while True:
		m.start()
		# initialize action
		action = ''
		# Loop until mission ends:
		try:
			while m.is_running():
				time.sleep(0.1)
				# get observation --> return what the agent can see
				observations = m.get_observation()

				if action == '' or observations.at_junction(): #Decide a new move
					action = alg.get_action(observations)

				m.send_command(action)
				m.check_errors()

				time.sleep(0.5)

		except Exception as e:
			m.send_command("quit")
			m.stop_clock()
			m.check_errors()

		m.stop_clock()
		score = m.score()

		print("\nMission ended with score: " + str(score))
		alg.set_score(score)

		time.sleep(2)
		# Let's see if I'm correct --> is it an issue related to "how long it takes" to compute the score and to clean the inventory?
		# And some stochasticity related to that ? --> If so , time.sleep() should work
		# Let's wait a little before clearing the inventory

		######################################
		#   IT WORKSSSS with time.sleep(2)   #
		######################################

		m.send_command("chat /clear")
		m.send_command("chat /kill @e[type=Player]")

	# Mission has ended.
