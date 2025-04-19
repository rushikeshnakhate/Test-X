import aiohttp
from typing import Any, Optional, Dict
from ...base_classes.base_connection import BaseConnection


class RemoteCommandConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url = f"http{'s' if self.config.port == 443 else ''}://{self.config.host}:{self.config.port}"

    async def connect(self) -> None:
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "X-API-Version": self.config.api_version
            }
            self._session = aiohttp.ClientSession(headers=headers)
            # Test connection
            async with self._session.get(f"{self._base_url}/health") as response:
                if response.status != 200:
                    raise ConnectionError(f"Health check failed: {response.status}")
            self._connected = True
        except Exception as e:
            self._connected = False
            if self._session:
                await self._session.close()
            raise ConnectionError(f"Failed to connect to Remote Command service: {str(e)}")

    async def disconnect(self) -> None:
        if self._session:
            await self._session.close()
            self._connected = False
            self._session = None

    async def health_check(self) -> bool:
        if not self._session:
            return False
        try:
            async with self._session.get(f"{self._base_url}/health") as response:
                return response.status == 200
        except Exception:
            return False

    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.is_connected:
            raise ConnectionError("Remote Command service is not connected")

        try:
            async with self._session.post(
                    f"{self._base_url}/execute",
                    json={"command": command, "parameters": params or {}}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Command execution failed: {response.status}")
                return await response.json()
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    async def list_available_commands(self) -> Dict[str, Any]:
        """Get list of available commands"""
        if not self.is_connected:
            raise ConnectionError("Remote Command service is not connected")

        try:
            async with self._session.get(f"{self._base_url}/commands") as response:
                if response.status != 200:
                    raise Exception(f"Failed to get commands: {response.status}")
                return await response.json()
        except Exception as e:
            raise Exception(f"Failed to get available commands: {str(e)}")
