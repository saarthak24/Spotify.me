var express = require('express'); // Express web server framework
var request = require('request'); // "Request" library
var cors = require('cors');
var cookieParser = require('cookie-parser');
var crypto = require("crypto");
var { client_id, client_secret, redirect_uri } = require('./settings.js');

/**
* Generates a random string containing numbers and letters
* @param  {number} length The length of the string
* @return {string} The generated string
*/
var generateRandomString = function(length) {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  
  for (var i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
};

this.verifyCode = generateRandomString(64)

var sha256Hasher = crypto.createHmac("sha256", client_secret);
var code_challenge = sha256Hasher.update(this.verifyCode).digest('base64');

console.log("Client_ID: " + client_id);

var stateKey = 'spotify_auth_state';

var app = express();
app.use(express.static(__dirname + '/public'))
.use(cors())
.use(cookieParser());

app.get('/login', function(req, res) {
  
  var state = generateRandomString(16);
  res.cookie(stateKey, state);
  
  // the application requests authorization
  var scope = 'user-read-private user-read-email user-library-read playlist-read-private';
  query = 'https://accounts.spotify.com/authorize?' +
  new URLSearchParams({
    client_id: client_id,
    response_type: 'code',
    redirect_uri: redirect_uri,
    state: state,
    scope: scope,
    code_challenge_method: 'S256',
    code_challenge: code_challenge
  })
  console.log(query);
  res.redirect(query);
});

// app.get('/callback', function(req, res) {
//   // the application requests refresh and access tokens
//   // after checking the state parameter
  
//   var code = req.query.code || null;
//   var state = req.query.state || null;
//   var storedState = req.cookies ? req.cookies[stateKey] : null;
  
//   if (state === null || state !== storedState) {
//     res.redirect('/#' +
//     new URLSearchParams({
//       error: 'state_mismatch'
//     }));
//   } else {
//     res.clearCookie(stateKey);
//     var authOptions = {
//       url: 'https://accounts.spotify.com/api/token',
//       form: {
//         code: code,
//         redirect_uri: redirect_uri,
//         grant_type: 'authorization_code'
//       },
//       headers: {
//         'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))
//       },
//       json: true
//     };
    
//     request.post(authOptions, function(error, response, body) {
//       if (!error && response.statusCode === 200) {
        
//         var access_token = body.access_token,
//         refresh_token = body.refresh_token;
        
//         var options = {
//           url: 'https://api.spotify.com/v1/me',
//           headers: { 'Authorization': 'Bearer ' + access_token },
//           json: true
//         };
        
//         // use the access token to access the Spotify Web API
//         request.get(options, function(error, response, body) {
//           console.log(body);
//         });
        
//         // we can also pass the token to the browser to make requests from there
//         res.redirect('/#' +
//         new URLSearchParams({
//           access_token: access_token,
//           refresh_token: refresh_token
//         }));
//       } else {
//         res.redirect('/#' +
//         new URLSearchParams({
//           error: 'invalid_token'
//         }));
//       }
//     });
//   }
// });

// app.get('/refresh_token', function(req, res) {
  
//   // requesting access token from refresh token
//   var refresh_token = req.query.refresh_token;
//   var authOptions = {
//     url: 'https://accounts.spotify.com/api/token',
//     headers: { 'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64')) },
//     form: {
//       grant_type: 'refresh_token',
//       refresh_token: refresh_token
//     },
//     json: true
//   };
  
//   request.post(authOptions, function(error, response, body) {
//     if (!error && response.statusCode === 200) {
//       var access_token = body.access_token;
//       res.send({
//         'access_token': access_token
//       });
//     }
//   });
// });

console.log('Listening on 8888');
app.listen(8888);