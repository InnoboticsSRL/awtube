import pytest
import asyncio
import json
from awtube.types import *
from awtube.types import *
from awtube.commands import *
from awtube.awtube import AWTube

"""
  Tests for the queues of the system. Check if the mechanism that moves queues from one queue to the other
  respecting the capacity works. """

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def awtube():
    return AWTube('0.0.0.0', port=1111)


@pytest.fixture
def awtube_tx_buffer_10(awtube):
    a = awtube
    for i in range(10):
        awtube.put_txbuffer(i)
    return a


@pytest.mark.asyncio
async def test_overflow(awtube_tx_buffer_10):
    # await asyncio.sleep(1)
    # move_cmds starts moving cmds at 15 and up
    awtube_tx_buffer_10._stream_status = StreamStatus()
    awtube_tx_buffer_10._stream_status.capacity = 15
    await awtube_tx_buffer_10.move_cmds()
    await awtube_tx_buffer_10.move_cmds()
    awtube_tx_buffer_10._stream_status.capacity = 14
    await awtube_tx_buffer_10.move_cmds()
    await awtube_tx_buffer_10.move_cmds()
    assert awtube_tx_buffer_10._AWTube__txbuffer.qsize() == 8
