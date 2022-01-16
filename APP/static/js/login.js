function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    var id_token = googleUser.getAuthResponse().id_token;
    var contenido = document.getElementById("contenido");
    console.log('EMAIL: '+profile.getEmail());
    console.log('NOMBRE: '+profile.getName());

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:5000/app/login');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        console.log('Signed in as: ' + xhr.responseText);
    };
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var respuesta = this.responseText;
                
            if (respuesta == "0"){
                //Se crea un usuario
                //window.location.href = "http://localhost:5000/app/usuarios/create";
                contenido.innerHTML = 
                "<div class='registro'>" +
                    "<h3>Has iniciado sesión por primera vez en GodTour</h3>" +
                    "<h5>Por favor, completa tu perfil</h5>" +
                    "<form action='{{url_for('bpclient.create_usuario')}}' method='POST'" +
                    "onsubmit='validarFormulario(event, this)' class='mb-3' enctype='multipart/form-data'>" +
                        "<div class='row'>" +
                            "<div class='col-3'>" +
                                "<label class='form-label'>Email: </label>" +
                                "<input class='form-control' id='correoUsuario' type='text' name='correo' required readonly />" +

                                "<br> " +

                                "<label class='form-label'>Nombre completo: </label>" +
                                "<input class='form-control' id='nombreUsuario' type='text' name='nombre_completo' required readonly />" +

                                "<br>" +

                                "<label class='form-label'>DNI: </label>" +
                                "<input class='form-control' id='dniUsuario' type='text' name='dni' required />" +

                                "<br>" +

                                "<label class='form-label'>Fecha nacimiento: </label>" +
                                "<input class='form-control' id='fechaNacimientoUsuario' type='date' name='fecha_nacimiento' required />" +

                                "<br>" +

                                "<label class='form-label'>Antigüedad permiso (Opcional): </label>" +
                                "<input class='form-control' id='dniUsuario' type='date' name='antiguedad_permiso' />" +
                            "</div>" +
                            "<div class='col-2'>" +
                                "<label for='foto_perfil' class='col-form-label'>Foto de perfil</label><br>" +
                                "<img src='https://i.postimg.cc/rpp0bZzx/doraemon.png' alt='' width='200' height='200' style='padding: 5% 5%;'>" +
                                "<input type='file' class='form-control' id='fotoUsuario' name='foto_perfil'>Cambiar</input>" +
                            "</div>" +
                        "</div>" +
                        "<br>" +
                        "<br>" +
                        "<input type='submit' class='btn btn-outline-info btn-lg' id='botonCentrado' value='Guardar' />" +
                    "</form>" +
                "</div>";
            } else if (respuesta == "1") {
                //El usuario ya existe
                //window.location.href = "http://localhost:5000";
            } else {
                alert("Ha ocurrido un error, por favor inténtelo de nuevo");
            }
        }
    }
    xhr.send('idtoken=' + id_token);
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then( function () { console.log('User signed out.'); } );
}