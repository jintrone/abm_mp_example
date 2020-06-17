"""
Code here is the scaffolding for a basic agent-based model.  The code is intended to be 'run'
from a script that drives the simulation. The model here introduces a separation of concerns
between the 'environment' (which may be passed in the agent during execution, and maintains
a registry of all agents) and the 'agents' which execute update functions.
"""

import random, time


class Agent:
    """Agents encapsulate the calculations to be run in each update

    This implementation is set up for multi-processing because it allows a caller to
    set the internal state at any point in time via the do_update method
    """

    def __init__(self, env):
        """ Initializes the agent and registers it within the environment

        Args:
            env: The Environment for the simulation
        """

        """ list of int: the ids of this agent's neighbors """
        self.neighbors = []

        self.cur_data = None
        """ int: the data for this round"""

        self.next_data = None
        """ int: the data for the next round """

        self.process_time = 0
        """ int: the amount of time we should sleep for each update; this is only really useful for demo purposes"""

        self.id = env.register(self)
        """ int: this agent's unique id """

    def setup(self, params: dict, env) -> None:
        """ Sets the agent up for the simulation

        Args:
            params: A dictionary of parameters that the agent will use for this simulation
        """

        # Set initial state
        self.cur_data = random.randint(-params["max"], params["max"])

        # This is useful for demo purposes to see the tradeoffs of multiprocessing
        self.process_time = params["process_time"]

        # Set up neighbors - note that all agents must be initialized before this call
        l = list(range(len(env.population)))
        l.remove(self.id)
        self.neighbors = random.sample(l, params["neighbors"])

    def calculate_update(self, env) -> int:
        """Do the calculations for a single step in the simulation

        The data from this calculation is both stored (in next_data) and returned to the caller.  In the multiprocessing
        case, the data that is local to the copy of this Agent stored in a worker process is not available to the master
        and so any state that changes inside the agent (e.g., next_data) is going to seem like it "dissappears" from the
        agent.

        The explicit return allows us to retrieve the result of the agent calculation, and then pass it back in to the
        agent (via do_update) to update the agent's internal state

        Args:
            env:  The Environment for this simulation

        Returns: The value of the next data

        """
        # Just a function to get agent x's data
        f = lambda x: env.lookup(x).cur_data

        # Sleep a little bit to simulate something more complicated
        if self.process_time > 0:
            time.sleep(self.process_time)

        self.next_data = (sum(map(f, self.neighbors)) + self.cur_data) / env.my_special_stuff
        return self.next_data

    def do_update(self, data: int  = None) -> None:
        """ Updates the data for the next time step

        By default, this function copies 'next_data' into 'cur_data'.  However, also allows
        the caller to override this, enabling the multiprocessing cases described above (see
        calculate_update).

        Args:
            data: (optional) Data that the caller can pass in to override next_data
        """
        if data is None:
            self.cur_data = self.next_data
        else:
            self.cur_data = data


class Environment:
    """ Represents the context in which an agent operates

    This should provide any necessary bookkeeping for the agents, including
    functionality for managing id generation, and accessing other agents by id
    """

    def __init__(self):
        self.population = []
        """Holder for the population, indices correspond to ids"""

        self.my_special_stuff = 3
        """Perhaps some special variables that are shared by all agents"""

    def lookup(self, id: int) -> Agent:
        """ Get the agent corresponding to this id

        Args:
            id: The id of the agent to retrieve

        Returns:
            The Agent that corresponds to this index

        """
        return self.population[id]

    def register(self, agent: Agent) -> int:
        """ Register this agent with the simulation

        Args:
            agent: The agent to be registered

        Returns:
            The id for the new agent

        """
        self.population.append(agent)
        return len(self.population) - 1
