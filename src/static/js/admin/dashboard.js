/**
 * Admin Dashboard Charts & Interactions
 */
function initDashboardCharts(config) {
    const totalUsers = config.totalUsers || 0;

    // ── Growth Chart ──────────────────────────────
    const growthCtx = document.getElementById('growthChart').getContext('2d');
    const grad = growthCtx.createLinearGradient(0, 0, 0, 300);
    grad.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
    grad.addColorStop(1, 'rgba(59, 130, 246, 0)');

    const chartData = {
        "1":  { labels: ['00:00','04:00','08:00','12:00','16:00','20:00','Now'], data: [2,5,12,8,15,22,18] },
        "7":  { labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], data: [15,28,45,38,52,64,58] },
        "14": { labels: ['D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','Today'], data: [8,15,22,18,30,25,40,35,50,45,60,55,70,65] },
        "30": { labels: ['Week 1','Week 2','Week 3','Week 4'], data: [Math.round(totalUsers*0.2), Math.round(totalUsers*0.45), Math.round(totalUsers*0.7), totalUsers] }
    };

    const growthOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: '#1c1c1f', titleColor: '#fff', bodyColor: '#a1a1aa',
                borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1,
                padding: 12, cornerRadius: 10, displayColors: false,
            }
        },
        scales: {
            y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false }, ticks: { color: '#71717a', font: { size: 11 } }, border: { display: false } },
            x: { grid: { display: false }, ticks: { color: '#71717a', font: { size: 11 } }, border: { display: false } }
        }
    };

    let currentGrowthChart = new Chart(growthCtx, {
        type: 'line',
        data: {
            labels: chartData["14"].labels,
            datasets: [{ label: 'Registrations', data: chartData["14"].data, borderColor: '#3b82f6', backgroundColor: grad, borderWidth: 2.5, tension: 0.4, fill: true, pointRadius: 0, pointHoverRadius: 5, pointHoverBackgroundColor: '#3b82f6', pointHoverBorderColor: '#fff', pointHoverBorderWidth: 2 }]
        },
        options: growthOptions
    });

    window.updateChartRange = function(range, event) {
        if (event) event.preventDefault();
        document.querySelectorAll('.date-btn-mini').forEach(b => b.classList.remove('active'));
        const btn = event ? event.target : document.querySelector(`.date-btn-mini[data-range="${range}"]`);
        if (btn) btn.classList.add('active');
        currentGrowthChart.data.labels = chartData[range].labels;
        currentGrowthChart.data.datasets[0].data = chartData[range].data;
        currentGrowthChart.update('active');
    };

    // ── Plans Doughnut ────────────────────────────
    const plansCtx = document.getElementById('plansChart');
    if (plansCtx) {
        const planLabels = config.planLabels || [];
        const planData = config.planData || [];
        const planColors = ['#3b82f6','#10b981','#a78bfa','#fbbf24','#f472b6'];

        // Color legend dots
        document.querySelectorAll('.plan-dot').forEach((el, i) => {
            el.style.background = planColors[i % planColors.length];
        });

        new Chart(plansCtx, {
            type: 'doughnut',
            data: { labels: planLabels, datasets: [{ data: planData.length ? planData : [1], backgroundColor: planData.length ? planColors.slice(0, planData.length) : ['#3f3f46'], borderWidth: 0, cutout: '70%', spacing: 2 }] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { backgroundColor: '#1c1c1f', titleColor: '#fff', bodyColor: '#a1a1aa', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, padding: 10, cornerRadius: 8 } }
            }
        });
    }

    // ── Gender Doughnut ───────────────────────────
    const genderCtx = document.getElementById('genderChart');
    if (genderCtx) {
        const maleCount = config.maleCount || 0;
        const femaleCount = config.femaleCount || 0;
        const unknownCount = totalUsers - maleCount - femaleCount;
        const gData = [maleCount, femaleCount];
        const gColors = ['#3b82f6', '#ec4899'];
        if (unknownCount > 0) { gData.push(unknownCount); gColors.push('#3f3f46'); }

        new Chart(genderCtx, {
            type: 'doughnut',
            data: { labels: ['Male', 'Female', 'Unknown'], datasets: [{ data: gData.length && gData.some(v=>v>0) ? gData : [1], backgroundColor: gData.some(v=>v>0) ? gColors : ['#3f3f46'], borderWidth: 0, cutout: '75%', spacing: 2 }] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { backgroundColor: '#1c1c1f', titleColor: '#fff', bodyColor: '#a1a1aa', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, padding: 10, cornerRadius: 8 } }
            }
        });
    }
}
