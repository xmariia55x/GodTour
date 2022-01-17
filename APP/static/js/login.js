function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    var id_token = googleUser.getAuthResponse().id_token;
    var contenido = document.getElementById("contenido");
    console.log('EMAIL: ' + profile.getEmail());
    console.log('NOMBRE: ' + profile.getName());

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:5000/app/login');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function () {
        console.log('Signed in as: ' + xhr.responseText);
    };
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var respuesta = this.responseText;

            if (respuesta == "0") {
                //Se crea un usuario
                //window.location.href = "http://localhost:5000/app/usuarios/create";
                contenido.innerHTML = "<div class='px-0 pt-0 my-0'>" +
                        "<h1 class='display-8 fw-bold'>Has iniciado sesión por primera vez en GodTour</h1>" +
                        "<h5>Por favor, completa tu perfil</h5>" +
                        "<form action='{{url_for('bpclient.create_usuario')}}' method='POST'" +
                        "onsubmit='validarFormulario(event, this)' class='mb-3' enctype='multipart/form-data'>" +
                            "<div class='row justify-content-md-center' style='text-align: left;'>" +
                                "<div class='col-3' style='margin-right: 5%;'>" +
                                    "<label class='form-label'>Email: </label>" +
                                    "<input class='form-control' id='correoUsuario' value='" + profile.getEmail() + "' type='text' name='correo' required readonly />" +

                                    "<br> " +

                                    "<label class='form-label'>Nombre completo: </label>" +
                                    "<input class='form-control' id='nombreUsuario' value='" + profile.getNombre() + "' type='text' name='nombre_completo' required />" +

                                    "<br>" +

                                    "<label class='form-label'>DNI: </label>" +
                                    "<input class='form-control' id='dniUsuario' type='text' name='dni' required />" +

                                    "<br>" +

                                    "<label class='form-label'>Fecha nacimiento: </label>" +
                                    "<input class='form-control' id='fechaNacimientoUsuario' type='date' name='fecha_nacimiento' required />" +

                                    "<br>" +

                                    "<label class='form-label'>Antigüedad permiso (Opcional): </label>" +
                                    "<input class='form-control' id='antiguedadUsuario' type='date' name='antiguedad_permiso' />" +
                                "</div>" +
                                "<div class='col-3'>" +
                                    "<label for='foto_perfil' class='col-form-label'>Foto de perfil: </label><br>" +
                                    "<img src='"+profile.getPicture()+"' id='foto' alt='' width='200' height='200' style='margin: 5% 0%;'>" +
                                    "<input type='file' class='form-control' id='fotoUsuario' name='foto_perfil' onchange='cambiarFoto' style='width: 200px;' />" +
                                "</div>" +
                            "</div>" +
                            "<br>" +
                            "<br>" +
                            "<input type='submit' class='btn btn-outline-info btn-lg' id='botonCentrado' value='Guardar' />" +
                        "</form>" +
                    "</div>";
            } else if (respuesta == "1") {
                window.location.href = "http://localhost:5000";
            } else {
                alert("Ha ocurrido un error, por favor inténtelo de nuevo");
            }
        }
    }
    xhr.send('idtoken=' + id_token);
}

function cambiarFoto() {
    var file = this.files.get(0);
    var img = document.getElementById("foto");
    img.src = file;
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () { console.log('User signed out.'); });
}