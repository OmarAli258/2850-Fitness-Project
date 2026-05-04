const backbtn = document.getElementById("previous")
const forwardbtn = document.getElementById("next")
const cards = document.querySelectorAll(".recentCard")

let currentindex = 0

if (forwardbtn && backbtn && cards.length > 0) {
    forwardbtn.addEventListener("click", function () {
        if (currentindex < cards.length - 1) {
            currentindex = currentindex + 1
            carousel(currentindex)
        }
    })

    backbtn.addEventListener("click", function () {
        if (currentindex > 0) {
            currentindex = currentindex - 1
            carousel(currentindex)
        }
    })
}

function carousel(index) {
    cards.forEach(function (card) {
        card.style.display = "none"
    })

    cards[index].style.display = "block"
}


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

if (workoutbtn) {
    workoutbtn.addEventListener("click", function () {
        showchart("workouts")
    })
}

if (timebtn) {
    timebtn.addEventListener("click", function () {
        showchart("time")
    })
}

if (distancebtn) {
    distancebtn.addEventListener("click", function () {
        showchart("distance")
    })
}

if (racesbtn) {
    racesbtn.addEventListener("click", function () {
        showchart("races")
    })
}

if (favoritebtn) {
    favoritebtn.addEventListener("click", function () {
        showchart("favorite")
    })
}

function showchart(type) {
    if (!mycanvas) {
        return
    }

    if (currenttype == type && currentchart != null) {
        currentchart.destroy()
        currentchart = null
        currenttype = null
        document.querySelector("#chartArea").classList.remove("active")
        return
    }

    if (currentchart != null) {
        currentchart.destroy()
    }

    let chartData = {}
    let chartColours = "#f5c518"
    let borderColours = "#f5c518"

    if (type === "workouts" && liveData.workouts) {
        chartData = {
            labels: liveData.workouts.labels,
            data: liveData.workouts.data,
            label: "Workouts This Week",
            type: "bar"
        }
    }

    if (type === "time" && liveData.time) {
        chartData = {
            labels: liveData.time.labels,
            data: liveData.time.data,
            label: "Minutes Spent This Week",
            type: "bar"
        }
        chartColours = "#36a2eb"
        borderColours = "#36a2eb"
    }

    if (type === "distance" && liveData.distance) {
        chartData = {
            labels: liveData.distance.labels,
            data: liveData.distance.data,
            label: "Distance This Week (km)",
            type: "line"
        }
        chartColours = "#2ecc71"
        borderColours = "#2ecc71"
    }

    if (type === "races" && liveData.races) {
        chartData = {
            labels: liveData.races.labels,
            data: liveData.races.data,
            label: "Races Completed",
            type: "bar"
        }
        chartColours = "#ff9f40"
        borderColours = "#ff9f40"
    }

    if (type === "favorite" && liveData.favorite) {
        const doughnutColors = [
            "#f5c518", "#3498db", "#2ecc71", "#e74c3c", "#9b59b6", "#ff9f40",
            "#1abc9c", "#34495e", "#e67e22", "#95a5a6"
        ]
        const doughnutBorders = ["#0a0a0a"] * liveData.favorite.labels.length

        chartData = {
            labels: liveData.favorite.labels,
            data: liveData.favorite.data,
            label: "Exercise Breakdown",
            type: "doughnut"
        }
        chartColours = doughnutColors.slice(0, liveData.favorite.labels.length)
        borderColours = doughnutBorders
    }

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
                    labels: {
                        color: "#ffffff"
                    }
                }
            },
            scales: chartData.type === "doughnut" ? {} : {
                x: {
                    ticks: {
                        color: "#ffffff"
                    },
                    grid: {
                        color: "#222222"
                    }
                },
                y: {
                    ticks: {
                        color: "#ffffff"
                    },
                    grid: {
                        color: "#222222"
                    }
                }
            }
        }
    })

    document.querySelector("#chartArea").classList.add("active")
    currenttype = type
}
