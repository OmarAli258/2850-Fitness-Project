const quotes=["Discipline Is The Gateway To Your Dreams","Dont Dream Of Winning Train For it","Get Comfortable With Being Uncomfortable","Make Excuses Or Make Progress"]
const quoteelement= document.getElementById("quotes")
let index = 0
setInterval(function() {
    index=(index + 1) %quotes.length
    quoteelement.textContent=quotes[index]
}, 5000)