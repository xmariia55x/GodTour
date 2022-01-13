function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId() + 'Don’t send to your backend! Use an ID token.');
    var id_token = googleUser.getAuthResponse().id_token;
    console.log('ID token: ' + id_token);
    console.log('EMAIL: '+profile.getEmail());
    console.log('NOMBRE: '+profile.getName());

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:5000/app/login');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        console.log('Signed in as: ' + xhr.responseText);
    };
    xhr.send('idtoken=' + id_token);
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then( function () { console.log('User signed out.'); } );
}