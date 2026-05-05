const backbtn = document.getElementById("previous")
const forwardbtn = document.getElementById("next")
const cards = document.querySelectorAll(".recentCard")

let currentindex = 0

if (forwardbtn && backbtn && cards.length > 0) {
    forwardbtn.addEventListener("click", function () {
        if (currentindex < cards.length - 1) {
            currentindex++
            carousel(currentindex)
        }
    })

    backbtn.addEventListener("click", function () {
        if (currentindex > 0) {
            currentindex--
            carousel(currentindex)
        }
    })
}

function carousel(index) {
    cards.forEach(card => card.style.display = "none")
    cards[index].style.display = "block"
}

// ---------------- CHART ----------------

const workoutbtn = document.getElementById("workouts")
const timebtn = document.getElementById("time")
const distancebtn = document.getElementById("distance")
const racesbtn = document.getElementById("races")
const favoritebtn = document.getElementById("favorite")
const mycanvas = document.getElementById("chart")
const chartArea = document.getElementById("chartArea")

let liveData = {}

if (chartArea && chartArea.dataset.chart) {
    try {
        liveData = JSON.parse(chartArea.dataset.chart)
    } catch (e) {
        console.error("Failed to parse chart data:", e)
    }
}

let currenttype = null
let currentchart = null

// button listeners
workoutbtn?.addEventListener("click", () => showchart("workouts"))
timebtn?.addEventListener("click", () => showchart("time"))
distancebtn?.addEventListener("click", () => showchart("distance"))
racesbtn?.addEventListener("click", () => showchart("races"))
favoritebtn?.addEventListener("click", () => showchart("favorite"))

function showchart(type) {
    if (!mycanvas) return

    // toggle off if same chart
    if (currenttype === type && currentchart) {
        currentchart.destroy()
        currentchart = null
        currenttype = null
        chartArea.classList.remove("active")
        return
    }

    if (currentchart) currentchart.destroy()

    let chartData = {}
    let chartColours = "#f5c518"
    let borderColours = "#f5c518"

    // ---------------- DATA SELECTION ----------------

    if (type === "workouts") {
        chartData = liveData.workouts ? {
            labels: liveData.workouts.labels,
            data: liveData.workouts.data,
            label: "Workouts This Week",
            type: "bar"
        } : {}
    }

    else if (type === "time") {
        chartData = liveData.time ? {
            labels: liveData.time.labels,
            data: liveData.time.data,
            label: "Minutes Spent This Week",
            type: "bar"
        } : {}

        chartColours = "#36a2eb"
        borderColours = "#36a2eb"
    }

    else if (type === "distance") {
        chartData = liveData.distance ? {
            labels: liveData.distance.labels,
            data: liveData.distance.data,
            label: "Distance This Week (km)",
            type: "line"
        } : {}

        chartColours = "#2ecc71"
        borderColours = "#2ecc71"
    }

    else if (type === "races") {
        chartData = liveData.races ? {
            labels: liveData.races.labels,
            data: liveData.races.data,
            label: "Races Completed",
            type: "bar"
        } : {}

        chartColours = "#ff9f40"
        borderColours = "#ff9f40"
    }

    else if (type === "favorite") {
        chartData = liveData.favorite ? {
            labels: liveData.favorite.labels,
            data: liveData.favorite.data,
            label: "Exercise Breakdown",
            type: "doughnut"
        } : {}

        const colours = [
            "#f5c518", "#3498db", "#2ecc71", "#e74c3c",
            "#9b59b6", "#ff9f40", "#1abc9c", "#34495e"
        ]

        chartColours = colours.slice(0, liveData.favorite ? liveData.favorite.labels.length : 0)
        borderColours = Array(chartColours.length).fill("#0a0a0a")
    }

    if (!chartData.type) {
        console.warn("No data available for chart type:", type)
        return
    }

    // ---------------- CREATE CHART ----------------

    currentchart = new Chart(mycanvas, {
        type: chartData.type,
        data: {
            labels: chartData.labels,
            datasets: [{
                label: chartData.label,
                data: chartData.data,
                backgroundColor: chartColours,
                borderColor: borderColours,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: "#ffffff" }
                }
            },
            scales: chartData.type === "doughnut" ? {} : {
                x: {
                    ticks: { color: "#ffffff" },
                    grid: { color: "#222222" }
                },
                y: {
                    ticks: { color: "#ffffff", stepSize: 1 },
                    grid: { color: "#222222" }
                }
            }
        }
    })

    chartArea.classList.add("active")
    currenttype = type
}
