from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ConnectionEvent:
    """Event data for connection-related events."""
    connection_id: str
    event_type: str
    details: Dict[str, Any] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()


class ConnectionObserver(ABC):
    """Base class for connection observers."""

    @abstractmethod
    async def on_connection_event(self, event: ConnectionEvent) -> None:
        """Handle a connection event."""
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


class HealthObserver(ConnectionObserver):
    """Observer for monitoring connection health."""

    def __init__(self):
        """Initialize the health observer."""
        self.health_status: Dict[str, bool] = {}

    async def on_connection_event(self, event: ConnectionEvent) -> None:
        """Update health status based on connection events."""
        if event.event_type == "connection_created":
            self.health_status[event.connection_id] = True
        elif event.event_type == "connection_closed":
            self.health_status[event.connection_id] = False
        elif event.event_type == "connection_error":
            self.health_status[event.connection_id] = False


class MetricsObserver(ConnectionObserver):
    """Observer for collecting connection metrics."""

    def __init__(self):
        """Initialize the metrics observer."""
        self.metrics: Dict[str, Dict[str, int]] = {
            "connections": {"total": 0, "active": 0, "failed": 0},
            "events": {"created": 0, "closed": 0, "error": 0}
        }

    async def on_connection_event(self, event: ConnectionEvent) -> None:
        """Update metrics based on connection events."""
        if event.event_type == "connection_created":
            self.metrics["connections"]["total"] += 1
            self.metrics["connections"]["active"] += 1
            self.metrics["events"]["created"] += 1
        elif event.event_type == "connection_closed":
            self.metrics["connections"]["active"] -= 1
            self.metrics["events"]["closed"] += 1
        elif event.event_type == "connection_error":
            self.metrics["connections"]["failed"] += 1
            self.metrics["events"]["error"] += 1
