"""
This demo script is designed to illustrate a simple approach to using multiprocessing
in Python to run an agent-based model in a multicore environment
"""

from abm import Agent, Environment
from multiprocessing import Pool
import time

"""Dictionary of parameters for the simulation; presumably would be drawn from a configuration file"""
params = {"neighbors": 3,
          "max": 50,
          "iterations": 30,
          "agents": 20,
          "processes": 15,              # The number of processes we should run in our pool
          "process_time":.25}          # The amount of time each agent should sleep during the update function

"""Special globally accessible variable for copying the environment into a worker process"""
worker_env = None


def update(a:Agent) -> (int,int):
    """ Encapsulates the update function for an agent

    Provided to the pool for running the update function on each agent.

    Args:
        a: The agent to run the calculation on

    Returns:
        A tuple consisting of the agent's id, and the result of the update from the agent

    """
    return a.id, a.calculate_update(worker_env)


def initializer(arg:Environment) -> None:
    """  Initializes the worker context

    The initializer function takes care of copying any data from the Master's context into
    the Worker's context. This copy of the data is is made available to each worker via a global
    variable

    Args:
        arg: In this case, this is just the Environment
    """
    global worker_env
    worker_env = arg


def doit():
    """ Simply runs the simulation

    Returns: Nothing

    """
    env = Environment()
    for i in range(params["agents"]):
        Agent(env)

    for a in env.population:
        a.setup(params,env)

    for i in range(params["iterations"]):

        # Here you can initialize the pool with however many worker processes you want.
        # In general, it makes sense to put something like one less than the number of cores you have
        # Note the initializer function just copies the local environment into a global context for
        # each worker.  There are probably more efficient ways to do this
        start = time.time()
        with Pool(params["processes"], initializer, initargs=(env,)) as p:
            result = p.map(update, env.population)

        for id, data in result:
            env.lookup(id).do_update(data)

        end = time.time()
        print("Iteration {} ({} seconds) - {}".format(i, end-start, ", ".join(
            map(lambda x: "A" + str(x.id) + ":" + str(x.cur_data), env.population))))


if __name__ == "__main__":
    doit()
