# OrderFlow — Test-Driven Order Fulfillment & Lifecycle Management System

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/flask-3.1.2-lightgrey.svg)](https://palletsprojects.com/p/flask/)
[![Test Suite](https://img.shields.io/badge/pytest-26%20passed-brightgreen.svg)](https://pytest.org/)
[![Architecture](https://img.shields.io/badge/design-Clean%20TDD-orange.svg)](#architecture--design-patterns)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)

**OrderFlow** is a modular, high-reliability order tracking and fulfillment service engineered from the ground up using strict **Test-Driven Development (TDD)** and **Clean Architecture** patterns. It features an isolated domain core, thread-safe decoupled storage adapters, standard RESTful HTTP endpoints, and an interactive real-time management dashboard.

---

## Table of Contents

- [Key Highlights](#key-highlights)
- [Architecture & Design Patterns](#architecture--design-patterns)
- [System Architecture Flow](#system-architecture-flow)
- [REST API Specification](#rest-api-specification)
- [Project Directory Layout](#project-directory-layout)
- [Installation & Environment Setup](#installation--environment-setup)
- [Automated Testing (TDD Suite)](#automated-testing-tdd-suite)
- [Running the Application](#running-the-application)
- [Interactive Web Dashboard Tour](#interactive-web-dashboard-tour)

---

## Key Highlights

- **Test-Driven Development (TDD)**: Designed and hardened using a Red-Green-Refactor cycle with 100% test pass rates across 26 unit and integration test scenarios.
- **Dependency Inversion**: The business domain (`OrderTracker`) requires only an abstract storage contract, making it trivial to swap in-memory storage for PostgreSQL, MongoDB, or Redis.
- **Defensive Domain Validation**: Input sanitization, strict quantity constraints, duplicate prevention, and lifecycle state transition guards.
- **Thread-Safe Ephemeral Storage**: Concurrency-protected storage engine with re-entrant locking (`RLock`) and mutation shielding via defensive copies.
- **RESTful API Semantics**: Proper JSON envelopes, HTTP status codes (`201 Created`, `200 OK`, `400 Bad Request`, `404 Not Found`, `500 Internal Error`).
- **Modern Responsive Dashboard**: Real-time status cards, live inventory telemetry, status badges, and single-page CRUD workflow.

---

## Architecture & Design Patterns

The codebase is organized into four distinct decoupled tiers:

1. **Presentation Layer (Frontend)**:
   - Responsive UI powered by Tailwind CSS, modern typography, and modular vanilla JavaScript.
   - Live KPI counter telemetry, status filtering, and dynamic feedback messaging.
2. **Controller Layer (REST API)**:
   - Built on Flask, providing clean route handlers, payload validation, status code mapping, and structured error responses.
3. **Domain Layer (Business Logic)**:
   - Encapsulated within `OrderTracker`. Owns order validation, uniqueness enforcement, state transition logic, and domain queries.
4. **Data Access Layer (Storage Adapter)**:
   - `InMemoryStorage` implements thread-safe key-value persistence with copy-on-write semantics.

---

## System Architecture Flow

```mermaid
flowchart TD
    Client["Client Browser / REST Consumer"] -->|HTTP REST Requests| API["Flask REST Controller (app.py)"]
    API -->|Validates Payload & Invocations| Domain["Domain Service (OrderTracker)"]
    Domain -->|Storage Protocol (save / get / list)| Storage["Storage Adapter (InMemoryStorage)"]
    Storage -->|Thread-Safe In-Memory Store| Dict[("Memory Dictionary & RLock")]

    subgraph Test Suites
        UnitTests["Unit Tests (test_order_tracker.py)"] -->|Mock Storage Fixtures| Domain
        IntegrationTests["Integration Tests (test_api.py)"] -->|Test Client Requests| API
    end
```

---

## REST API Specification

### Base URL
All API endpoints are mounted under `/api`.

| Method | Endpoint | Description | Request Body | Success Status |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/orders` | Create and register a new order | JSON order object | `201 Created` |
| `GET` | `/api/orders` | Retrieve all orders or filter by status | Query: `?status=<status>` | `200 OK` |
| `GET` | `/api/orders/<order_id>` | Fetch specific order details | _None_ | `200 OK` / `404` |
| `PUT` | `/api/orders/<order_id>/status` | Update fulfillment state | `{"new_status": "..."}` | `200 OK` / `404` |

#### 1. Create Order
**`POST /api/orders`**
```json
{
  "order_id": "ORD-1001",
  "item_name": "4K Ultra Monitor",
  "quantity": 2,
  "customer_id": "CUST-901",
  "status": "pending"
}
```
**Response (`201 Created`):**
```json
{
  "order_id": "ORD-1001",
  "item_name": "4K Ultra Monitor",
  "quantity": 2,
  "customer_id": "CUST-901",
  "status": "pending"
}
```

#### 2. Get Order by Identifier
**`GET /api/orders/ORD-1001`**
**Response (`200 OK`):**
```json
{
  "order_id": "ORD-1001",
  "item_name": "4K Ultra Monitor",
  "quantity": 2,
  "customer_id": "CUST-901",
  "status": "pending"
}
```

#### 3. Update Order Status
**`PUT /api/orders/ORD-1001/status`**
```json
{
  "new_status": "shipped"
}
```
**Response (`200 OK`):**
```json
{
  "order_id": "ORD-1001",
  "item_name": "4K Ultra Monitor",
  "quantity": 2,
  "customer_id": "CUST-901",
  "status": "shipped"
}
```

#### 4. Filter Orders by Status
**`GET /api/orders?status=shipped`**
**Response (`200 OK`):**
```json
[
  {
    "order_id": "ORD-1001",
    "item_name": "4K Ultra Monitor",
    "quantity": 2,
    "customer_id": "CUST-901",
    "status": "shipped"
  }
]
```

---

## Project Directory Layout

```
OrderManage/
├── README.md                           # Master system documentation
├── .gitignore                          # Git ignore definitions
└── starter/
    ├── pytest.ini                      # Pytest discovery configuration
    ├── README.md                       # Core package technical overview
    ├── backend/
    │   ├── __init__.py                 # Backend package module
    │   ├── app.py                      # Flask REST API & static file serving
    │   ├── in_memory_storage.py        # Thread-safe in-memory storage adapter
    │   ├── order_tracker.py            # Domain service & business validations
    │   ├── requirements.txt            # Dependency manifest
    │   └── tests/
    │       ├── __init__.py             # Test package module
    │       ├── test_api.py             # Integration test suite for REST routes
    │       └── test_order_tracker.py   # Unit test suite for domain logic
    └── frontend/
        ├── css/
        │   └── style.css               # UI typography, badge styling & layout
        ├── index.html                  # Responsive single-page dashboard
        └── js/
            └── script.js               # Client controller & state coordinator
```

---

## Installation & Environment Setup

### Prerequisites
- Python 3.9+ (Python 3.11 recommended)
- `pip` package manager

### 1. Clone & Navigate to Repository
```bash
git clone <repository-url>
cd OrderManage/starter
```

### 2. Create and Activate Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

---

## Automated Testing (TDD Suite)

All 26 automated tests can be executed using `pytest`.

```bash
# From within the starter/ directory:
pytest -v
```

### Test Suite Summary:
- **Unit Tests (`test_order_tracker.py`)**:
  - `test_initialization_requires_valid_storage_interface`
  - `test_add_order_successfully`
  - `test_add_order_with_custom_status`
  - `test_add_order_raises_error_if_exists`
  - `test_add_order_input_validation` (parametrized for empty ID, blank item, zero quantity, negative quantity, blank customer, invalid status)
  - `test_get_order_by_id_found` & `test_get_order_by_id_not_found` & `test_get_order_by_id_empty_input`
  - `test_update_order_status_success` & `test_update_order_status_non_existent` & `test_update_order_status_invalid_status`
  - `test_list_all_orders_empty` & `test_list_all_orders_with_records`
  - `test_list_orders_by_status_filtering` & `test_list_orders_by_status_no_match`
- **Integration Tests (`test_api.py`)**:
  - `test_add_order_api_success`
  - `test_get_order_api_success`
  - `test_get_order_api_not_found`
  - `test_update_order_status_api_success`
  - `test_list_all_orders_api_with_data`
  - `test_list_orders_by_status_api_matching`

---

## Running the Application

To launch the Flask application server:

```bash
# Execute from within the starter/ directory:
python -m backend.app
```

The server initializes on port `5000`:
- **Web Dashboard**: Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in any modern web browser.
- **REST API Base**: [http://127.0.0.1:5000/api/orders](http://127.0.0.1:5000/api/orders)

---

## Interactive Web Dashboard Tour

1. **KPI Metric Telemetry**:
   - The top row instantly reflects count totals for **Total Orders**, **Pending**, **Processing**, and **Shipped**.
2. **Order Placement**:
   - Fill in Order ID, Item Description, Quantity, and Customer ID. Click **+ Submit Order** to post to `/api/orders`.
3. **Real-Time Status Progression**:
   - Change order state (e.g. from `pending` to `shipped`) directly via the status update form.
4. **Order Search / Inspection**:
   - Enter an Order ID to fetch and view its raw JSON structure in the inspector window.
5. **Inventory Filter**:
   - Filter records dynamically using the status dropdown or click **Refresh** to reload the complete list.
