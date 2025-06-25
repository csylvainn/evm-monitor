"""
Template pour l'activité - Version corrigée
web/templates/activity.py
"""

from .base import BASE_TEMPLATE

# Template pour l'activité - PROBLÈME RÉSOLU: extra_styles et scripts séparés
ACTIVITY_TEMPLATE = BASE_TEMPLATE.replace(
    '{% block content %}{% endblock %}',
    '''{% block content %}
    <!-- Overview cards -->
    <div class="overview-grid">
        <div class="overview-card">
            <h3>📅 Days Tracked</h3>
            <div class="value">{{ overview.total_days }}</div>
        </div>
        <div class="overview-card">
            <h3>🔄 Activities</h3>
            <div class="value">{{ "{:,}".format(overview.total_wallet_activities) }}</div>
        </div>
        <div class="overview-card">
            <h3>📊 Transactions</h3>
            <div class="value">{{ "{:,}".format(overview.total_transactions) }}</div>
        </div>
        <div class="overview-card">
            <h3>📈 Avg/Slot</h3>
            <div class="value">{{ overview.avg_wallets_per_slot }}</div>
        </div>
        <div class="overview-card">
            <h3>🚀 Peak</h3>
            <div class="value">{{ overview.max_wallets_per_slot }}</div>
        </div>
    </div>
    
    <!-- Controls -->
    <div class="controls">
        <label for="dateSelect" style="font-weight: 600;">📅 Select Date:</label>
        <select id="dateSelect" class="form-select" onchange="changeDateChart()">
            {% if not available_dates %}
                <option value="">No data available</option>
            {% else %}
                {% for date in available_dates %}
                    <option value="{{ date }}" {% if date == selected_date %}selected{% endif %}>
                        {{ date }}
                    </option>
                {% endfor %}
            {% endif %}
        </select>
        <span style="color: var(--text-muted); font-size: 14px;">
            📊 5-minute intervals
        </span>
    </div>
    
    <!-- Chart -->
    {% if stats_data %}
    <div class="chart-container">
        <h3>📊 Activity for {{ selected_date }}</h3>
        <canvas id="activityChart" height="100"></canvas>
    </div>
    {% else %}
    <div class="no-data">
        {% if available_dates %}
            <h3>🚫 No data for selected date</h3>
            <p>Please select a different date from the dropdown above.</p>
        {% else %}
            <h3>📊 No activity data available yet</h3>
            <p>Activity statistics will appear here once monitoring starts.</p>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Daily summary -->
    {% if daily_summary %}
    <div class="chart-container">
        <h3>📋 Recent Days Summary</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
            {% for day in daily_summary %}
            <div style="background: var(--bg-tertiary); padding: 16px; border-radius: 8px; border-left: 4px solid var(--accent-blue);">
                <h4 style="margin: 0 0 8px 0;">{{ day.date_formatted }}</h4>
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary);">
                    <span><strong>{{ "{:,}".format(day.total_wallets) }}</strong> activities</span>
                    <span><strong>{{ "{:,}".format(day.total_transactions) }}</strong> txs</span>
                    <span>Peak: <strong>{{ day.peak_wallets }}</strong></span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
{% endblock %}'''
).replace(
    '{% block scripts %}{% endblock %}',
    '''{% block scripts %}
<!-- Chart.js CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
<script>
    const chartData = {{ stats_data_json | safe }};
    let activityChart = null;
    
    function initChart() {
        if (!chartData || chartData.length === 0) return;
        
        const ctx = document.getElementById('activityChart').getContext('2d');
        if (activityChart) activityChart.destroy();
        
        const labels = chartData.map(item => item.time_slot);
        const walletsData = chartData.map(item => item.active_wallets);
        const transactionsData = chartData.map(item => item.total_transactions);
        
        activityChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Active Wallets',
                    data: walletsData,
                    backgroundColor: 'rgba(88, 166, 255, 0.6)',
                    borderColor: '#58a6ff',
                    borderWidth: 1,
                    yAxisID: 'y'
                }, {
                    label: 'Transactions',
                    data: transactionsData,
                    type: 'line',
                    backgroundColor: 'rgba(63, 185, 80, 0.1)',
                    borderColor: '#3fb950',
                    borderWidth: 2,
                    fill: false,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Time (5-minute slots)' },
                        grid: { color: 'rgba(48, 54, 61, 0.5)' }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Active Wallets' },
                        grid: { color: 'rgba(48, 54, 61, 0.5)' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Transactions' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }
    
    function changeDateChart() {
        const selectedDate = document.getElementById('dateSelect').value;
        if (selectedDate) {
            window.location.href = '/activity?date=' + selectedDate;
        }
    }
    
    document.addEventListener('DOMContentLoaded', initChart);
</script>
{% endblock %}'''
).replace('{% block refresh_url %}/{% endblock %}', '/activity')