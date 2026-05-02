const backbtn = document.getElementById("previous")
const forwardbtn = document.getElementById("next")
const cards = document.querySelectorAll(".recentCard")
let currentindex=0
forwardbtn.addEventListener("click", function(){
    if (currentindex < cards.length-1){
        currentindex= currentindex+1
        carousel(currentindex)
    }
})
backbtn.addEventListener("click", function(){
    if (currentindex > 0){
        currentindex=currentindex-1
        carousel(currentindex)
    }
})
function carousel(index) {
    cards.forEach(function(card){
        card.style.display='none'
    })
    cards[index].style.display='block'

}
const workoutbtn=document.getElementById("workouts")
const timebtn=document.getElementById("time")
const streakbtn=document.getElementById("streak")
const favoritebtn=document.getElementById("favorite")
const mycanvas =document.getElementById("chart")
workoutbtn.addEventListener("click",function(){
    showchart("workouts")
})
timebtn.addEventListener("click",function(){
    showchart("time")
})
streakbtn.addEventListener("click",function(){
    showchart("streak")
})
favoritebtn.addEventListener("click",function(){
    showchart("favorite")

})
let currenttype =null 
let currentchart = null

function showchart(type){
    if (currenttype == type && currentchart != null) {
        currentchart.destroy()
        currentchart = null
        currenttype = null
        document.querySelector('#chartArea').classList.remove('active')
        return
    }
    if (currentchart != null) {
        currentchart.destroy()
    }
    let chartData={}
    if (type=="workouts"){
        chartData={
            labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
            data: [1,0,2,0,1,2,0],
            label:"Workouts This Week",
            type: 'bar'
        }
    }
    if (type=="time"){
        chartData={
            labels:['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
            data: [1,0,3,0,1.5,0,3,0],
            label:"Time Spent This Week",
            type: 'bar'
        }
    }
    if (type == "streak") {
        chartData = {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            data: [3, 5, 7, 14],
            label: "Streak Over Last 4 Weeks",
            type: 'line'
        }
    }

    if (type == "favorite") {
        chartData = {
            labels: ['Running', 'Swimming', 'Cycling', 'Weightlifting', 'Crossfit'],
            data: [12, 8, 5, 3, 2],
            label: "Exercise Breakdown",
            type: 'doughnut'
        }
    }

    let chartColours = "#f5c518"
    let borderColours = "#f5c518"

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
                borderColor: borderColours
            }]
        }
    })
    document.querySelector('#chartArea').classList.add('active')
    currenttype=type
}