async function fetchData() {
    try {
        console.log("Fetching data...");
        const response = await fetch('bandwidth_data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Fetched data:", data);
        return data;
    } catch (error) {
        console.error("Could not fetch data:", error);
        return [];
    }
}

function createChart(data, index) {
    const limit = data.monthly_bw_limit_b / 1e9;
    const usage = data.bw_counter_b / 1e9;
    const resetDay = data.bw_reset_day_of_month;
    const name = data.name;

    const canvas = document.createElement('canvas');
    canvas.id = `chart-${index}`;
    canvas.style.width = '300px';
    canvas.style.height = '300px';
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
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${name} - Reset Day: ${resetDay}`
                }
            }
        }
    });
}

async function init() {
    const allData = await fetchData();
    console.log("Fetched data:", allData);
    if (allData.length === 0) {
        document.getElementById('charts-container').innerHTML = '<p>No data available. Please check the console for errors.</p>';
        return;
    }
    for (let i = 0; i < allData.length; i++) {
        createChart(allData[i], i);
    }
}

init();