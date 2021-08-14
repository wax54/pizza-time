const APPLE = 'apple-maps';
const GOOGLE = 'google-maps'

function onAppleMobileTech() {
    return ((navigator.platform.indexOf("iPhone") != -1) ||
        (navigator.platform.indexOf("iPad") != -1) ||
        (navigator.platform.indexOf("iPod") != -1))
}
function prefferedMap() {
    if (localStorage.mapsPref === APPLE) return APPLE;
    else if(localStorage.mapsPref === GOOGLE) return GOOGLE;
    else return GOOGLE;
} 
function setPrefferedMap(pref) {
    if(pref === APPLE) localStorage.mapsPref = APPLE;
    else if (pref === GOOGLE) localStorage.mapsPref = GOOGLE;
    else throw Error("MAPS PREF INVALID!");
}

function updateMapLinks() {
    /* if we're on iOS, replace the https: with maps: protocol */
    if (onAppleMobileTech()) {
        if (prefferedMap() === APPLE) {
            const mapLinks = document.getElementsByClassName("map-link");
            for (let link of mapLinks) {
                //replace all the links with map links
                const destination = link.dataset.destination;
                link.href = `maps://maps.apple.com/?daddr=${destination}`
            }
        } else {
            const mapLinks = document.getElementsByClassName("map-link");
            for(let link of mapLinks){
                //replace all the links with map links
                const destination = link.dataset.destination;
                link.href = `maps://www.google.com/maps/dir/?api=1&dir_action=navigate&destination=${destination}`
            } 
        } 
    } else {
        const mapLinks = document.getElementsByClassName("map-link");
        for (let link of mapLinks) {
            //replace all the links with map links
            const destination = link.dataset.destination;
            link.href = `https://www.google.com/maps/dir/?api=1&dir_action=navigate&destination=${destination}`
        }
    }
}

// "https://www.google.com/maps/dir/?api=1&dir_action=navigate&destination={{order['address']|urlencode}}"

function giveAppleMapOption() {
    if (onAppleMobileTech()) {
        let mapsPrefButton = document.getElementById("maps-pref");
        //if no link yet, create the container and it and append them to the nav
        if (!mapsPrefButton) {
            //make the button
            mapsPrefButton = document.createElement("a");
            mapsPrefButton.id = "maps-pref";
            mapsPrefButton.className = "btn btn-block btn-light larger-text";
            //make the container
            const mapsPrefContainer = document.createElement('li');
            mapsPrefContainer.className = "nav-item m-2 d-grid gap-2";

            //get the navbar
            const navBar = document.getElementsByClassName("navbar-nav")[0];
            //add the button to the container
            mapsPrefContainer.append(mapsPrefButton);
            //add the container to the navbar(on the DOM)
            navBar.append(mapsPrefContainer);
        }
        updateMapPrefButton(mapsPrefButton);
    //not on I technology
    } else {
        //if there is a maps pref button...
        let mapsPrefButton = document.getElementById("maps-pref");
        if (mapsPrefButton) {
            //...remove it
            mapsPrefButton.parentElement.remove();
        }
    }

}

function updateMapPrefButton(button) {
    if(prefferedMap() === APPLE) {
        button.innerText = "Use Google Maps";
        button.onclick = (evt) => {
            evt.preventDefault();
            setPrefferedMap(GOOGLE);
            updateMapPrefButton(button)
            updateMapLinks();
        }
    } else {
        button.innerText = "Use Apple Maps";
        button.onclick = (evt) => {
            evt.preventDefault();
            setPrefferedMap(APPLE);
            updateMapPrefButton(button)
            updateMapLinks();
        }
    }
    
}

giveAppleMapOption();
updateMapLinks();