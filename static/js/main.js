const quotes=["Discipline Is The Gateway To Your Dreams","Dont Dream Of Winning Train For it","Get Comfortable With Being Uncomfortable","Make Excuses Or Make Progress"]
const quoteelement= document.getElementById("quotes")
let index = 0
setInterval(function() {
    index=(index + 1) %quotes.length
    quoteelement.textContent=quotes[index]
}, 5000)

function initFeedMaps() {
    var mapElements = document.querySelectorAll('.feed-map[data-route]');
    
    mapElements.forEach(function(el) {
        var routeData = JSON.parse(el.dataset.route);
        
        var map = L.map(el).setView([routeData[0][0], routeData[0][1]], 13);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);
        
        L.polyline(routeData, {color: '#3498db', weight: 4}).addTo(map);
        
        map.fitBounds(map.getBounds());
    });
}