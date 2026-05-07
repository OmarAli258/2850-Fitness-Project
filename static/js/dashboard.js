//first thing in the javascript is the carousel 
const backbtn = document.getElementById("previous")
const forwardbtn = document.getElementById("next")
const cards = document.querySelectorAll(".recentCard")
// getting the buttons to work with in js
let currentindex = 0
// if the buttons exist on the page aka there is an activity then move forward or back till you make it to last or first
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
// hide all the cards then show the one with the specifed index 
function carousel(index) {
    cards.forEach(function (card) {
        card.style.display = "none"
    })
    cards[index].style.display = "block"
}
// second part is the Stats cards
const workoutbtn = document.getElementById("workouts")
const timebtn = document.getElementById("time")
const distancebtn = document.getElementById("distance")
const racesbtn = document.getElementById("races")
const favoritebtn = document.getElementById("favorite")
const mycanvas = document.getElementById("chart")
//get the cards so that when theyre clicked they work
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
//The function that shows and builds the charts based on whats clicked  
function showchart(type) {
    if (!mycanvas) {
        return
    }

    if (currenttype == type && currentchart != null) { //if the same card is clicked twice destroy the chart
        currentchart.destroy()
        currentchart = null
        currenttype = null
        document.querySelector("#chartArea").classList.remove("active")
        return
    }

    if (currentchart != null) { //destroy previous chart 
        currentchart.destroy()
    }

    let chartData = {}
    //chart data is gotten from flask in the html and the data is used to build the charts labels, data etc
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
//adding some nice colors to me the charts look nice using the same yellow as the rest of the site
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
    //actually making the chart that the data was enterd in above using Chart.js library
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

    document.querySelector("#chartArea").classList.add("active") //show the area around the chart
    currenttype = type
}
//The Drop Down search bar which was made instead of a seperate page for searching
const searchInput = document.getElementById("searchInput");
const searchResults = document.getElementById("searchResults");
let searchTimer = null; //make search bar a bit delayed so its not instant after every stroke

if (searchInput) {
    searchInput.addEventListener("input", function () { //activate if typing
        const query = searchInput.value.trim();

        clearTimeout(searchTimer); //cancel a search until user is done typing

        if (query === "") { //hide if the input is empty 
            hideDropdown();
            return;
        }

        searchTimer = setTimeout(function () { //search the database only after 250ms after the last letter typed to not waste database searches on every letter
            fetchSearchResults(query);
        }, 250);
    });

    document.addEventListener("click", function (event) { //if the user clicks off get rid of dropdown
        if (!event.target.closest(".search-wrapper")) {
            hideDropdown();
        }
    });
}
//calls the flask api and passes results to the renderresults function
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
//makes the html for the drop down using the search results 
function renderResults(results) {
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="search-empty">No activities found</div>';
        showDropdown();
        return;
    }

    let html = ""; //go through and make a clickable link to the its view activity page
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
//helper functions for showing and hiding the dropdown 
function showDropdown() {
    searchResults.classList.add("active");
}

function hideDropdown() {
    searchResults.classList.remove("active");
}