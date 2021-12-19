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

var marcadorOrigen = null;
var marcadorDestino = null;

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

function buscarOrigen(formulario, tipo) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            try{
                var json_res = JSON.parse(xhttp.responseText);
                var codigo = "";
                var divResultados = document.getElementById("resultadosOrigen");
                console.log("hola");
                console.log(json_res);
                if (json_res == []){
                    throw "excepcion";
                }

                for (x of json_res) {
                    codigo += '<button type="button" class="list-group-item list-group-item-action" aria-current="true" onclick=asignarOrigen('+x+')>'+ x["display_name"]+'</button>';
                }
                
                divResultados.innerHTML = codigo;
            } catch(error) {
                alert("Dirección no encontrada")
            }
        }
    };
    xhttp.open("GET", "https://open.mapquestapi.com/nominatim/v1/search.php?q="
                       +formulario.numero +" "
                       +formulario.nombre +" "
                       +formulario.ciudad +" "
                       +formulario.cp +"&format=json&key=aawYnbqgFdCflcNz0TnpNv21CeKSUq1x", true);
    xhttp.send();
}