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

        var meteorologicaIcon = L.icon({
            iconUrl: 'http://localhost:5000/static/images/incidencia-meteorologica.png',
            iconSize: [40, 40],
            iconAnchor:   [22, 40],
            popupAnchor:  [-3, -76]
        });
        
        var montanaIcon = L.icon({
            iconUrl: 'http://localhost:5000/static/images/incidencia-montana.png',
            iconSize: [40, 40],
            iconAnchor:   [22, 40],
            popupAnchor:  [-3, -76]
        });

        var conoIcon = L.icon({
            iconUrl: 'http://localhost:5000/static/images/incidencia-cono.png',
            iconSize: [40, 40],
            iconAnchor:   [22, 40],
            popupAnchor:  [-3, -76]
        });
        
        var obrasIcon = L.icon({
            iconUrl: 'http://localhost:5000/static/images/incidencia-obras.png',
            iconSize: [40, 40],
            iconAnchor:   [22, 40],
            popupAnchor:  [-3, -76]
        });

        var retencionIcon = L.icon({
            iconUrl: 'http://localhost:5000/static/images/incidencia-retencion.png',
            iconSize: [40, 40],
            iconAnchor:   [22, 40],
            popupAnchor:  [-3, -76]
        });

        var marcadores = [];

        function cargarMapaRango() {
            removeMarkers();
            var xhttp = new XMLHttpRequest();
            var text = document.getElementById("rangoKM");
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
                    
                    } catch(error){
                        alert("No hay incidencias en el rango indicado");
                    }
                
                } 
            };
            xhttp.open("GET", "/api/incidencias?rango="+text.value, true);
            xhttp.send();
        }

        function cargarMapaProvincias() {
            removeMarkers();
            var xhttp = new XMLHttpRequest();
            var text = document.getElementById("trafico_provincia");
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    try{
                        var json_res = JSON.parse(xhttp.responseText);
                        var metereologicas = json_res[0];
                        var montanas = json_res[1];
                        var conos = json_res[2];
                        var obras = json_res[3];
                        var retenciones = json_res[4];
                        var latMin = parseFloat(json_res[5].toString().replace(",", "."));
                        var lonMin = parseFloat(json_res[6].toString().replace(",", "."));
                        var latMax = parseFloat(json_res[7].toString().replace(",", "."));
                        var lonMax = parseFloat(json_res[8].toString().replace(",","."));
                        
                        var corner1 = L.latLng(latMin, lonMin),
                        corner2 = L.latLng(latMax, lonMax),
                        bounds = L.latLngBounds(corner1, corner2);
                        map.fitBounds(bounds);
                        
                            //Tiene elementos
                            for (v of metereologicas){
                                var lat = parseFloat(v["geometry"]["coordinates"][1]);
                                var lon = parseFloat(v["geometry"]["coordinates"][0]);
                                marcadores.push(L.marker([lat, lon], {icon : meteorologicaIcon}).addTo(map).bindPopup("Causa: " + v["properties"]["causa"] + 
                                                                                                                ", Nivel: " + v["properties"]["nivel"]));
                            }
                            for (v of montanas){
                                var lat = parseFloat(v["geometry"]["coordinates"][1]);
                                var lon = parseFloat(v["geometry"]["coordinates"][0]);
                                marcadores.push(L.marker([lat, lon], {icon : montanaIcon}).addTo(map).bindPopup("Causa: " + v["properties"]["causa"] + 
                                                                                                                ", Nivel: " + v["properties"]["nivel"]));
                            }
                            for (v of conos){
                                var lat = parseFloat(v["geometry"]["coordinates"][1]);
                                var lon = parseFloat(v["geometry"]["coordinates"][0]);
                                marcadores.push(L.marker([lat, lon], {icon : conoIcon}).addTo(map).bindPopup("Causa: " + v["properties"]["causa"] + 
                                                                                                                ", Nivel: " + v["properties"]["nivel"]));
                            }
                            for (v of obras){
                                var lat = parseFloat(v["geometry"]["coordinates"][1]);
                                var lon = parseFloat(v["geometry"]["coordinates"][0]);
                                marcadores.push(L.marker([lat, lon], {icon : obrasIcon}).addTo(map).bindPopup("Causa: " + v["properties"]["causa"] + 
                                                                                                                ", Nivel: " + v["properties"]["nivel"]));
                            }
                        
                            for (v of retenciones){
                                var lat = parseFloat(v["geometry"]["coordinates"][1]);
                                var lon = parseFloat(v["geometry"]["coordinates"][0]);
                                marcadores.push(L.marker([lat, lon], {icon : retencionIcon}).addTo(map).bindPopup("Causa: " + v["properties"]["causa"] + 
                                                                                                                ", Nivel: " + v["properties"]["nivel"]));
                            }
                        
                    } 
                    
                    catch(error){
                        alert("No hay incidencias en la provincia indicada");
                    }
                
                } 
            };
            xhttp.open("GET", "/api/incidencias?provincia="+text.value, true);
            xhttp.send();
        }

        function removeMarkers(){
            for (var i=0; i < marcadores.length; i++){
                map.removeLayer(marcadores[i])
            }
        }