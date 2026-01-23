document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const tabs = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // Global Chart Instances
    let requestsChartInstance = null;
    let endpointsChartInstance = null;

    // Dashboard Data Fetching
    async function loadDashboardData() {
        try {
            // Parallel Fetching
            const [errorRate, avgTime, reqPerMin, mostUsed] = await Promise.all([
                fetch('/analytics/error-rate').then(res => res.json()),
                fetch('/analytics/avg-response-time').then(res => res.json()),
                fetch('/analytics/requests-per-minute').then(res => res.json()),
                fetch('/analytics/most-used').then(res => res.json())
            ]);

            // Update DOM
            document.getElementById('error-rate').textContent = `${errorRate.error_rate_percent.toFixed(1)}%`;
            document.getElementById('avg-response-time').textContent = `${avgTime.avg_response_time_ms.toFixed(0)}ms`;

            // Render Charts
            renderRequestsChart(reqPerMin);
            renderEndpointsChart(mostUsed);
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    // Chart Rendering
    function renderRequestsChart(data) {
        const ctx = document.getElementById('requestsChart').getContext('2d');
        
        if (requestsChartInstance) {
            requestsChartInstance.destroy();
        }

        requestsChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.minute),
                datasets: [{
                    label: 'Requests',
                    data: data.map(d => d.count),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
                }
            }
        });
    }

    function renderEndpointsChart(data) {
        const ctx = document.getElementById('endpointsChart').getContext('2d');
        
        if (endpointsChartInstance) {
            endpointsChartInstance.destroy();
        }

        endpointsChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.endpoint),
                datasets: [{
                    label: 'Calculated Hits',
                    data: data.map(d => d.count),
                    backgroundColor: '#10b981',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
                }
            }
        });
    }

    // Items Manager
    const itemsList = document.getElementById('items-list');
    const modal = document.getElementById('item-modal');
    const openModalBtn = document.getElementById('create-item-btn');
    const closeModalBtn = document.querySelector('.close-modal');
    const createItemForm = document.getElementById('create-item-form');

    // Modal Logic
    openModalBtn.onclick = () => modal.classList.add('active');
    closeModalBtn.onclick = () => modal.classList.remove('active');
    window.onclick = (e) => { if (e.target === modal) modal.classList.remove('active'); };

    async function loadItems() {
        try {
            const res = await fetch('/items/');
            const items = await res.json();
            
            itemsList.innerHTML = items.map(item => `
                <tr>
                    <td>${item.name}</td>
                    <td>$${item.price.toFixed(2)}</td>
                    <td><span class="status-badge ${item.in_stock ? 'status-in-stock' : 'status-out-stock'}">
                        ${item.in_stock ? 'In Stock' : 'Out of Stock'}
                    </span></td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error loading items:', error);
        }
    }

    createItemForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const newItem = {
            name: document.getElementById('item-name').value,
            price: parseFloat(document.getElementById('item-price').value),
            in_stock: document.getElementById('item-stock').checked
        };

        try {
            const res = await fetch('/items/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newItem)
            });

            if (res.ok) {
                modal.classList.remove('active');
                createItemForm.reset();
                loadItems(); // Refresh list
            } else {
                alert('Failed to create item');
            }
        } catch (error) {
            console.error('Error creating item:', error);
        }
    });

    // Initial Load & Auto-Refresh
    loadDashboardData();
    loadItems();
    
    // Auto-refresh using setInterval (5000ms)
    setInterval(() => {
        loadDashboardData();
        // Option to refresh items too, or keep it manual? 
        // Refreshing items ensures stock status is current.
        loadItems(); 
    }, 5000);
});
