from typing import Any, Optional, Dict

import oracledb

from ...base_classes.base_connection import BaseConnection
from ...base_classes.base_service import BaseService
from ...common.connection_manager import ConnectionManager


class OracleConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._connection: Optional[oracledb.AsyncConnection] = None

    async def connect(self) -> None:
        try:
            self._connection = await oracledb.connect_async(
                user=self.config.username,
                password=self.config.password,
                dsn=f"{self.config.host}:{self.config.port}/{self.config.service_name}",
                encoding="UTF-8"
            )
            self._connected = True
        except Exception as e:
            self._connected = False
            raise ConnectionError(f"Failed to connect to Oracle database: {str(e)}")

    async def disconnect(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connected = False
            self._connection = None

    async def health_check(self) -> bool:
        try:
            if not self._connection:
                return False
            async with self._connection.cursor() as cursor:
                await cursor.execute("SELECT 1 FROM DUAL")
                return True
        except Exception:
            return False


class OracleService(BaseService):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._connection: Optional[OracleConnection] = None

    async def initialize(self) -> None:
        connection_id = f"oracle_{self.config.name}"
        self._connection = await ConnectionManager.get_connection(
            connection_id,
            OracleConnection,
            this.config
        )

    async def shutdown(self) -> None:
        if self._connection:
            await ConnectionManager.close_connection(f"oracle_{self.config.name}")
            self._connection = None

    async def health_check(self) -> bool:
        if not self._connection:
            return False
        return await self._connection.health_check()

    async def execute_query(self, query: str, params: dict = None) -> Any:
        if not self._connection or not self._connection.is_connected:
            raise ConnectionError("Service is not connected")

        async with self._connection._connection.cursor() as cursor:
            await cursor.execute(query, params or {})
            return await cursor.fetchall()
