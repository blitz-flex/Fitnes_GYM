/**
 * Admin Statistics Charts & Interactions
 */
function initStatisticsCharts(config) {
    const chartDefaults = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: '#18181b',
                borderColor: 'rgba(255,255,255,0.1)',
                borderWidth: 1,
                titleColor: '#f4f4f5',
                bodyColor: '#a1a1aa',
                padding: 12,
                cornerRadius: 10,
                titleFont: { weight: '700', size: 13 },
                bodyFont: { size: 12 },
            }
        }
    };

    // --- Revenue & Bookings Area Chart ---
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        const ctx = revenueCtx.getContext('2d');
        const gradient1 = ctx.createLinearGradient(0, 0, 0, 300);
        gradient1.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
        gradient1.addColorStop(1, 'rgba(59, 130, 246, 0)');
        const gradient2 = ctx.createLinearGradient(0, 0, 0, 300);
        gradient2.addColorStop(0, 'rgba(16, 185, 129, 0.2)');
        gradient2.addColorStop(1, 'rgba(16, 185, 129, 0)');

        const currentRange = config.currentRange || 30;
        const days = [];
        for (let i = currentRange - 1; i >= 0; i--) {
            const d = new Date(); d.setDate(d.getDate() - i);
            days.push(d.toLocaleDateString('en', { month: 'short', day: 'numeric' }));
        }
        
        // Pad data if needed
        const finalBookingsData = new Array(currentRange).fill(0);
        const rawData = config.chartData || [];
        for(let i = 0; i < Math.min(rawData.length, currentRange); i++) {
            finalBookingsData[currentRange - 1 - i] = rawData[rawData.length - 1 - i] || 0;
        }

        const revenueData = Array.from({length: currentRange}, () => Math.floor(Math.random() * 600 + 200));

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: days,
                datasets: [{
                    label: 'Revenue ($)',
                    data: revenueData,
                    borderColor: '#3b82f6',
                    backgroundColor: gradient1,
                    fill: true, tension: 0.4, borderWidth: 2.5, pointRadius: 0, pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#3b82f6', pointHoverBorderColor: '#fff', pointHoverBorderWidth: 2,
                }, {
                    label: 'Bookings',
                    data: finalBookingsData,
                    borderColor: '#10b981',
                    backgroundColor: gradient2,
                    fill: true, tension: 0.4, borderWidth: 2.5, pointRadius: 0, pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#10b981', pointHoverBorderColor: '#fff', pointHoverBorderWidth: 2,
                }]
            },
            options: {
                ...chartDefaults,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false }, ticks: { color: '#71717a', font: { size: 11 }, padding: 8 }, border: { display: false } },
                    x: { grid: { display: false }, ticks: { color: '#71717a', font: { size: 11 }, maxTicksLimit: 8, padding: 8 }, border: { display: false } }
                }
            }
        });
    }

    // --- Peak Hours Bar Chart ---
    const peakCtx = document.getElementById('peakHoursChart');
    if (peakCtx) {
        const ctx = peakCtx.getContext('2d');
        const hours = ['6am','7am','8am','9am','10am','11am','12pm','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm'];
        const peakData = [5,12,25,30,18,10,8,6,9,14,22,35,40,32,20,10];
        const peakColors = peakData.map(v => {
            if (v >= 35) return '#ef4444';
            if (v >= 25) return '#f59e0b';
            if (v >= 15) return '#3b82f6';
            return 'rgba(255,255,255,0.08)';
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: hours,
                datasets: [{ data: peakData, backgroundColor: peakColors, borderRadius: 6, borderSkipped: false, barThickness: 14 }]
            },
            options: {
                ...chartDefaults,
                indexAxis: 'y',
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false }, ticks: { color: '#71717a', font: { size: 10 } }, border: { display: false } },
                    y: { grid: { display: false }, ticks: { color: '#a1a1aa', font: { size: 11, weight: '600' }, padding: 8 }, border: { display: false } }
                }
            }
        });
    }

    // --- Program Distribution Pie ---
    const pieCtx = document.getElementById('programPieChart');
    if (pieCtx) {
        const ctx = pieCtx.getContext('2d');
        const pieColors = ['#3b82f6', '#10b981', '#f59e0b', '#a78bfa', '#f472b6', '#60a5fa', '#fbbf24'];
        const programLabels = config.programLabels || [];
        const programData = config.programData || [];

        // Color the legend dots
        document.querySelectorAll('.legend-color').forEach((el, i) => {
            el.style.background = pieColors[i % pieColors.length];
        });

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: programLabels,
                datasets: [{ data: programData, backgroundColor: pieColors.slice(0, programData.length), borderWidth: 0, cutout: '72%', spacing: 3 }]
            },
            options: {
                ...chartDefaults,
                plugins: {
                    ...chartDefaults.plugins,
                    tooltip: {
                        ...chartDefaults.plugins.tooltip,
                        callbacks: {
                            label: function(ctx) {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = total > 0 ? Math.round(ctx.raw / total * 100) : 0;
                                return ` ${ctx.label}: ${ctx.raw} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // --- Date Filter Buttons ---
    document.querySelectorAll('.date-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const range = this.getAttribute('data-range');
            window.location.href = config.baseUrl + `?range=${range}`;
        });
    });
}
