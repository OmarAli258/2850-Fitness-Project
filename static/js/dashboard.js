// used Claude to explain the chart switching logic with Chart.js, the carousel index tracking for prev/next buttons,
// and the fetch API call to the search endpoint
//first thing in the javascript is the carousel 
const backbtn = document.getElementById("previous")
const forwardbtn = document.getElementById("next")
const cards = document.querySelectorAll(".recentCard")
// getting the buttons to work with in js
let currentindex = 0
// if the buttons exist on the page (aka there is an activity) move forward or back till you make it to last or first
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
// hide all cards then show the one with the specifed index 
function carousel(index) {
    cards.forEach(function (card) {
        card.style.display = "none"
    })
    cards[index].style.display = "block"
}

// second part is the stats cards
const workoutbtn = document.getElementById("workouts")
const timebtn = document.getElementById("time")
const distancebtn = document.getElementById("distance")
const racesbtn = document.getElementById("races")
const favoritebtn = document.getElementById("favorite")
const mycanvas = document.getElementById("chart")
//get the cards so when theyre clicked they work
let currenttype = null
let currentchart = null

//when button clicked show the chart
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

//builds and shows the chart based on which card is clicked  
function showchart(type) {
    if (!mycanvas) {
        return
    }

    //if the same card is clicked twice destroy the chart
    if (currenttype == type && currentchart != null) {
        currentchart.destroy()
        currentchart = null
        currenttype = null
        document.querySelector("#chartArea").classList.remove("active")
        return
    }

    //destroy previous chart before drawing a new one
    if (currentchart != null) {
        currentchart.destroy()
    }

    let chartData = {}
    //chart data comes from flask via the html and is used to build the chart labels and values etc
    if (type == "workouts") {
        chartData = {
            labels: CHART_DATA.labels,
            data: CHART_DATA.workouts,
            label: "Workouts This Week",
            type: "bar"
        }
    }

    if (type == "time") {
        chartData = {
            labels: CHART_DATA.labels,
            data: CHART_DATA.minutes,
            label: "Minutes Spent This Week",
            type: "bar"
        }
    }

    if (type == "distance") {
        chartData = {
            labels: CHART_DATA.labels,
            data: CHART_DATA.distance,
            label: "Distance This Week (km)",
            type: "line"
        }
    }

    if (type == "favorite") {
        chartData = {
            labels: CHART_DATA.type_labels,
            data: CHART_DATA.type_counts,
            label: "Exercise Breakdown",
            type: "doughnut"
        }
    }

    if (type == "races") {
        chartData = {
            labels: ["Upcoming", "Past", "PBs"],
            data: [
                CHART_DATA.upcoming_races,
                CHART_DATA.past_races,
                CHART_DATA.personal_bests
            ],
            label: "Race Summary",
            type: "bar"
        }
    }

    //adding colors to make the charts look nice, default is the yellow used on the rest of the site
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

    if (type == "races") {
        chartColours = ["#ff9f40", "#f5c518", "#2ecc71"]
        borderColours = ["#0a0a0a", "#0a0a0a", "#0a0a0a"]
    }

    if (type == "favorite") {
        chartColours = [
            "#f5c518",
            "#2c80b8",
            "#2ecc55",
            "#3ce7b7",
            "#c31b1b"
        ]
        borderColours = [
            "#0a0a0a",
            "#0a0a0a",
            "#0a0a0a",
            "#0a0a0a",
            "#0a0a0a"
        ]
    }

    //actually building the chart using the Chart.js library
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
                    ticks: { color: "#ffffff" },
                    grid: { color: "#222222" }
                },
                y: {
                    ticks: { 
                        color: "#ffffff",
                        stepSize: 1
                    },
                    grid: { color: "#222222" }
                }
            }
        }
    })

    //show the area around the chart
    document.querySelector("#chartArea").classList.add("active")
    currenttype = type
}

//drop down search bar (made instead of a seperate page for searching)
const searchInput = document.getElementById("searchInput");
const searchResults = document.getElementById("searchResults");
let searchTimer = null; //makes search a bit delayed so it doesnt fire on every keystroke

if (searchInput) {
    searchInput.addEventListener("input", function () { //runs when typing
        const query = searchInput.value.trim();

        clearTimeout(searchTimer); //cancel pending search if user keeps typing

        if (query === "") { //hide if input is empty 
            hideDropdown();
            return;
        }

        //wait 250ms after last keystroke before actually searching to avoid wasting database queries
        searchTimer = setTimeout(function () {
            fetchSearchResults(query);
        }, 250);
    });

    //if user clicks off get rid of dropdown
    document.addEventListener("click", function (event) {
        if (!event.target.closest(".search-wrapper")) {
            hideDropdown();
        }
    });
}

//calls the flask api and passes results to renderResults
function fetchSearchResults(query) {
    fetch("/api/search?q=" + encodeURIComponent(query))
        .then(function (response) {
            return response.json();
        })
        .then(function (results) {
            renderResults(results);
        })
        .catch(function (error) {
            console.error("Search failed:", error);
            hideDropdown();
        });
}

//builds the html for the dropdown using the search results 
function renderResults(results) {
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="search-empty">No activities found</div>';
        showDropdown();
        return;
    }

    let html = "";
    //loop through results and make each one a clickable link to its view activity page
    for (const activity of results) {
        const distance = activity.distance ? activity.distance + " km" : "No distance";
        html += `
            <a href="/activities/${activity.id}" class="search-result">
                <div class="search-result-type">${activity.type}</div>
                <div class="search-result-meta">${activity.date} | ${activity.duration} min | ${distance}</div>
            </a>
        `;
    }

    searchResults.innerHTML = html;
    showDropdown();
}

//helper functions to show and hide the dropdown 
function showDropdown() {
    searchResults.classList.add("active");
}

function hideDropdown() {
    searchResults.classList.remove("active");
}