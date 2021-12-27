// The first parameter are the coordinates of the center of the map
// The second parameter is the zoom level

// The first parameter are the coordinates of the center of the map
        // The second parameter is the zoom level
        var map = L.map('map').setView([40.463667, -3.74922], 6);
        
        // {s}, {z}, {x} and {y} are placeholders for map tiles
        // {x} and {y} are the x/y of where you are on the map
        // {z} is the zoom level
        // {s} is the subdomain of cartodb
        var layer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
        });
        
        // Now add the layer onto the map
        map.addLayer(layer);

        var greenIcon = L.icon({
            iconUrl: 'http://localhost:5000/static/images/verde.png',
            iconSize: [40, 40],
            iconAnchor:   [22, 40],
            popupAnchor:  [-3, -76]
        });
        
        var yellowIcon = L.icon({
            iconUrl: 'http://localhost:5000/static/images/amarillo.png',
            iconSize: [40, 40],
            iconAnchor:   [22, 40],
            popupAnchor:  [-3, -76]
        });
        
        var redIcon = L.icon({
            iconUrl: 'http://localhost:5000/static/images/rojo.png',
            iconSize: [40, 40],
            iconAnchor:   [22, 40],
            popupAnchor:  [-3, -76]
        });

        var marcadores = [];

        function cargarMapa() {
            var spinner = document.getElementById("spinner");
            spinner.style.display = 'block';
            removeMarkers();
            var xhttp = new XMLHttpRequest();
            var text = document.getElementById("gasolineras_municipio");
            console.log(text);
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    try{
                        var json_res = JSON.parse(xhttp.responseText);
                        var baratas = json_res[0];
                        var medias = json_res[1];
                        var caras = json_res[2];
                        var latMin = parseFloat(json_res[3].toString().replace(",", "."));
                        var lonMin = parseFloat(json_res[4].toString().replace(",", "."));
                        var latMax = parseFloat(json_res[5].toString().replace(",", "."));
                        var lonMax = parseFloat(json_res[6].toString().replace(",","."));
                        
                        var corner1 = L.latLng(latMin, lonMin),
                        corner2 = L.latLng(latMax, lonMax),
                        bounds = L.latLngBounds(corner1, corner2);
                        map.fitBounds(bounds);
                        
                        for (barata of baratas){
                            var lat = parseFloat(barata["Latitud"].replace(",","."));
                            var lon = parseFloat(barata["Longitud (WGS84)"].replace(",", "."));
                            marcadores.push(L.marker([lat, lon], {icon : greenIcon}).addTo(map).bindPopup("Precio: " + barata["Precio Gasolina 95 E5"] + 
                                                                                                            ", Marca: " + barata["Rótulo"]));
                        }
                        for (media of medias){
                            var lat = parseFloat(media["Latitud"].replace(",","."));
                            var lon = parseFloat(media["Longitud (WGS84)"].replace(",","."));
                            marcadores.push(L.marker([lat, lon], {icon : yellowIcon}).addTo(map).bindPopup("Precio: " + media["Precio Gasolina 95 E5"] + 
                            ", Marca: " + media["Rótulo"]));
                        }
                        for (cara of caras) {
                            var lat = parseFloat(cara["Latitud"].replace(",","."));
                            var lon = parseFloat(cara["Longitud (WGS84)"].replace(",","."));
                            marcadores.push(L.marker([lat, lon], {icon : redIcon}).addTo(map).bindPopup("Precio: " + cara["Precio Gasolina 95 E5"] + 
                            ", Marca: " + cara["Rótulo"]));
                        }
                    } catch(error){
                        alert("No hay gasolineras en el municipio indicado");
                    }
                    spinner.style.display = 'none';
                } 
            };
            xhttp.open("GET", "/api/gasolineras?municipio="+text.value, true);
            xhttp.send();
        }

        function cargarMapaProvincias() {
            var spinner = document.getElementById("spinner");
            spinner.style.display = 'block';
            removeMarkers();
            var xhttp = new XMLHttpRequest();
            var text = document.getElementById("gasolineras_provincia");
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    try{
                        var json_res = JSON.parse(xhttp.responseText);
                        var baratas = json_res[0];
                        var medias = json_res[1];
                        var caras = json_res[2];
                        var latMin = parseFloat(json_res[3].toString().replace(",", "."));
                        var lonMin = parseFloat(json_res[4].toString().replace(",", "."));
                        var latMax = parseFloat(json_res[5].toString().replace(",", "."));
                        var lonMax = parseFloat(json_res[6].toString().replace(",","."));
                        
                        var corner1 = L.latLng(latMin, lonMin),
                        corner2 = L.latLng(latMax, lonMax),
                        bounds = L.latLngBounds(corner1, corner2);
                        map.fitBounds(bounds);
                        
                        for (barata of baratas){
                            var lat = parseFloat(barata["Latitud"].replace(",","."));
                            var lon = parseFloat(barata["Longitud (WGS84)"].replace(",", "."));
                            marcadores.push(L.marker([lat, lon], {icon : greenIcon}).addTo(map).bindPopup("Precio: " + barata["Precio Gasolina 95 E5"] + 
                                                                                                            ", Marca: " + barata["Rótulo"]));
                        }
                        for (media of medias){
                            var lat = parseFloat(media["Latitud"].replace(",","."));
                            var lon = parseFloat(media["Longitud (WGS84)"].replace(",","."));
                            marcadores.push(L.marker([lat, lon], {icon : yellowIcon}).addTo(map).bindPopup("Precio: " + media["Precio Gasolina 95 E5"] + 
                            ", Marca: " + media["Rótulo"]));
                        }
                        for (cara of caras) {
                            var lat = parseFloat(cara["Latitud"].replace(",","."));
                            var lon = parseFloat(cara["Longitud (WGS84)"].replace(",","."));
                            marcadores.push(L.marker([lat, lon], {icon : redIcon}).addTo(map).bindPopup("Precio: " + cara["Precio Gasolina 95 E5"] + 
                            ", Marca: " + cara["Rótulo"]));
                        }
                    } catch(error){
                        alert("No hay gasolineras en la provincia indicada");
                    }

                    spinner.style.display = 'none';
                } 
            };
            xhttp.open("GET", "/api/gasolineras?provincia="+text.value, true);
            xhttp.send();
        }

        function removeMarkers(){
            for (var i=0; i < marcadores.length; i++){
                map.removeLayer(marcadores[i])
            }
        }

/*
var latMinima = document.getElementById("latMin").value;
var latMaxima= document.getElementById("latMax").value;
var lonMinima = document.getElementById("lonMin").value;
var lonMaxima = document.getElementById("lonMax").value;
var baratas = document.getElementById("baratas").value;
var medias = document.getElementById("medias").value;
var caras = document.getElementById("caras").value;

console.log(latMinima);
console.log(latMaxima);
console.log(lonMinima);
console.log(lonMaxima);
console.log(baratas);
console.log(medias);
console.log(caras);


var map = L.map('map');
var corner1 = L.latLng(latMinima, lonMinima),
corner2 = L.latLng(latMaxima, lonMaxima),
bounds = L.latLngBounds(corner1, corner2);
map.fitBounds(bounds);


// {s}, {z}, {x} and {y} are placeholders for map tiles
// {x} and {y} are the x/y of where you are on the map
// {z} is the zoom level
// {s} is the subdomain of cartodb
var layer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Now add the layer onto the map
// map.addLayer(layer);

//Haremos un for poniendo markers.

var greenIcon = L.icon({
    iconUrl: 'http://localhost:5000/static/images/verde.png',
    iconSize: [40, 40],
    iconAnchor:   [22, 40],
    popupAnchor:  [-3, -76]
});

var yellowIcon = L.icon({
    iconUrl: 'http://localhost:5000/static/images/amarillo.png',
    iconSize: [40, 40],
    iconAnchor:   [22, 40],
    popupAnchor:  [-3, -76]
});

var redIcon = L.icon({
    iconUrl: 'http://localhost:5000/static/images/rojo.png',
    iconSize: [40, 40],
    iconAnchor:   [22, 40],
    popupAnchor:  [-3, -76]
});
var a = JSON.parse(baratas);
for(var i = 0; i < a.length; i++) {
    var parse = a[i];
    console.log(parse);
    //var lat = parse["Latitud"];
   // console.log(lat);
   
    //var lon = parse["Longitud (WGS84)"];
    //console.log(lon);
    //var precio = parse["Precio Gasolina 95 E5"];
    //var nombre = parse["Rótulo"];
    //let marca = L.marker([lat, lon], {icon : greenIcon}).addTo(map).bindPopup("Precio: " + precio + "</br> Nombre: " + nombre);
}

for(var i = 0; i < medias.length; i++) {
    var parse = medias[i];
    var lat = parse["Latitud"];
    var lon = parse["Longitud (WGS84)"];
    var precio = parse["Precio Gasolina 95 E5"];
    var nombre = parse["Rótulo"];
    let marca = L.marker([lat, lon], {icon : yellowIcon}).addTo(map).bindPopup("Precio: " + precio + ", Nombre: " + nombre);
}

for(var i = 0; i < caras.length; i++) {
    var parse = caras[i];
    var lat = parse["Latitud"];
    var lon = parse["Longitud (WGS84)"];
    var precio = parse["Precio Gasolina 95 E5"];
    var nombre = parse["Rótulo"];
    let marca = L.marker([lat, lon], {icon : redIcon}).addTo(map).bindPopup("Precio: " + precio + ", Nombre: " + nombre);
}

*/