from __future__ import annotations
import json
import typing as tp
from awtube.ws_thread import WebsocketThread
from awtube.aw_types import *
from awtube.gbc_types import *
from awtube.commands import *
from awtube.exceptions import *
from collections import deque
import logging as lg
import time
import asyncio
import queue

TIMEOUT = 5


class AWTube(WebsocketThread):
    def __init__(self,
                 robot_ip: str = "0.0.0.0",
                 port: str = "9001",
                 headers=None,
                 config_path: str = None,
                 blocking: bool = True,
                 name: str = "AWTube",
                 log_level: int | str = lg.DEBUG,
                 logger: lg.Logger | None = None):
        self._name = name
        self.__robot_ip = robot_ip
        self.__port = port
        self.blocking = blocking
        self.__txbuffer = queue.Queue()
        self.url = f"ws://{self.__robot_ip}:{self.__port}/ws"

        # TODO
        self._config_path = config_path
        #  TODO: parametric with config file
        self._state_memory_length = 5
        # if not self.blocking:
        super().__init__(self.url, headers)

        # logging
        if logger:
            self._logger = logger
        else:
            self._logger = lg.getLogger(self._name)
            self._logger.setLevel(lg.DEBUG)
        self.received_message = False

        # last commands sent
        self._set_joint_states = deque(maxlen=self._state_memory_length)

        # actual position feedback
        self._act_joint_states = deque(maxlen=self._state_memory_length)

        # record last heartbeat with timestamp
        self.timed_heartbeat: tuple(int, float) = None

        # machine status
        self._machine_status = None
        self._stream_status = None
        self._activity_status = None
        self._current_tag = None
        # self._current_cmd_done = False

        # Start yielding messages from txbuffer
        self._tasks.append(self.send_cmds)
        self._tasks.append(self.echo_heartbeat)
        self._tasks.append(self.reset_enable)

    async def reset(self) -> None:
        self._logger.debug('Reset machine.')
        await asyncio.sleep(1)
        self.send(get_machine_command(
            control_word=ControlWord.FAULTRESET128))
        await asyncio.sleep(1)
        self.send(get_machine_command(control_word=ControlWord.RESET))
        return self

    async def enable(self) -> None:
        self._logger.debug('Enable machine.')
        await asyncio.sleep(1)
        self.send(get_machine_command(
            control_word=ControlWord.SHUTDOWN))
        await asyncio.sleep(1)
        self.send(get_machine_command(
            control_word=ControlWord.QUICKSTOP))
        await asyncio.sleep(1)
        self.send(get_machine_command(
            control_word=ControlWord.FAULTRESET))
        return self

    async def reset_enable(self, socket: WebsocketThread) -> None:
        await self.reset()
        await self.enable()

    async def echo_heartbeat(self, socket: WebsocketThread) -> None:
        """ Get latest heartbeat sent and periodically every 200 ms send it back """
        while True:
            if self._machine_status:
                self.send(get_machine_command_heartbeat(
                    heartbeat=self._machine_status.heartbeat))
                self._logger.debug(
                    f'Sent heartbeat:{self._machine_status.heartbeat}')
            await asyncio.sleep(0.2)

    def put_txbuffer(self, message: str) -> None:
        """ Put command in queue to send respecting the capacity of the websocket stream.

        Args:
            message: The string message to send over the socket.
        """
        self.__txbuffer.put(message)

    async def send_cmds(self, socket: WebsocketThread) -> None:
        """ asyncio coroutine which takes messages from txbuffer and puts them in the outter queue,
            respecting the capacity of the stream. """
        while True:
            if self._stream_status:
                print(f'Capacity: {self._stream_status.capacity}')

            if self.__txbuffer.empty():
                # TODO: decide on good sleep interval
                # sleep and check again
                await asyncio.sleep(0.1)
            # elif self._stream_status.read_count != self._stream_status.write_count:
            #     await asyncio.sleep(0.01)
            elif not self._stream_status:
                # if no feedback recieved yet
                await asyncio.sleep(0.1)
            elif self._stream_status.capacity >= 15:
                # get from txbuffer and send
                self.send(self.__txbuffer.get())
                # await asyncio.sleep(0.02)
                # print('Put new command in txbuffer.')

    def get_state(self, message: str) -> None:
        """ Here get last n telemetry points from ws which will be used as the state of the robot. """
        try:
            js = json.loads(message)

            # joint states
            # TODO: clean up
            for el in js['telemetry'][-self._state_memory_length:]:
                # get set commands
                self._set_joint_states.append(JointStates(
                    positions=[all['p'] for all in el['set']],
                    velocities=[all['v'] for all in el['set']],
                    accelerations=[all['a'] for all in el['set']],
                    torques=[all['t'] for all in el['set']]
                ))
                # get actual feedback from encoders
                self._act_joint_states.append(JointStates(
                    positions=[all['p'] for all in el['act']],
                    velocities=[all['v'] for all in el['act']],
                    accelerations=[all['a'] for all in el['act']],
                    torques=[all['t'] for all in el['act']]
                ))

            self._machine_status = MachineStatus(**js['status']['machine'])

            # TODO: stream array id ??????
            self._stream_status = StreamStatus(**js['stream'][0])

            self._activity_status = ActivityStatus(
                **js['status']['activity'][0])

            self.received_message = True

            # record timed heartbeat
            self.timed_heartbeat = (
                self._machine_status.heartbeat, time.time())

        except Exception as e:
            self._logger.error(e)
            # await self.stop_loop()

    def get_logger(self) -> lg.Logger:
        return self._logger

    async def handle_message(self, message: str) -> None:
        """ json message callback. """
        self._logger.debug('Handling new message.')
        self.get_state(message)
        # self.send_heartbeat()

    def send_heartbeat(self) -> None:
        if self._machine_status:
            self.send(get_machine_command_heartbeat(
                heartbeat=self._machine_status.heartbeat))
            self._logger.debug(
                f'Sent heartbeat:{self._machine_status.heartbeat}')

    def move_joints(self, joint_positions: tp.List[float], tag: int = 0, blocking: bool = False) -> AWTube:
        """ Send moveJoints command. """
        # TODO: better checks
        joints = JointStates(positions=joint_positions)
        self.send(get_stream_move_joints(joints, tag=tag))
        self._logger.debug('Sent moveJoints command.')
        return self

    def move_to_position(self, translation: tp.Dict[str, float], rotation: tp.Dict[str, float]) -> AWTube:
        """ Send moveToPosition command. """
        pose = Pose(position=Position(**translation),
                    orientation=Quaternion(**rotation))
        self.send(get_stream_move_to_position(pose))
        self._logger.debug('Sent moveToPosition command.')
        return self

    def move_joints_vel(self, joint_velocities: tp.List[float]) -> AWTube:
        """ Send moveJointsAtVel command. """
        joints = JointStates(velocities=joint_velocities)
        self.send(get_stream_move_joints_at_vel(joints))
        self._logger.debug('Sent moveJointsAtVel command.')
        return self

    def move_joints_interpolated(self,
                                 joint_positions: tp.List[float],
                                 joint_velocities: tp.List[float],
                                 tag: int = 0,
                                 debug: bool = False) -> AWTube:
        """ Put moveJointsInterpolated command on txbuffer. """
        joints = JointStates(positions=joint_positions,
                             velocities=joint_velocities)
        if self._stream_status:
            self.put_txbuffer(get_stream_move_joints_interpolated(
                joints, tag=tag, debug=debug))
            self._logger.debug('Sent moveJointsInterpolated command.')
        else:
            raise Exception('Stream status is None.')
        return self

    def move_line(self, translation: tp.Dict[str, float],  rotation: tp.Dict[str, float], tag: int = 0) -> AWTube:
        """ Send moveLine command. """
        pose = Pose(position=Position(**translation),
                    orientation=Quaternion(**rotation))
        self.send(get_stream_move_line(pose, debug=False, tag=tag))
        self._logger.debug('Sent moveLine command.')
        return self

    def pause(self) -> AWTube:
        """ Send pause command. """
        return NotImplementedError
        self.send(get_stream_pause_program(debug=True))
        self._logger.debug('Sent pause command.')
        return self

    def move_arc(self) -> AWTube:
        """ Send moveArc command. """
        raise NotImplementedError()
        self._logger.debug('Sent moveArc command.')
        return self

    def move_rotation_vel(self) -> AWTube:
        """ Send moveRotationAtVel command. """
        raise NotImplementedError()
        self._logger.debug('Sent moveRotationAtVel command.')
        return self

    def move_vector_vel(self) -> AWTube:
        """ Send moveVectorAtVel command. """
        raise NotImplementedError()
        self._logger.debug('Sent moveVectorAtVel command.')
        return self

    def set_max_speed() -> AWTube:
        """ Send setMaxSpeed command. """
        raise NotImplementedError()
        self._logger.debug('Sent setMaxSpeed command.')
        return self

    def set_max_acceleration() -> AWTube:
        """ Send setMaxAcceleration command. """
        raise NotImplementedError()
        self._logger.debug('Sent setMaxAcceleration command.')
        return self
