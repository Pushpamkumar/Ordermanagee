/**
 * OrderFlow Dashboard Client Controller
 * Handles user interactions, form submissions, and asynchronous API calls.
 */

document.addEventListener('DOMContentLoaded', () => {
    const messageContainer = document.getElementById('message-container');
    const addOrderForm = document.getElementById('add-order-form');
    const getOrderForm = document.getElementById('get-order-form');
    const singleOrderDetails = document.getElementById('single-order-details');
    const updateStatusForm = document.getElementById('update-status-form');
    const listAllOrdersBtn = document.getElementById('list-all-orders-btn');
    const filterStatusSelect = document.getElementById('filter-status');
    const ordersTableBody = document.getElementById('orders-table-body');

    // KPI Counters
    const statTotal = document.getElementById('stat-total');
    const statPending = document.getElementById('stat-pending');
    const statProcessing = document.getElementById('stat-processing');
    const statShipped = document.getElementById('stat-shipped');

    let notificationTimer = null;

    function showMessage(message, type) {
        if (notificationTimer) {
            clearTimeout(notificationTimer);
        }
        messageContainer.textContent = message;
        messageContainer.className = `message-box ${type === 'success' ? 'message-success' : 'message-error'}`;
        messageContainer.classList.remove('hidden');
        notificationTimer = setTimeout(() => {
            messageContainer.classList.add('hidden');
        }, 5000);
    }

    function getBadgeClass(status) {
        const s = (status || '').toLowerCase();
        if (s === 'pending') return 'badge-status badge-pending';
        if (s === 'processing') return 'badge-status badge-processing';
        if (s === 'shipped') return 'badge-status badge-shipped';
        if (s === 'delivered') return 'badge-status badge-delivered';
        if (s === 'cancelled') return 'badge-status badge-cancelled';
        return 'badge-status bg-slate-100 text-slate-700';
    }

    function updateMetricCards(orders) {
        if (!statTotal) return;
        statTotal.textContent = orders.length;
        statPending.textContent = orders.filter(o => (o.status || '').toLowerCase() === 'pending').length;
        statProcessing.textContent = orders.filter(o => (o.status || '').toLowerCase() === 'processing').length;
        statShipped.textContent = orders.filter(o => (o.status || '').toLowerCase() === 'shipped').length;
    }

    function renderOrdersTable(orders) {
        ordersTableBody.innerHTML = '';
        if (!orders || orders.length === 0) {
            ordersTableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-8 text-slate-400 font-medium text-sm">
                        No orders currently found matching the selected filter.
                    </td>
                </tr>
            `;
            return;
        }

        orders.forEach((order, index) => {
            const row = document.createElement('tr');
            row.className = index % 2 === 0 ? 'bg-white hover:bg-slate-50 transition-colors' : 'bg-slate-50/50 hover:bg-slate-100/60 transition-colors';
            
            const badgeClass = getBadgeClass(order.status);
            
            row.innerHTML = `
                <td class="py-3 px-4 font-mono font-bold text-slate-800 text-xs">${escapeHtml(order.order_id)}</td>
                <td class="py-3 px-4 font-medium text-slate-900">${escapeHtml(order.item_name)}</td>
                <td class="py-3 px-4 text-slate-600 font-semibold">${escapeHtml(String(order.quantity))}</td>
                <td class="py-3 px-4 font-mono text-slate-500 text-xs">${escapeHtml(order.customer_id)}</td>
                <td class="py-3 px-4"><span class="${badgeClass}">${escapeHtml(order.status || 'unknown')}</span></td>
            `;
            ordersTableBody.appendChild(row);
        });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    async function refreshTelemetry() {
        try {
            const res = await fetch('/api/orders');
            if (res.ok) {
                const allOrders = await res.json();
                updateMetricCards(allOrders);
            }
        } catch (_) {
            // Silently ignore telemetry refresh failure
        }
    }

    async function fetchAndRenderOrders(status = '') {
        try {
            const url = status ? `/api/orders?status=${encodeURIComponent(status)}` : '/api/orders';
            const response = await fetch(url);
            const orders = await response.json();
            if (!response.ok) {
                throw new Error(orders.error || 'Failed to retrieve order records.');
            }
            renderOrdersTable(orders);
            refreshTelemetry();
        } catch (error) {
            showMessage(`Error fetching orders: ${error.message}`, 'error');
            renderOrdersTable([]);
        }
    }

    // Submit new order
    addOrderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(addOrderForm);
        const orderData = Object.fromEntries(formData.entries());
        orderData.quantity = parseInt(orderData.quantity, 10);

        try {
            const response = await fetch('/api/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'Failed to create order.');
            }
            showMessage(`Order #${result.order_id} recorded successfully!`, 'success');
            addOrderForm.reset();
            fetchAndRenderOrders(filterStatusSelect.value);
        } catch (error) {
            showMessage(`Unable to register order: ${error.message}`, 'error');
        }
    });

    // Lookup single order
    getOrderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const orderId = document.getElementById('get-order-id').value.trim();
        singleOrderDetails.classList.add('hidden');

        if (!orderId) {
            showMessage('Please specify an Order ID.', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/orders/${encodeURIComponent(orderId)}`);
            const order = await response.json();
            if (!response.ok) {
                throw new Error(order.error || 'Order lookup failed.');
            }
            singleOrderDetails.querySelector('pre').textContent = JSON.stringify(order, null, 2);
            singleOrderDetails.classList.remove('hidden');
        } catch (error) {
            showMessage(`Lookup error: ${error.message}`, 'error');
        }
    });

    // Update status
    updateStatusForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const orderId = document.getElementById('update-order-id').value.trim();
        const newStatus = document.getElementById('update-new-status').value;

        if (!orderId || !newStatus) {
            showMessage('Both Order ID and New Status are required.', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/orders/${encodeURIComponent(orderId)}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_status: newStatus })
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'Status transition rejected.');
            }
            showMessage(`Order #${orderId} status changed to '${newStatus}'.`, 'success');
            updateStatusForm.reset();
            fetchAndRenderOrders(filterStatusSelect.value);
        } catch (error) {
            showMessage(`Status update error: ${error.message}`, 'error');
        }
    });

    // Filtering & Refresh
    listAllOrdersBtn.addEventListener('click', () => {
        filterStatusSelect.value = '';
        fetchAndRenderOrders();
    });

    filterStatusSelect.addEventListener('change', (e) => {
        fetchAndRenderOrders(e.target.value);
    });

    // Initial population
    fetchAndRenderOrders();
});
