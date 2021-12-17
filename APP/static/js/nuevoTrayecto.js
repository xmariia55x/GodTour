// The first parameter are the coordinates of the center of the map
// The second parameter is the zoom level

var map = L.map('map').setView([36.7213028, -4.4216366], 11);

// {s}, {z}, {x} and {y} are placeholders for map tiles
// {x} and {y} are the x/y of where you are on the map
// {z} is the zoom level
// {s} is the subdomain of cartodb
var layer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Now add the layer onto the map
// map.addLayer(layer);

var marcadores = [];

// This is AJAX FC
function cargarMapa() {
    removeMarkers();
    var xhttp = new XMLHttpRequest();
    //var text = document.getElementById("texto");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            /*var json_res = JSON.parse(xhttp.responseText);
            for (x of json_res) {
                marcadores.push(L.marker([x.lat, x.lon]).addTo(map).bindPopup("Lat: " + x.lat +
                    "<br>Lon: " + x.lon +
                    "<br>Hint: " + x.hint));
            }*/
        }
    };
    xhttp.open("GET", "/api/logbookByEmail?email=" + text.value, true);
    xhttp.send();
}

function removeMarkers() {
    for (var i = 0; i < marcadores.length; i++) {
        map.removeLayer(marcadores[i])
    }
}
