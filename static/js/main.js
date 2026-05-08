// Used Claude to brainstorm ideas and eventually led to the moving banner
 quotes=["Discipline Is The Gateway To Your Dreams","Dont Dream Of Winning Train For it","Get Comfortable With Being Uncomfortable","Make Excuses Or Make Progress"]
//above are the quotes in the banner
const quoteelement= document.getElementById("quotes")
let index = 0
//this is to the function that goes to the next quote every 5 secs and uses module to restart after reaching end of array
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

document.addEventListener('DOMContentLoaded', function() {
    const exerciseCards = document.querySelector('.exerciseCards');
    if (exerciseCards) {
        exerciseCards.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight') {
                this.scrollLeft += 200;
                e.preventDefault();
            } else if (e.key === 'ArrowLeft') {
                this.scrollLeft -= 200;
                e.preventDefault();
            }
        });
    }

    document.querySelectorAll('[style*="overflow-x:auto"]').forEach(function(el) {
        el.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight') {
                this.scrollLeft += 200;
                e.preventDefault();
            } else if (e.key === 'ArrowLeft') {
                this.scrollLeft -= 200;
                e.preventDefault();
            }
        });
    });
});