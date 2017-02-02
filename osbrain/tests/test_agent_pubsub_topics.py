import time

from osbrain import run_agent

from common import nsaddr  # pragma: no flakes
from common import nsproxy  # pragma: no flakes


def log_received_to_list(agent, message, topic=None):
    agent.received_list.append(message)


def test_pubsub(nsaddr):
    """
    Simple publisher-subscriber pattern test.

    Different messages sent with different agents subscribed to different
    topics are tested within this method.
    """
    a0 = run_agent('a0')
    a1 = run_agent('a1')
    a2 = run_agent('a2')
    a3 = run_agent('a3')
    a4 = run_agent('a4')
    a5 = run_agent('a5')

    for agent in (a1, a2, a3, a4, a5):
        agent.set_attr(received_list=[])

    addr = a0.bind('PUB', alias='pub')

    a1.connect(addr, handler=log_received_to_list)
    a2.connect(addr, handler={'foo': log_received_to_list})
    a3.connect(addr, handler={'bar': log_received_to_list,
                              'foo': log_received_to_list})
    a4.connect(addr, handler={'bar': log_received_to_list})
    a5.connect(addr, handler={'fo': log_received_to_list})

    # Give some time for all the agents to connect
    time.sleep(0.1)

    # Send some messages
    message_01 = 'Hello'
    a0.send('pub', message_01)

    message_02 = 'World'
    a0.send('pub', message_02, topic='foo')

    message_03 = 'FOO'
    a0.send('pub', message_03, topic='foobar')

    message_04 = 'BAR'
    a0.send('pub', message_04, topic='fo')

    # Give some time for all the agents to handle the message
    time.sleep(0.1)

    # Check each agent received the corresponding messages
    assert message_01 in a1.get_attr('received_list')
    assert message_02 in a1.get_attr('received_list')
    assert message_03 in a1.get_attr('received_list')
    assert message_04 in a1.get_attr('received_list')

    assert message_01 not in a2.get_attr('received_list')
    assert message_02 in a2.get_attr('received_list')
    assert message_03 in a2.get_attr('received_list')
    assert message_04 not in a2.get_attr('received_list')

    assert message_01 not in a3.get_attr('received_list')
    assert message_02 in a3.get_attr('received_list')
    assert message_03 in a3.get_attr('received_list')
    assert message_04 not in a3.get_attr('received_list')

    assert message_01 not in a4.get_attr('received_list')
    assert message_02 not in a4.get_attr('received_list')
    assert message_03 not in a4.get_attr('received_list')
    assert message_04 not in a4.get_attr('received_list')

    assert message_01 not in a5.get_attr('received_list')
    assert message_02 in a5.get_attr('received_list')
    assert message_03 in a5.get_attr('received_list')
    assert message_04 in a5.get_attr('received_list')