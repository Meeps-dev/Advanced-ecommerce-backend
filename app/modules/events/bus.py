from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable, DefaultDict


logger = logging.getLogger(__name__)
EventHandler = Callable[[Any], Any]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: DefaultDict[type, list[EventHandler]] = defaultdict(list)

    def clear(self) -> None:
        self._subscribers.clear()

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: Any) -> list[Any]:
        results: list[Any] = []
        handlers = self._subscribers.get(type(event), [])
        for handler in handlers:
            try:
                results.append(handler(event))
            except Exception:
                logger.exception(
                    "domain_event_handler_failed",
                    extra={
                        "event": "domain_event_handler_failed",
                        "event_type": type(event).__name__,
                        "handler": getattr(handler, "__name__", repr(handler)),
                    },
                )
        return results


event_bus = EventBus()
