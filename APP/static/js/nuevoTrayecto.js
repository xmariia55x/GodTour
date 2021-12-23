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

window.onload = function () {
    if (document.getElementById("nombreOrigen").value.length > 0){
        
        var oLat = document.getElementById("latitudOrigen").value; 
        var oLon = document.getElementById("longitudOrigen").value;
        var oNombre = document.getElementById("nombreOrigen").value;
        
        var dLat = document.getElementById("latitudDestino").value; 
        var dLon = document.getElementById("longitudDestino").value;
        var dNombre = document.getElementById("nombreDestino").value;

        asignarDireccion(oNombre, oLat, oLon, "Origen");
        asignarDireccion(dNombre, dLat, dLon, "Destino");
    }
}


function buscarDirecciones(evento, formulario, tipoBusqueda) {
    evento.preventDefault();
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            try{
                var json_res = JSON.parse(xhttp.responseText);
                var codigo = "";
                var divResultados = document.getElementById("resultados"+tipoBusqueda); //Origen o Destino
                if (json_res.length == 0){
                    codigo += '<label>No se han encontrado resultados</label>'
                } else {
                    codigo += '<label>Resultados encontrados:</label>'
                }

                for (x of json_res) {
                    codigo += "<button type=\"button\" class=\"list-group-item list-group-item-action\" "
                              +"data-bs-toggle=\"offcanvas\" data-bs-target=\"#offcanvas"+tipoBusqueda+"\" aria-controls=\"offcanvas"+tipoBusqueda+"\" aria-current=\"true\" "
                              +"onclick=\"asignarDireccion('"+x.display_name+"', "+x.lat+", "+x.lon+", '"+tipoBusqueda+"')\">"+ x.display_name+"</button>";
                }
                divResultados.innerHTML = codigo;

                return false;

            } catch(error) {
                alert("Dirección no encontrada")
            }
        }
    };
    xhttp.open("GET", "https://nominatim.openstreetmap.org/search?q="
                       +formulario.numero.value + "+"
                       +formulario.tipo.value + "+"
                       +formulario.nombre.value + "+"
                       +formulario.ciudad.value + "+"
                       +formulario.cp.value +"&format=json&key=aawYnbqgFdCflcNz0TnpNv21CeKSUq1x", true);
    xhttp.send();
}

function asignarDireccion(nombre, lat, lon, tipoBusqueda){
    var offcanvas = document.getElementById('offcanvas'+tipoBusqueda);

    input_nombre = document.getElementById('nombre'+tipoBusqueda);
    input_latitud = document.getElementById('latitud'+tipoBusqueda);
    input_longitud = document.getElementById('longitud'+tipoBusqueda);

    input_nombre.value = nombre;
    input_latitud.value = lat;
    input_longitud.value = lon;

    var origenIcon = L.icon({
        iconUrl: 'http://localhost:5000/static/images/verde-marker.png',
        iconSize: [40, 40],
        iconAnchor:   [22, 40],
        popupAnchor:  [-3, -76]
    });

    var destinoIcon = L.icon({
        iconUrl: 'http://localhost:5000/static/images/rojo-flag.png',
        iconSize: [40, 40],
        iconAnchor:   [22, 40],
        popupAnchor:  [-3, -76]
    });

    if (tipoBusqueda == 'Origen'){
        if (marcadorOrigen != null)
            map.removeLayer(marcadorOrigen);
        marcadorOrigen =  L.marker([lat, lon], {icon : origenIcon}).addTo(map).bindPopup("<strong>Origen</strong><br>Lat: " + lat + "<br>Lon: " + lon + "<br>Nombre: " + nombre);
    } else if (tipoBusqueda == 'Destino'){
        if (marcadorDestino != null)
            map.removeLayer(marcadorDestino);
        marcadorDestino =  L.marker([lat, lon], {icon : destinoIcon}).addTo(map).bindPopup("<strong>Destino</strong><br>Lat: " + lat + "<br>Lon: " + lon + "<br>Nombre: " + nombre);
    }

    if (marcadorOrigen != null && marcadorDestino != null){
        var bounds = L.latLngBounds(marcadorOrigen.getLatLng(), marcadorDestino.getLatLng());
        map.fitBounds(bounds);
    }
}

function validarFormulario(evento, formulario){
    console.log(formulario.origen_nombre.value);
    if (formulario.origen_nombre.value.length == 0){
        evento.preventDefault();
        alert("No se ha introducido el origen");
        return false;
    } 
    
    if (formulario.destino_nombre.value.length == 0){
        alert("No se ha introducido el destino");
    }
    
    var select = document.getElementById("select-vehiculo");
    var selectedOperation = select.options[select.selectedIndex].getAttribute("plazas");

    if (document.getElementsByName("plazas_totales")[0].value > selectedOperation){
        evento.preventDefault();
        alert("Se ha superado el límite máximo de plazas del vehículo. Seleccione un número menor o igual que "+selectedOperation);
        return false;
    }
    //var selectedOperation = select.options[select.selectedIndex].data-plazas;

    alert("Actualizado con éxito");
}

function actualizarMaxPlazas(){
    var plazas_totales = document.getElementsByName("plazas_totales")[0];
    var vehiculo_id = document.getElementsByName("vehiculo")[0].value;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json_res = JSON.parse(xhttp.responseText);
            plazas_totales.setAttribute('max', json_res["plazas"]);
            plazas_totales.value = json_res["plazas"];   
        }
    };
    xhttp.open("GET", "/api/vehiculos/"+vehiculo_id);
    xhttp.send();
}