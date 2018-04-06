"""
Test file for bugs found in osbrain.
"""
import time
import sys

from osbrain import Agent
from osbrain import run_agent
from osbrain.helper import agent_dies
from osbrain.helper import wait_condition
from osbrain.helper import wait_agent_condition

from common import nsproxy  # noqa: F401


def test_timer_recursion(nsproxy):
    """
    This bug occurred with the first implementation of the timer. After
    some iterations the timer would throw an exception when the recursion
    limit was exceeded. Timers should never reach a recursion limit.
    """
    def inc(agent):
        agent.count += 1

    agent = run_agent('a0')
    agent.set_attr(count=0)
    agent.each(0.0, inc)

    limit = sys.getrecursionlimit()
    assert wait_agent_condition(agent, lambda agent: agent.count > limit,
                                timeout=10)


def test_slow_clean_up_socket_files(nsproxy):
    """
    Even if the clean-up process is slow, IPC socket files should always be
    cleaned. This test was created to ensure that the clean-up process is
    executed before the agent's daemon shutdown when the agent is killed.
    """
    class Lazy(Agent):
        def _clean_up(self):
            time.sleep(0.5)
            super()._clean_up()

    agent = run_agent('a0', base=Lazy)
    address = agent.bind('PUSH')
    agent.oneway.kill()

    assert agent_dies('name', nsproxy)
    assert wait_condition(address.address.exists, negate=True)
