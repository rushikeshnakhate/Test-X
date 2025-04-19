from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
from datetime import datetime


class ConnectionEvent:
    def __init__(self, connection_id: str, event_type: str, details: Dict[str, Any] = None):
        self.connection_id = connection_id
        self.event_type = event_type
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class ConnectionObserver(ABC):
    @abstractmethod
    async def on_connection_event(self, event: ConnectionEvent) -> None:
        """Handle connection events"""
        pass


class ConnectionSubject(ABC):
    def __init__(self):
        self._observers: List[ConnectionObserver] = []
        self._lock = asyncio.Lock()

    async def attach(self, observer: ConnectionObserver) -> None:
        """Attach an observer"""
        async with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    async def detach(self, observer: ConnectionObserver) -> None:
        """Detach an observer"""
        async with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)

    async def notify(self, event: ConnectionEvent) -> None:
        """Notify all observers of an event"""
        async with self._lock:
            observers = self._observers.copy()

        await asyncio.gather(
            *[observer.on_connection_event(event) for observer in observers]
        )


class LoggingObserver(ConnectionObserver):
    async def on_connection_event(self, event: ConnectionEvent) -> None:
        print(f"[{event.timestamp}] Connection {event.connection_id}: {event.event_type}")
        if event.details:
            print(f"Details: {event.details}")


class MetricsObserver(ConnectionObserver):
    def __init__(self):
        self.metrics: Dict[str, Dict[str, int]] = {}
        self._lock = asyncio.Lock()

    async def on_connection_event(self, event: ConnectionEvent) -> None:
        async with self._lock:
            if event.connection_id not in self.metrics:
                self.metrics[event.connection_id] = {}

            event_counts = self.metrics[event.connection_id]
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1


class HealthCheckObserver(ConnectionObserver):
    def __init__(self):
        self.health_status: Dict[str, bool] = {}
        self._lock = asyncio.Lock()

    async def on_connection_event(self, event: ConnectionEvent) -> None:
        async with self._lock:
            if event.event_type == "health_check":
                self.health_status[event.connection_id] = event.details.get("healthy", False)
            elif event.event_type == "disconnected":
                self.health_status[event.connection_id] = False
