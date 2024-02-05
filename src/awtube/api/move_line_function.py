from awtube.api.robot_function import RobotFunction
from awtube.commands.move_joints_interpolated import MoveJointsInterpolated
from awtube.commanders.stream_commander import StreamCommander
from awtube.command_reciever import CommandReciever
import typing as tp
from awtube.commands import move_line


class MoveLineFunction(RobotFunction):
    def __init__(self, stream_commander: StreamCommander, reciever: CommandReciever) -> None:
        self._stream_commander = stream_commander
        self._reciever = reciever

    async def move_line(self,
                        translation: tp.Dict[str, float],
                        rotation: tp.Dict[str, float],
                        tag: int = 0) -> None:
        """ Send a moveLine command to a CommandReciever.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        cmd = move_line.MoveLine(self._reciever, translation, rotation, tag)
        self._stream_commander.add_command(cmd)
        await self._stream_commander.execute_commands()
