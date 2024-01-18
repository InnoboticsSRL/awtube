
class HeartbeatFailure(Exception):
    """ Raised when heartbeat is not recieved in predefined time slot. """

    def __init__(self, message="Heartbeat missed!") -> None:
        self.message = message
        super().__init__(self.message)
