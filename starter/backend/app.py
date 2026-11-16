"""
RESTful API Web Service for the Order Management Platform.
Exposes endpoints for creating, retrieving, filtering, and updating orders.
"""

from typing import Tuple, Any
from flask import Flask, jsonify, request, send_from_directory, Response
from backend.in_memory_storage import InMemoryStorage
from backend.order_tracker import OrderTracker

app = Flask(__name__, static_folder="../frontend")

# Service dependency graph
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.route("/")
def serve_index() -> Response:
    """Serves the single-page application dashboard entrypoint."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def serve_static(filename: str) -> Response:
    """Serves static assets (stylesheets, JavaScript scripts, icons)."""
    return send_from_directory(app.static_folder, filename)


@app.route("/api/orders", methods=["POST"])
def add_order_api() -> Tuple[Response, int]:
    """
    Endpoint: Registers a new order into the tracking repository.
    Expects JSON payload with: order_id, item_name, quantity, customer_id, (optional) status.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a valid JSON object."}), 400

    required_keys = ("order_id", "item_name", "quantity", "customer_id")
    missing_keys = [key for key in required_keys if key not in payload]
    if missing_keys:
        return (
            jsonify({"error": f"Missing required fields: {', '.join(missing_keys)}"}),
            400,
        )

    try:
        raw_quantity = payload.get("quantity")
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            return jsonify({"error": "Field 'quantity' must be an integer."}), 400

        status = payload.get("status", "pending")
        created_order = order_tracker.add_order(
            order_id=payload.get("order_id"),
            item_name=payload.get("item_name"),
            quantity=quantity,
            customer_id=payload.get("customer_id"),
            status=status,
        )
        return jsonify(created_order), 201

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Internal server error: {str(exc)}"}), 500


@app.route("/api/orders/<string:order_id>", methods=["GET"])
def get_order_api(order_id: str) -> Tuple[Response, int]:
    """
    Endpoint: Fetches details of a specific order by order_id.
    """
    record = order_tracker.get_order_by_id(order_id)
    if record is None:
        return jsonify({"error": f"Order with ID '{order_id}' was not found."}), 404

    return jsonify(record), 200


@app.route("/api/orders/<string:order_id>/status", methods=["PUT"])
def update_order_status_api(order_id: str) -> Tuple[Response, int]:
    """
    Endpoint: Updates the fulfillment lifecycle status of an existing order.
    Expects JSON payload: {"new_status": "..."}
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "new_status" not in payload:
        return jsonify({"error": "Payload must include 'new_status'."}), 400

    new_status = payload.get("new_status")
    if not new_status or not str(new_status).strip():
        return jsonify({"error": "The 'new_status' parameter cannot be blank."}), 400

    try:
        updated_order = order_tracker.update_order_status(order_id, str(new_status))
        return jsonify(updated_order), 200
    except ValueError as exc:
        error_message = str(exc)
        if "does not exist" in error_message or "not found" in error_message.lower():
            return jsonify({"error": error_message}), 404
        return jsonify({"error": error_message}), 400
    except Exception as exc:
        return jsonify({"error": f"Internal server error: {str(exc)}"}), 500


@app.route("/api/orders", methods=["GET"])
def list_orders_api() -> Tuple[Response, int]:
    """
    Endpoint: Lists all orders, optionally filtered by status query parameter.
    Example: GET /api/orders?status=pending
    """
    status_filter = request.args.get("status")
    if status_filter:
        orders = order_tracker.list_orders_by_status(status_filter)
    else:
        orders = order_tracker.list_all_orders()

    return jsonify(orders), 200


if __name__ == "__main__":
    # Start local development server
    app.run(host="0.0.0.0", port=5000, debug=True)
