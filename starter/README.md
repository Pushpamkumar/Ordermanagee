# OrderFlow System Core Package

This directory contains the core application package for the **OrderFlow** Order Management System, structured into decoupled backend services, testing harnesses, and a responsive frontend dashboard.

## Module Organization

```
starter/
├── backend/
│   ├── __init__.py               # Backend package initialisation
│   ├── app.py                    # Flask HTTP API & static asset delivery
│   ├── in_memory_storage.py      # Thread-safe in-memory storage adapter
│   ├── order_tracker.py          # Core domain logic & lifecycle rules
│   ├── requirements.txt          # Python dependencies (Flask, pytest)
│   └── tests/
│       ├── __init__.py           # Test package initialisation
│       ├── test_api.py           # REST API integration test suite
│       └── test_order_tracker.py # Domain unit tests with mock fixtures
├── frontend/
│   ├── css/
│   │   └── style.css             # Modern custom typography and status pill styling
│   ├── index.html                # Responsive operations single-page dashboard
│   └── js/
│       └── script.js             # Async client controller and live metric tracking
├── pytest.ini                    # Test runner configuration
└── README.md                     # Directory reference guide
```

## Quick Verification

Run all test suites from this directory:

```bash
pytest -v
```

Start the application server:

```bash
python -m backend.app
```
