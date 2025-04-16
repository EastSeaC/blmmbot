# async_event_bus.py
import asyncio
from typing import Dict, List, Callable, Any


class AsyncEventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers: Dict[str, List[Callable]] = {}
        return cls._instance

    async def publish(self, event_type: str, data: Any = None):
        if event_type in self._subscribers:
            await asyncio.gather(
                *[callback(data) for callback in self._subscribers[event_type]]
            )

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)