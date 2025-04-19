from typing import Any, Optional, Dict, List

import aiohttp

from ...base_classes.base_connection import BaseConnection


class RemoteSearchConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url = f"http{'s' if self.config.port == 443 else ''}://{self.config.host}:{self.config.port}"

    async def connect(self) -> None:
        try:
            headers = {
                "Content-Type": "application/json"
            }
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.search_timeout)
            )
            # Test connection
            async with self._session.get(f"{self._base_url}/health") as response:
                if response.status != 200:
                    raise ConnectionError(f"Health check failed: {response.status}")
            self._connected = True
        except Exception as e:
            self._connected = False
            if self._session:
                await self._session.close()
            raise ConnectionError(f"Failed to connect to Pattern Search service: {str(e)}")

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

    async def search_pattern(self, pattern: str, options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not self.is_connected:
            raise ConnectionError("Pattern Search service is not connected")

        try:
            search_params = {
                "pattern": pattern,
                "max_results": self.config.max_results,
                **(options or {})
            }

            async with self._session.post(
                    f"{self._base_url}/search",
                    json=search_params
            ) as response:
                if response.status != 200:
                    raise Exception(f"Pattern search failed: {response.status}")
                results = await response.json()
                return results.get("matches", [])[:self.config.max_results]
        except Exception as e:
            raise Exception(f"Failed to execute pattern search: {str(e)}")
