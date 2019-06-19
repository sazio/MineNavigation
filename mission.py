# “Code is more often read than written.” --Guido Van Rossum
# author : Simone Azeglio

""" **********
    mission.py
    **********

    ======================================
"""

import MalmoPython
import os
import sys
import time
import json
import random
import math
import heuristics


class mission:
    """A class used for everything related to a mission (a run of the environment):

            Attributes
            ----------

            Methods
            -------
            load(mission_file)
                Load the world from *.xml* file and create default **Malmo** objects

            start()
                Set client pool, client info , reset the world for each new mission, set dimensions
                of the video-window and agent's viewpoint. Attempt to start a mission for 10 times if there's any
                issue occurring (some stochastics errors - take a look at Malmo's official documentation:
                https://github.com/microsoft/malmo ), when the mission starts it keeps counting the time.

            is_running()
                Check if the mission is currently running:
                returns True if mission is running

            get_observation()
                Loads floor grid, edge distances, current player position, and entity (e.g. diamond) position
                in order to let the agent know the distance to the diamond (odor-like representation).
                It also counts collected items and exports the world view in a *.json* file.
                Agent's observation is a *3x3 grid*: he's in the center and he knows only 1 block in every
                possible direction

            send_command()
                Send command input to the Agent in order to perform the next move.
                It even counts if the current cell is a newly explored one or not (this
                will be useful in implementing the score function)

            stop_clock()
                It stops the time at the end of the mission (useful for score function based on time)

            check_errors()
                Check whether there are errors in the mission (check *world_state* Malmo's method). Those errors are typically related to Malmo Client

            block_score()
                The agent has to explore new blocks in order to get a better *fitness*, he gets a penalty by being in the same
                block (no points for fitness)

            time_score()
                The agent gets one fitness point for each seconds he spends alive

            item_score()
                The agent gets some more points for each item he picks up from the ground
                (1 diamond = 50 fitness points)

            score()
                Sums up block_score , time_score and item_score to get the Fitness

    """

    def __init__(self):
        self.missionXML = ""  # XML code -- Setting up the world
        self.agent_host = None
        self.malmo_mission = None
        self.malmo_mission_record = None
        self.world_state = None

        self.number = 0

        self.agent_location = (None, None)
        self.num_items = 0
        self.blocks_traveled = {} # dictionary mapping an (x,z) coordinate to the number of times the agent has been there

        self.start_time = None
        self.end_time = None

    def load(self, mission_file):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w')  # flush print output immediately

        # More interesting generator string: "3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"
        # flat world string 3;7,220*1,5*3,2;3;,biome_1

        with open(mission_file, 'r') as xmlFile:
            self.missionXML = xmlFile.read()


        self.agent_host = MalmoPython.AgentHost()
        try:
            self.agent_host.parse( sys.argv )
        except RuntimeError as e:
            print('ERROR:',e)
            print(self.agent_host.getUsage())
            exit(1)
        if self.agent_host.receivedArgument("help"):
            print(self.agent_host.getUsage())
            exit(0)


    def start(self):

        self.malmo_client_pool = MalmoPython.ClientPool()
        self.malmo_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10001))  # 10000 in use - try 10001

        self.malmo_mission = MalmoPython.MissionSpec(self.missionXML, True)
        self.malmo_mission.forceWorldReset()

        self.malmo_mission_record = MalmoPython.MissionRecordSpec()

        self.malmo_mission.requestVideo(800, 500)
        self.malmo_mission.setViewpoint(1)

        # Attempt to start a mission:
        max_retries = 10
        for retry in range(max_retries):
            try:
                self.agent_host.startMission(self.malmo_mission, self.malmo_mission_record )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:",e)
                    exit(1)
                else:
                    time.sleep(2)

        # Loop until mission starts:
        print("Waiting for the mission to start ")
        self.world_state = self.agent_host.getWorldState()

        while not self.world_state.has_mission_begun:
            sys.stdout.write(".")
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()
            for error in self.world_state.errors:
                print("Error:", error.text)

        print(" ")
        print("Mission running ")

        self.number += 1
        self.start_time = time.time()
        self.end_time = None

    def is_running(self):
        if self.world_state == None:
            return False
        return self.world_state.is_mission_running

    def get_observation(self):

        edges = ["Top", "Right", "Bottom", "Left"]
        while self.world_state.is_mission_running:
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()
            if len(self.world_state.errors) > 0:
                raise AssertionError('Could not load grid.')

            if self.world_state.number_of_observations_since_last_state > 0:
                msg = self.world_state.observations[-1].text
                state = json.loads(msg)

                grid = state.get(u'floorAll', 0)
                # Check in the xml file --> floorAll is a 3x3 grid
                distances = [state.get(u'distanceFrom' + e, 0) for e in edges]
                cell = state.get(u'cell', 0)
                # The agent has a GPS
                el = state.get(u'entityCoordinates', 0)

                self.agent_location = cell
                # He's gonna pick some diamonds - we want to count em all --> every diamond is 50 points
                self.num_items = sum([state.get("Hotbar_" + str(i) + "_size", 0) for i in range(9)])

                #Export Observation data -- to check for Inventory Issues -- might be related to time tho
                with open('symbolicView.txt', 'w') as outfile:
                    json.dump(msg, outfile)

                break

        return observation(grid, distances, cell, el)


    def send_command(self, cmd):

        if self.agent_location not in self.blocks_traveled:
            self.blocks_traveled[self.agent_location] = 0

        self.blocks_traveled[self.agent_location] += 1
        self.agent_host.sendCommand(cmd)


    def stop_clock(self):
        self.end_time = time.time()


    def check_errors(self):
        self.world_state = self.agent_host.getWorldState()
        for error in self.world_state.errors:
            print("Error:", error.text)




    # Kind of experience --> If I discover new blocks I get some money --> The agent has incentives to explore
    def block_score(self):
        score = 0
        for location in self.blocks_traveled:
            score += math.log(self.blocks_traveled[location] + 1, 2)  # diminishing returns for being at the same block

        return score


    def time_score(self):
        if self.start_time == None:
            return 0
        if self.end_time == None:
            self.end_time = time.time()

        """
        # Distance between agent and diamond --> For Ground.xml - silence elseways
        # <DrawItem x="7" y="56" z="-3" type="diamond" />
        #agent_loc = self.agent_location.replace(',', '')
        agent_loc = self.agent_location.replace("(", "")
        agent_loc = agent_loc.replace(")", "")
        #float_list_agent_loc=list(map(float, agent_loc.split(',')))
        #list_agent_loc = list(agent_loc)
        float_list_agent_loc = [float(i) for i in list_agent_loc]
        print("Agent's Location" + float_list_agent_loc)

        diamond_location = [7.0, -3.0]
        dist_ag_diam = heuristics.distance(float_list_agent_loc, diamond_location)

        # Add some function related to diamonds' distance --> Exploring only | Think about Survival mode too
        """


        # Overclocking issue: x 2 because of the overclocking  if we need
        return self.end_time - self.start_time # - dist_ag_diam


    def item_score(self):
        return self.num_items

    def score(self):
        return self.item_score() * 50 + self.time_score() + self.block_score()



class observation:

    """ A class used to represent an observation of the world:

            Attributes
            ----------
            set_grid: str
                Extracted from the *.json* World File by *mission.get_observation()*
                The grid is the part of the world seen by the agent

            set_edge_distances : str
                Extracted from the *.json* World File by *mission.get_observation()*
                Distances from the edges of the world (The world is limited)

            set_cell : str
                Extracted from the *.json* World File by *mission.get_observation()*
                Cell is the agent location in the world (The agent has a GPS)

            set_entity_locations : str
                Extracted from the .json World File by mission.get_observation()
                Locations of entities (e.g. Diamonds, Zombies)


            Methods
            -------
            at_junction()
                States whether a move is plausible or not : The agent can only walk over glowstone.
                This is useful in order to limit the world with another material (e.g. Lava)

    """
    def __init__(self, set_grid, set_edge_distances, set_cell, set_entity_locations):
        self.grid = set_grid
        self.edge_distances = set_edge_distances
        self.agent_cell = set_cell
        self.entity_locations = set_entity_locations

    def at_junction(self):
    #Whether a move is plausible or not

        actions_list = []

        if(self.grid[1] == u'glowstone'):
            actions_list.append('movenorth 1')
        if(self.grid[3] == u'glowstone'):
            actions_list.append('movewest 1')
        if(self.grid[5] == u'glowstone'):
            actions_list.append('moveeast 1')
        if(self.grid[7] == u'glowstone'):
            actions_list.append('movesouth 1')
        if len(actions_list) == 1:
            return True

        return True

