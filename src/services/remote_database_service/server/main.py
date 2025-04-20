# from src.services.database.oracle_adapter import OracleAdapter
# async def main():
#     adapter = OracleAdapter()  # Instead of SQLiteAdapter
#     server = DatabaseServer(adapter)
#
#     config = {
#         'host': 'oracle-db.example.com',
#         'port': 1521,
#         'username': 'admin',
#         'password': 'secret',
#         'service_name': 'ORCL'
#     }
#
#     await server.connect(config)
#     print(f"Server running on {server.DEFAULT_HOST}:{server.DEFAULT_PORT}")
#     print("Press Ctrl+C to stop...")

import asyncio

from src.services.remote_database_service.server.database_server import DatabaseServer
from src.services.remote_database_service.server.sqlite_adapter import SQLiteAdapter


async def main():
    # Create adapter
    adapter = SQLiteAdapter()

    # Configuration - can be changed for different databases
    config = {
        'host': 'localhost',
        'port': 9001,
        'database_path': 'my_database.db'  # or ':memory:' for in-memory DB
    }

    # Create server with config
    server = DatabaseServer(adapter, config)

    try:
        # Start the server
        await server.connect()
        print(f"Server running on {config['host']}:{config['port']}")
        print("Press Ctrl+C to stop...")

        # Keep server running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down server...")
        await server.disconnect()
    except Exception as e:
        print(f"Error: {str(e)}")
        await server.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
