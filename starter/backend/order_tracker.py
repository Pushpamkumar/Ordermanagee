"""
Order Management Domain Module

Encapsulates core business logic, lifecycle rules, and state transitions
for order tracking following Clean Architecture and TDD principles.
"""

from typing import Any, Dict, List, Optional


class OrderValidationError(ValueError):
    """Raised when order parameters fail domain validation rules."""
    pass


class OrderNotFoundError(ValueError):
    """Raised when an operation targets a non-existent order ID."""
    pass


class OrderTracker:
    """
    Core domain service managing order lifecycle and fulfillment states.
    Decoupled from storage implementations via interface inversion.
    """

    ALLOWED_STATUSES = {"pending", "processing", "shipped", "delivered", "cancelled"}

    def __init__(self, storage: Any) -> None:
        """
        Initialize the OrderTracker with a compatible storage backend.
        
        :param storage: Storage backend implementing save_order, get_order, and get_all_orders.
        :raises TypeError: If storage backend is missing required interface methods.
        """
        required_interface = ("save_order", "get_order", "get_all_orders")
        for method_name in required_interface:
            method = getattr(storage, method_name, None)
            if not callable(method):
                raise TypeError(
                    f"Storage adapter must provide a callable '{method_name}' method."
                )
        self.storage = storage

    def _validate_order_payload(
        self,
        order_id: str,
        item_name: str,
        quantity: int,
        customer_id: str,
        status: str,
    ) -> Dict[str, Any]:
        """Validates and standardizes order attributes."""
        if not order_id or not str(order_id).strip():
            raise ValueError("Order ID must be a non-empty string.")

        if not item_name or not str(item_name).strip():
            raise ValueError("Item name cannot be blank.")

        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer greater than zero.")

        if not customer_id or not str(customer_id).strip():
            raise ValueError("Customer ID must be a non-empty string.")

        normalized_status = str(status).strip().lower()
        if normalized_status not in self.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Permitted statuses: {', '.join(sorted(self.ALLOWED_STATUSES))}."
            )

        return {
            "order_id": str(order_id).strip(),
            "item_name": str(item_name).strip(),
            "quantity": quantity,
            "customer_id": str(customer_id).strip(),
            "status": normalized_status,
        }

    def add_order(
        self,
        order_id: str,
        item_name: str,
        quantity: int,
        customer_id: str,
        status: str = "pending",
    ) -> Dict[str, Any]:
        """
        Registers a new order in the tracking system.

        :raises ValueError: If input parameters are invalid or order ID already exists.
        :return: Created order record.
        """
        validated_order = self._validate_order_payload(
            order_id=order_id,
            item_name=item_name,
            quantity=quantity,
            customer_id=customer_id,
            status=status,
        )

        # Ensure uniqueness of the order ID
        existing = self.storage.get_order(validated_order["order_id"])
        if existing:
            raise ValueError(f"Order with ID '{validated_order['order_id']}' already exists.")

        self.storage.save_order(validated_order["order_id"], validated_order)
        return validated_order.copy()

    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an order by its unique identifier.

        :param order_id: Unique order ID.
        :return: Order details dictionary or None if not found.
        """
        if not order_id or not str(order_id).strip():
            return None

        order = self.storage.get_order(str(order_id).strip())
        return order.copy() if order else None

    def update_order_status(self, order_id: str, new_status: str) -> Dict[str, Any]:
        """
        Updates the fulfillment status of an existing order.

        :param order_id: Unique order identifier.
        :param new_status: Target status string.
        :raises ValueError: If order does not exist or status is unrecognized.
        :return: Updated order dictionary.
        """
        if not order_id or not str(order_id).strip():
            raise ValueError("A valid order ID must be provided.")

        clean_id = str(order_id).strip()
        current_record = self.storage.get_order(clean_id)
        if not current_record:
            raise ValueError(f"Order with ID '{clean_id}' does not exist.")

        normalized_status = str(new_status).strip().lower()
        if normalized_status not in self.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status '{new_status}'. Permitted statuses: {', '.join(sorted(self.ALLOWED_STATUSES))}."
            )

        updated_record = current_record.copy()
        updated_record["status"] = normalized_status
        self.storage.save_order(clean_id, updated_record)
        return updated_record

    def list_all_orders(self) -> List[Dict[str, Any]]:
        """
        Lists all recorded orders across all statuses.

        :return: List of order dictionaries.
        """
        records = self.storage.get_all_orders()
        if isinstance(records, dict):
            return [order.copy() for order in records.values()]
        elif isinstance(records, list):
            return [order.copy() for order in records]
        return []

    def list_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Filters orders by a specific fulfillment status.

        :param status: Filter criterion status.
        :return: Filtered list of order dictionaries.
        """
        if not status or not str(status).strip():
            return self.list_all_orders()

        target = str(status).strip().lower()
        all_orders = self.list_all_orders()
        return [order for order in all_orders if order.get("status", "").lower() == target]
