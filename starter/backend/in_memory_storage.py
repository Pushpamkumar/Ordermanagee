"""
In-Memory Storage Adapter Module

Provides a thread-safe ephemeral key-value data store for order records.
Implements the storage interface contract required by OrderTracker.
"""

from threading import RLock
from typing import Any, Dict, Optional


class InMemoryStorage:
    """
    Thread-safe in-memory key-value repository for orders.
    Useful for testing, development, and standalone lightweight execution.
    """

    def __init__(self) -> None:
        self._orders: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()

    def save_order(self, order_id: str, order_data: Dict[str, Any]) -> None:
        """
        Saves or updates an order in the storage repository.
        Stores an isolated shallow copy to prevent external mutation leaks.
        """
        with self._lock:
            self._orders[str(order_id)] = order_data.copy()

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single order by ID.
        Returns a fresh copy or None if no match is found.
        """
        with self._lock:
            record = self._orders.get(str(order_id))
            return record.copy() if record is not None else None

    def get_all_orders(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns a dictionary map of all stored orders keyed by order ID.
        """
        with self._lock:
            return {oid: data.copy() for oid, data in self._orders.items()}

    def clear(self) -> None:
        """
        Clears all records in memory. Primarily used to reset state between tests.
        """
        with self._lock:
            self._orders.clear()
