var key = 0

getRandomAscii = function() {
    let possible = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    return possible.charAt(Math.random() * possible.length);

}

getRandomKey = function(len) {
    key = "";
    for (let i = 0; i< len; i++) {
        key +=  getRandomAscii();
    }
    return key;
}

var generate = function() {
    if (key == 0) {
        key = getRandomKey(12);
    }
    
    createNewImage(key)
    checkApiTask = setInterval(function() { checkImageMade(key) }, 500);

}

function createNewImage(key) {
    fetch("/" + key);
    console.log("updating")
}

async function checkImageMade(key) {
    let res = await fetch("/check/" + key);
    let json = await res.json()

    if (json == "True") {
        console.log("CONFIRMED")
        updateImage(key)
        clearInterval(checkApiTask)
    }
}

function updateImage(key) {
    console.log("updating image")
    document.getElementById("image").src = "/static/images/" + key + ".png?" + new Date().getTime()
}