// The first parameter are the coordinates of the center of the map
// The second parameter is the zoom level

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

for(var i = 0; i < baratas.length; i++) {
    var parse = baratas[i];
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