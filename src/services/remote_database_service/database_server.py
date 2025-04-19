"""
Remote database server implementation.
"""
import asyncio
import json
import sqlite3
from typing import Dict, Any, Optional
from aiohttp import web
from src.base_classes.base_connection import BaseConnection


class DatabaseServer(BaseConnection):
    """Server for handling remote database connections"""

    def __init__(self):
        super().__init__()
        self._app = web.Application()
        self._runner = None
        self._site = None
        self._db_connection = None
        self._config = None

    async def connect(self, config: Dict[str, Any]) -> None:
        """Start the database server"""
        self._config = config
        self._db_connection = sqlite3.connect(config['database_path'])

        # Setup routes
        self._app.router.add_post('/execute', self._handle_execute)
        self._app.router.add_get('/health', self._handle_health)

        # Start server
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(
            self._runner,
            config['host'],
            config['port']
        )
        await self._site.start()
        self._is_connected = True

    async def disconnect(self) -> None:
        """Stop the database server"""
        if self._site:
            await self._runner.cleanup()
        if self._db_connection:
            self._db_connection.close()
        self._is_connected = False

    async def _handle_execute(self, request: web.Request) -> web.Response:
        """Handle SQL execution requests"""
        try:
            data = await request.json()
            query = data.get('query')
            params = data.get('params', [])

            if not query:
                return web.json_response({
                    'error': 'No query provided'
                }, status=400)

            cursor = self._db_connection.cursor()
            cursor.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return web.json_response({
                    'columns': columns,
                    'results': results
                })
            else:
                self._db_connection.commit()
                return web.json_response({
                    'affected_rows': cursor.rowcount
                })

        except Exception as e:
            return web.json_response({
                'error': str(e)
            }, status=500)

    async def _handle_health(self, request: web.Request) -> web.Response:
        """Handle health check requests"""
        return web.json_response({
            'status': 'healthy',
            'connected': self._is_connected
        })
