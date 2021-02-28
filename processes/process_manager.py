import typing
from processes import Process


class BusyException(Exception):
    """Raise if a user already has a process running"""


class ProcessManager:
    user_processes: dict[int, Process] = {}

    @staticmethod
    async def spawn(user_id: int, process: Process):
        if user_id in ProcessManager.user_processes and ProcessManager.user_processes[user_id]:
            raise BusyException()
        ProcessManager.user_processes[user_id] = process
        await ProcessManager.user_processes[user_id].start()
        ProcessManager.clean(user_id)

    # note that this doesn't kill the process, just cleans the dict
    @staticmethod
    def clean(user_id: int):
        ProcessManager.user_processes[user_id] = None
