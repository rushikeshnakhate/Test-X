from typing import Any, Optional, Dict

# import quickfix

from ...base_classes.base_connection import BaseConnection
from ...base_classes.base_service import BaseService
from ...common.connection_manager import ConnectionManager


class QuickFixApplication():
    def __init__(self):
        super().__init__()
        self.is_logged_on = False

    def onCreate(self, sessionID):
        self.sessionID = sessionID

    def onLogon(self, sessionID):
        self.is_logged_on = True

    def onLogout(self, sessionID):
        self.is_logged_on = False

    def toAdmin(self, message, sessionID):
        pass

    def fromAdmin(self, message, sessionID):
        pass

    def toApp(self, message, sessionID):
        pass

    def fromApp(self, message, sessionID):
        pass


class QuickFixConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # self._settings = quickfix.SessionSettings(config.config_file_name)
        # self._store_factory = quickfix.FileStoreFactory(self._settings)
        # self._log_factory = quickfix.FileLogFactory(self._settings)
        # self._application = QuickFixApplication()
        # self._initiator: Optional[quickfix.SocketInitiator] = None

    async def connect(self) -> None:
        try:
            # self._initiator = quickfix.SocketInitiator(
            #     self._application,
            #     self._store_factory,
            #     self._settings,
            #     self._log_factory
            # )
            self._initiator.start()
            self._connected = True
        except Exception as e:
            self._connected = False
            raise ConnectionError(f"Failed to connect QuickFix: {str(e)}")

    async def disconnect(self) -> None:
        pass
        # if self._initiator:
        #     self._initiator.stop()
        #     self._connected = False
        #     self._initiator = None

    async def health_check(self) -> bool:
        pass
        # return self._connected and self._application.is_logged_on

    # async def send_message(self, message: quickfix.Message) -> None:
    #     if not self.is_connected:
    #         raise ConnectionError("QuickFix service is not connected")
    #
    #     session = quickfix.Session.lookupSession(self._application.sessionID)
    #     if not session:
    #         raise ConnectionError("No active QuickFix session")
    #
    #     quickfix.Session.sendToTarget(message, self._application.sessionID)


class QuickFixService(BaseService):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._connection: Optional[QuickFixConnection] = None

    async def initialize(self) -> None:
        connection_id = "quickfix"
        self._connection = await ConnectionManager.get_connection(
            connection_id,
            QuickFixConnection,
            self.config
        )

    async def shutdown(self) -> None:
        if self._connection:
            await ConnectionManager.close_connection("quickfix")
            self._connection = None

    async def health_check(self) -> bool:
        if not self._connection:
            return False
        return await self._connection.health_check()

    async def send_order(self, order_details: Dict[str, Any]) -> None:
        """Send a new order via QuickFix"""
        if not self._connection or not self._connection.is_connected:
            raise ConnectionError("QuickFix service is not connected")
        pass
        # message = quickfix.Message()
        # message.getHeader().setField(35, "D")  # MsgType = NewOrderSingle
        #
        # # Set order fields
        # message.setField(11, order_details.get("clOrdID", ""))  # ClOrdID
        # message.setField(55, order_details.get("symbol", ""))  # Symbol
        # message.setField(54, order_details.get("side", "1"))  # Side
        # message.setField(38, order_details.get("quantity", 0))  # OrderQty
        # message.setField(40, order_details.get("orderType", "1"))  # OrdType
        #
        # if "price" in order_details:
        #     message.setField(44, order_details["price"])  # Price
        #
        # await self._connection.send_message(message)
