from __future__ import annotations
import json
import time
from awtube.gbc_types import StreamStatus
from awtube.observers.observer import Observer
from awtube.aw_types import JointStates
from collections import deque


class TelemetryObserver(Observer):
    """
    The Observer interface declares the update coroutine, used by subjects.
    """

    def __init__(self) -> None:
        self.stream_status = None
        self.state_memory_length = 1
        self.set_joint_states = deque(maxlen=self.state_memory_length)
        self.act_joint_states = deque(maxlen=self.state_memory_length)

    def update(self, message: str) -> None:
        """
        Recieve update from subject and decode message.

        Raises:
            NotImplementedError:
        """
        try:
            js = json.loads(message)
            # TODO: stream array id ??????
            self._payload = JointStates(
                positions=[joint_i['p']
                           for joint_i in js['telemetry'][-1]['set']],
                velocities=[joint_i['v']
                            for joint_i in js['telemetry'][-1]['set']],
                accelerations=[joint_i['a']
                               for joint_i in js['telemetry'][-1]['set']],
                torques=[joint_i['t'] for joint_i in js['telemetry'][-1]['set']])
            # for el in js['telemetry'][-self.state_memory_length:]:
            #     # get set commands
            #     print('here')
            #     self.set_joint_states.append(JointStates(
            #         positions=[all['p'] for all in el['set']],
            #         velocities=[all['v'] for all in el['set']],
            #         accelerations=[all['a'] for all in el['set']],
            #         torques=[all['t'] for all in el['set']]
            #     ))
            #     # get actual feedback from encoders
            #     self.act_joint_states.append(JointStates(
            #         positions=[all['p'] for all in el['act']],
            #         velocities=[all['v'] for all in el['act']],
            #         accelerations=[all['a'] for all in el['act']],
            #         torques=[all['t'] for all in el['act']]
            #     ))

            # record timestamp
            self._timestamp = time.time()

        except Exception as e:
            # self._logger.error(e)
            print(e)
            # print('Not recieving any telemetry!')
