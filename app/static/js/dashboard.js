// Progress Chart
const ctx = document.getElementById('progressChart');
if (ctx) {
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Scales', 'Arpeggios', 'Rhythm', 'Technique', 'Theory'],
            datasets: [{
                label: 'Skill Level',
                data: window.progressData || [],
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgb(99, 102, 241)',
                borderWidth: 2,
                pointBackgroundColor: 'rgb(99, 102, 241)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#a6adc8'
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.1)'
                    },
                    pointLabels: {
                        color: '#cdd6f4'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#cdd6f4'
                    }
                }
            }
        }
    });
}
