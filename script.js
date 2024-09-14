async function fetchData() {
    const response = await fetch('bandwidth_data.json');
    return response.json();
}

function createChart(data, index) {
    const limit = data.monthly_bw_limit_b / 1e9;
    const usage = data.bw_counter_b / 1e9;
    const resetDay = data.bw_reset_day_of_month;

    const canvas = document.createElement('canvas');
    canvas.id = `chart-${index}`;
    document.getElementById('charts-container').appendChild(canvas);

    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: ['Used', 'Remaining'],
            datasets: [{
                data: [usage, limit - usage],
                backgroundColor: ['#FF6384', '#36A2EB']
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: `Service ${index + 1} - Reset Day: ${resetDay}`
            }
        }
    });
}

async function init() {
    const allData = await fetchData();
    for (let i = 0; i < allData.length; i++) {
        createChart(allData[i], i);
    }
}

init();