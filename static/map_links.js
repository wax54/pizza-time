function replaceMapLinksForIphone() {
    if /* if we're on iOS, open in Apple Maps */
        ((navigator.platform.indexOf("iPhone") != -1) ||
        (navigator.platform.indexOf("iPad") != -1) ||
        (navigator.platform.indexOf("iPod") != -1)){
            const mapLinks = document.getElementsByClassName("map-link");
            for(let link of mapLinks){
                //replace all the links with map links
                const ref = link.href;
                link.href = ref.replace("https://", "maps://");
            }
        }
}

replaceMapLinksForIphone();