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
const favoritebtn = document.getElementById("favorite")
const mycanvas = document.getElementById("chart")

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

    if (type == "workouts") {
        chartData = {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            data: [1, 0, 2, 0, 1, 2, 0],
            label: "Workouts This Week",
            type: "bar"
        }
    }

    if (type == "time") {
        chartData = {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            data: [45, 0, 60, 0, 30, 50, 0],
            label: "Minutes Spent This Week",
            type: "bar"
        }
    }

    if (type == "distance") {
        chartData = {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            data: [5, 0, 8, 0, 3, 6, 0],
            label: "Distance This Week (km)",
            type: "line"
        }
    }

    if (type == "favorite") {
        chartData = {
            labels: ["Running", "Swimming", "Cycling", "Weightlifting", "Crossfit"],
            data: [12, 8, 5, 3, 2],
            label: "Exercise Breakdown",
            type: "doughnut"
        }
    }

    let chartColours = "#f5c518"
    let borderColours = "#f5c518"

    if (type == "time") {
        chartColours = "#36a2eb"
        borderColours = "#36a2eb"
    }

    if (type == "distance") {
        chartColours = "#2ecc71"
        borderColours = "#2ecc71"
    }

    if (type == "favorite") {
        chartColours = [
            "#f5c518", // Running
            "#3498db", // Swimming
            "#2ecc71", // Cycling
            "#e74c3c", // Weightlifting
            "#9b59b6"  // Crossfit
        ]

        borderColours = [
            "#0a0a0a",
            "#0a0a0a",
            "#0a0a0a",
            "#0a0a0a",
            "#0a0a0a"
        ]
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