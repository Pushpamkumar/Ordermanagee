"""
Unit Test Suite for the OrderTracker Domain Service

Validates domain rules, lifecycle transitions, edge cases, and storage interactions
using isolated mock adapters following Test-Driven Development (TDD).
"""

from unittest.mock import Mock
import pytest
from ..order_tracker import OrderTracker


# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    Simulates storage behaviors without depending on disk or live services.
    """
    mock = Mock()
    mock.get_order.return_value = None
    mock.get_all_orders.return_value = {}
    return mock


@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage fixture.
    """
    return OrderTracker(mock_storage)


# --- Unit Tests ---

def test_initialization_requires_valid_storage_interface():
    """Verifies that OrderTracker enforces storage contract compliance."""
    invalid_storage = object()
    with pytest.raises(TypeError, match="Storage adapter must provide a callable"):
        OrderTracker(invalid_storage)


def test_add_order_successfully(order_tracker, mock_storage):
    """Tests creating a basic order with default 'pending' status."""
    created = order_tracker.add_order(
        order_id="ORD-101",
        item_name="Mechanical Keyboard",
        quantity=2,
        customer_id="CUST-88",
    )

    mock_storage.save_order.assert_called_once_with(
        "ORD-101",
        {
            "order_id": "ORD-101",
            "item_name": "Mechanical Keyboard",
            "quantity": 2,
            "customer_id": "CUST-88",
            "status": "pending",
        },
    )
    assert created["order_id"] == "ORD-101"
    assert created["status"] == "pending"


def test_add_order_with_custom_status(order_tracker, mock_storage):
    """Tests adding an order with an explicitly specified valid status."""
    created = order_tracker.add_order(
        order_id="ORD-102",
        item_name="Ergonomic Mouse",
        quantity=1,
        customer_id="CUST-99",
        status="processing",
    )

    mock_storage.save_order.assert_called_once()
    assert created["status"] == "processing"


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Ensures duplicate order registration raises a ValueError with informative message."""
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order(
            order_id="ORD_EXISTING",
            item_name="Smart Monitor",
            quantity=1,
            customer_id="CUST-001",
        )


@pytest.mark.parametrize(
    "order_id,item_name,qty,cust_id,status,err_match",
    [
        ("", "Monitor", 1, "C1", "pending", "Order ID must be a non-empty string"),
        ("ORD1", "", 1, "C1", "pending", "Item name cannot be blank"),
        ("ORD1", "Monitor", 0, "C1", "pending", "Quantity must be a positive integer"),
        ("ORD1", "Monitor", -5, "C1", "pending", "Quantity must be a positive integer"),
        ("ORD1", "Monitor", 1, "", "pending", "Customer ID must be a non-empty string"),
        ("ORD1", "Monitor", 1, "C1", "dispatched_fake", "Invalid status"),
    ],
)
def test_add_order_input_validation(
    order_tracker, order_id, item_name, qty, cust_id, status, err_match
):
    """Verifies that invalid payloads are caught by domain validation."""
    with pytest.raises(ValueError, match=err_match):
        order_tracker.add_order(
            order_id=order_id,
            item_name=item_name,
            quantity=qty,
            customer_id=cust_id,
            status=status,
        )


def test_get_order_by_id_found(order_tracker, mock_storage):
    """Verifies fetching an existing order by its identifier."""
    sample_order = {
        "order_id": "ORD-500",
        "item_name": "USB-C Hub",
        "quantity": 3,
        "customer_id": "CUST-42",
        "status": "pending",
    }
    mock_storage.get_order.return_value = sample_order

    result = order_tracker.get_order_by_id("ORD-500")
    mock_storage.get_order.assert_called_once_with("ORD-500")
    assert result == sample_order


def test_get_order_by_id_not_found(order_tracker, mock_storage):
    """Verifies None is returned when an order does not exist."""
    mock_storage.get_order.return_value = None

    result = order_tracker.get_order_by_id("NONEXISTENT-ID")
    mock_storage.get_order.assert_called_once_with("NONEXISTENT-ID")
    assert result is None


def test_get_order_by_id_empty_input(order_tracker, mock_storage):
    """Verifies that blank order ID returns None without querying storage."""
    assert order_tracker.get_order_by_id("") is None
    mock_storage.get_order.assert_not_called()


def test_update_order_status_success(order_tracker, mock_storage):
    """Verifies status progression from pending to shipped."""
    existing_record = {
        "order_id": "ORD-700",
        "item_name": "Webcam",
        "quantity": 1,
        "customer_id": "CUST-10",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing_record

    updated = order_tracker.update_order_status("ORD-700", "shipped")
    assert updated["status"] == "shipped"
    mock_storage.save_order.assert_called_once_with(
        "ORD-700",
        {
            "order_id": "ORD-700",
            "item_name": "Webcam",
            "quantity": 1,
            "customer_id": "CUST-10",
            "status": "shipped",
        },
    )


def test_update_order_status_non_existent(order_tracker, mock_storage):
    """Verifies updating an unrecorded order raises a descriptive ValueError."""
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError, match="Order with ID 'MISSING-ORD' does not exist."):
        order_tracker.update_order_status("MISSING-ORD", "shipped")


def test_update_order_status_invalid_status(order_tracker, mock_storage):
    """Verifies updating with an unsupported status raises a ValueError."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD-800",
        "item_name": "Desk Lamp",
        "quantity": 1,
        "customer_id": "CUST-20",
        "status": "pending",
    }

    with pytest.raises(ValueError, match="Invalid status 'in_outer_space'"):
        order_tracker.update_order_status("ORD-800", "in_outer_space")


def test_list_all_orders_empty(order_tracker, mock_storage):
    """Verifies listing returns an empty list when repository is empty."""
    mock_storage.get_all_orders.return_value = {}
    assert order_tracker.list_all_orders() == []


def test_list_all_orders_with_records(order_tracker, mock_storage):
    """Verifies listing retrieves all stored records."""
    mock_storage.get_all_orders.return_value = {
        "O1": {"order_id": "O1", "item_name": "Item 1", "quantity": 1, "customer_id": "C1", "status": "pending"},
        "O2": {"order_id": "O2", "item_name": "Item 2", "quantity": 2, "customer_id": "C2", "status": "shipped"},
    }

    orders = order_tracker.list_all_orders()
    assert len(orders) == 2
    order_ids = {o["order_id"] for o in orders}
    assert order_ids == {"O1", "O2"}


def test_list_orders_by_status_filtering(order_tracker, mock_storage):
    """Verifies filtering orders by a specific status string."""
    mock_storage.get_all_orders.return_value = {
        "O1": {"order_id": "O1", "status": "pending"},
        "O2": {"order_id": "O2", "status": "shipped"},
        "O3": {"order_id": "O3", "status": "pending"},
        "O4": {"order_id": "O4", "status": "delivered"},
    }

    pending_orders = order_tracker.list_orders_by_status("pending")
    assert len(pending_orders) == 2
    assert all(o["status"] == "pending" for o in pending_orders)

    shipped_orders = order_tracker.list_orders_by_status("shipped")
    assert len(shipped_orders) == 1
    assert shipped_orders[0]["order_id"] == "O2"


def test_list_orders_by_status_no_match(order_tracker, mock_storage):
    """Verifies filtering by status returns empty list when no orders match."""
    mock_storage.get_all_orders.return_value = {
        "O1": {"order_id": "O1", "status": "pending"}
    }
    assert order_tracker.list_orders_by_status("cancelled") == []
