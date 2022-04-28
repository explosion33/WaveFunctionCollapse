var key = 0
var options = ["Grass1", "Grass2", "Tree", "Water", "Sand"]

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
    
    document.getElementById("load").hidden = false
    spinTask = setInterval(rotate, 2)

    createNewImage(key)
    checkApiTask = setInterval(function() { checkImageMade(key) }, 500);

}

function createNewImage(key) {
    let width = document.getElementById("width").value
    let height = document.getElementById("height").value

    let ops = {}
    for (let i = 0; i<options.length; i++) {
        k = options[i]
        v = document.getElementById(k + "n").value
        ops[k] = parseInt(v)
    } 

    fetch("/" + key,
    {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({"width": width, "height": height, "options": ops})
      }).then(function(){
          console.log("updating")
      }).catch(function(err){
        console.log(err)
        console.log("failed --retrying")
        createNewImage(key)
      });
}

async function checkImageMade(key) {
    let res = await fetch("/check/" + key);
    let json = await res.json()

    if (json == "True") {
        console.log("CONFIRMED")
        updateImage(key)
        clearInterval(checkApiTask)
        clearInterval(spinTask)
        document.getElementById("load").hidden = true
    }
}

function updateImage(key) {
    console.log("updating image")
    document.getElementById("image").src = "/static/images/" + key + ".png?" + new Date().getTime()
}


function setupInputs() {
    document.getElementById("widthSlider").min   = 1
    document.getElementById("widthSlider").max   = 30
    document.getElementById("widthSlider").value = 5

    document.getElementById("heightSlider").min   = 1
    document.getElementById("heightSlider").max   = 30
    document.getElementById("heightSlider").value = 5

    document.getElementById("width").value = 5
    document.getElementById("height").value = 5

}

var updateBoxFromSlider = function(idSlider, idBox) {
    let slider = document.getElementById(idSlider)
    let box = document.getElementById(idBox)

    box.value = slider.value
}

var updateSliderFromBox = function(idSlider, idBox) {
    let slider = document.getElementById(idSlider)
    let box = document.getElementById(idBox)

    console.log(slider.value + " " + box.value + " " + slider.max + " " + slider.min)

    if (box.value > parseInt(slider.max)) {
        box.value = slider.max
    } 

    else if (box.value < parseInt(slider.min)) {
        box.value = slider.min
    }

    slider.value = box.value
}

var rotate = function() {
    let load = document.getElementById("load");
    let curr = parseInt(load.name) + 5;
    if (curr >= 360) {curr -= 360};
    load.style="transform:rotate(" + curr + "deg)";
    load.name = curr;
}