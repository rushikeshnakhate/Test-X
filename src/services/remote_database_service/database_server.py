"""
Database server implementation with multiple backend support.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from aiohttp import web


class BaseDatabaseBackend(ABC):
    """Abstract base class for database backends"""

    @abstractmethod
    async def connect(self, config: Dict[str, Any]) -> None:
        """Connect to the database"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        pass

    @abstractmethod
    async def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        """Execute a query and return results"""
        pass


class OracleBackend(BaseDatabaseBackend):
    """Oracle database backend implementation"""

    def __init__(self):
        self.connection = None

    async def connect(self, config: Dict[str, Any]) -> None:
        try:
            import cx_Oracle
            dsn = cx_Oracle.makedsn(config['host'], config['port'], service_name=config['service_name'])
            self.connection = await cx_Oracle.connect(
                user=config['user'],
                password=config['password'],
                dsn=dsn
            )
        except ImportError:
            raise Exception("cx_Oracle package not installed")
        except Exception as e:
            raise Exception(f"Oracle connection error: {str(e)}")

    async def disconnect(self) -> None:
        if self.connection:
            await self.connection.close()

    async def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        cursor = self.connection.cursor()
        try:
            await cursor.execute(query, params or [])

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                results = await cursor.fetchall()
                return {'columns': columns, 'results': results}
            else:
                return {'affected_rows': cursor.rowcount}
        except Exception as e:
            return {'error': str(e)}
        finally:
            await cursor.close()


class PostgreSQLBackend(BaseDatabaseBackend):
    """PostgreSQL database backend implementation"""

    def __init__(self):
        self.connection = None

    async def connect(self, config: Dict[str, Any]) -> None:
        try:
            import asyncpg
            self.connection = await asyncpg.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
        except ImportError:
            raise Exception("asyncpg package not installed")
        except Exception as e:
            raise Exception(f"PostgreSQL connection error: {str(e)}")

    async def disconnect(self) -> None:
        if self.connection:
            await self.connection.close()

    async def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        try:
            if query.strip().upper().startswith('SELECT'):
                results = await self.connection.fetch(query, *(params or []))
                if results:
                    columns = list(results[0].keys())
                    return {'columns': columns, 'results': [tuple(r.values()) for r in results]}
                return {'columns': [], 'results': []}
            else:
                result = await self.connection.execute(query, *(params or []))
                return {'affected_rows': int(result.split()[-1])}
        except Exception as e:
            return {'error': str(e)}


class SQLiteBackend(BaseDatabaseBackend):
    """SQLite database backend implementation"""

    def __init__(self):
        self.connection = None

    async def connect(self, config: Dict[str, Any]) -> None:
        try:
            import aiosqlite
            self.connection = await aiosqlite.connect(config['database'])
        except ImportError:
            raise Exception("aiosqlite package not installed")
        except Exception as e:
            raise Exception(f"SQLite connection error: {str(e)}")

    async def disconnect(self) -> None:
        if self.connection:
            await self.connection.close()

    async def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        cursor = await self.connection.cursor()
        try:
            await cursor.execute(query, params or [])

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                results = await cursor.fetchall()
                return {'columns': columns, 'results': results}
            else:
                return {'affected_rows': cursor.rowcount}
        except Exception as e:
            return {'error': str(e)}
        finally:
            await cursor.close()


class DatabaseServer:
    """HTTP server for database operations"""

    def __init__(self):
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.backend = None
        self.config = None

    async def connect(self, config: Dict[str, Any]) -> None:
        """Initialize the server with configuration"""
        self.config = config

        # Create appropriate backend
        db_type = config.get('type', 'sqlite').lower()
        if db_type == 'oracle':
            self.backend = OracleBackend()
        elif db_type == 'postgresql':
            self.backend = PostgreSQLBackend()
        else:  # default to SQLite
            self.backend = SQLiteBackend()

        await self.backend.connect(config)

        # Setup routes
        self.app.add_routes([
            web.post('/execute', self.handle_execute),
            web.get('/health', self.handle_health)
        ])

    async def disconnect(self) -> None:
        """Cleanup resources"""
        if self.backend:
            await self.backend.disconnect()
        if self.runner:
            await self.runner.cleanup()
        if self.site:
            await self.site.stop()

    async def start(self) -> None:
        """Start the HTTP server"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(
            self.runner,
            self.config.get('host', 'localhost'),
            self.config.get('port', 8080)
        )
        await self.site.start()
        logging.info(f"Server started at http://{self.config.get('host', 'localhost')}:{self.config.get('port', 8080)}")

    async def handle_execute(self, request: web.Request) -> web.Response:
        """Handle execute requests"""
        try:
            data = await request.json()
            query = data.get('query')
            params = data.get('params', [])

            if not query:
                return web.json_response({'error': 'No query provided'}, status=400)

            result = await self.backend.execute(query, params)

            if 'error' in result:
                return web.json_response({'error': result['error']}, status=400)

            return web.json_response(result)
        except json.JSONDecodeError:
            return web.json_response({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({'status': 'ok'})


# Example configuration
config = {
    'type': 'postgresql',  # or 'oracle', 'sqlite'
    'host': 'localhost',
    'port': 8080,
    'user': 'dbuser',
    'password': 'dbpass',
    'database': 'mydatabase',
    # Oracle specific:
    # 'service_name': 'ORCL'
}

import asyncio


async def main():
    # Server setup
    server_config = {
        'type': 'sqlite',  # or 'postgresql', 'oracle'
        'host': 'localhost',
        'port': 8080,
        'database': 'example.db'  # for SQLite
        # For PostgreSQL/Oracle you'd include user/password etc.
    }

    server = DatabaseServer()
    await server.connect(server_config)
    await server.start()

    print("Server started, press Ctrl+C to stop")

    # Keep server running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await server.disconnect()
        print("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
