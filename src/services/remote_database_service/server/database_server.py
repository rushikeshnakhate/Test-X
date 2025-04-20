"""
Remote database server implementation.
"""
import logging
import threading
import socketserver
from http.server import BaseHTTPRequestHandler
import json
from typing import Dict, Any, Optional
import asyncio

from src.base_classes.base_connection import BaseConnection
from src.common.logging_config import setup_logging
from .database_adapter import DatabaseAdapter

setup_logging(__name__, "DEBUG")
logger = logging.getLogger(__name__)


class DatabaseRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler using DatabaseAdapter"""

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for SQL execution"""
        if self.path == '/execute':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data)
                query = data.get('query')
                params = data.get('params', [])

                logger.debug(f"Executing query: {query} with params: {params}")

                if not query:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': 'No query provided'}).encode())
                    return

                result = self.server.database_adapter.execute(query, params)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())

            except Exception as e:
                logger.error(f"Query execution failed: {str(e)}")
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_GET(self):
        """Handle health check requests"""
        if self.path == '/health':
            try:
                # Create event loop and run health check
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    health_status = loop.run_until_complete(self.server.server.health_check())
                    response = {
                        'status': 'healthy' if health_status else 'unhealthy',
                        'connected': health_status
                    }
                except Exception as e:
                    logger.error(f"Health check failed: {str(e)}", exc_info=True)
                    response = {
                        'status': 'unhealthy',
                        'connected': False,
                        'error': str(e)
                    }
                finally:
                    loop.close()

                self._set_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                logger.error(f"Error handling health check request: {str(e)}", exc_info=True)
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    'status': 'unhealthy',
                    'connected': False,
                    'error': str(e)
                }).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())


class DatabaseServer(BaseConnection):
    """Database server with pluggable database adapter"""

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 9001
    DEFAULT_DB_PATH = ':memory:'

    def __init__(self, adapter: DatabaseAdapter, config: Optional[Dict[str, Any]] = None):
        # Initialize with merged config
        merged_config = {
            'host': self.DEFAULT_HOST,
            'port': self.DEFAULT_PORT,
            'database_path': self.DEFAULT_DB_PATH
        }
        if config:
            merged_config.update(config)

        super().__init__(merged_config)
        self._adapter = adapter
        self._httpd = None
        self._server_thread = None
        logger.debug(f"Initialized database server with config: {merged_config}")

    async def health_check(self) -> bool:
        """Implementation of abstract health_check method"""
        try:
            # Check if server is running and database is connected
            if not self._is_connected:
                logger.warning("Database server is not connected")
                return False

            if not self._httpd:
                logger.warning("HTTP server is not initialized")
                return False

            if not self._server_thread or not self._server_thread.is_alive():
                logger.warning("Server thread is not running")
                return False

            # Check database adapter health
            if not self._adapter.is_connected():
                logger.warning("Database adapter is not connected")
                return False

            logger.debug("Database server health check passed")
            return True
        except Exception as e:
            logger.error(f"Error during health check: {str(e)}", exc_info=True)
            return False

    async def connect(self, connection_params: Optional[Dict[str, Any]] = None) -> None:
        """Start the server with database connection"""
        # Use provided params or fall back to initialized config
        params = connection_params if connection_params is not None else self.config

        try:
            # Connect to database using adapter
            logger.info("Connecting to database...")
            self._adapter.connect(params)

            # Start HTTP server
            self._httpd = socketserver.TCPServer(
                (params['host'], params['port']),
                DatabaseRequestHandler
            )
            self._httpd.database_adapter = self._adapter
            self._httpd.server = self

            # Start in background thread
            self._server_thread = threading.Thread(target=self._httpd.serve_forever)
            self._server_thread.daemon = True
            self._server_thread.start()

            logger.info(f"Server running on {params['host']}:{params['port']}")
            self._is_connected = True

        except Exception as e:
            logger.error(f"Server startup failed: {str(e)}", exc_info=True)
            self._is_connected = False
            raise

    async def disconnect(self) -> None:
        """Stop the server and disconnect database"""
        logger.info("Shutting down server...")

        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()

        self._adapter.disconnect()
        self._is_connected = False
        logger.info("Server shutdown complete")
