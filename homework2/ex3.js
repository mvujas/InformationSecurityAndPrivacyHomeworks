const btoa = require('btoa')

function ascii (a) { return a.charCodeAt(0); }
function toChar(i) { return String.fromCharCode(i); }

var mySecureOneTimePad = "Never send a human to do a machine's job";

function hash(msg,key) {
    if (key.length < msg.length) {
        var diff = msg.length - key.length;
        key += key.substring(0,diff);
    }

    var amsg = msg.split("").map(ascii);
    var akey = key.substring(0,msg.length).split("").map(ascii);
    return btoa(amsg.map(function(v,i) { 
        return v ^ akey[i];
    }).map(toChar).join(""));
}

// Just apply hash function on username 
// (may work with other usernames other admin, I haven't checked)
console.log(hash('admin', mySecureOneTimePad));