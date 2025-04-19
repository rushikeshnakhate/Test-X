from ...base_classes.base_connection import BaseConnection


class IMIXConnection(BaseConnection):
    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def health_check(self) -> bool:
        pass

    def __init__(self):
        super().__init__()
        pass
