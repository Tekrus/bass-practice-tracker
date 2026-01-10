// Fetch and display practice chart
fetch('/api/progress-data')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('practiceChart');
        if (ctx && data.daily_practice) {
            // Get last 14 days
            const labels = [];
            const values = [];
            const today = new Date();

            for (let i = 13; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                const dateStr = date.toISOString().split('T')[0];
                labels.push(date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }));
                values.push(data.daily_practice[dateStr] || 0);
            }

            if (window.Chart) {
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Minutes Practiced',
                            data: values,
                            backgroundColor: 'rgba(99, 102, 241, 0.7)',
                            borderColor: 'rgb(99, 102, 241)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: '#a6adc8' },
                                grid: { color: 'rgba(255,255,255,0.1)' }
                            },
                            x: {
                                ticks: { color: '#a6adc8' },
                                grid: { color: 'rgba(255,255,255,0.1)' }
                            }
                        },
                        plugins: {
                            legend: {
                                labels: { color: '#cdd6f4' }
                            }
                        }
                    }
                });
            }
        }
    });
