let tipInputs = document.querySelectorAll(".tip-input");

for (let input of tipInputs) {
    input.addEventListener("change", (evt) => {
        updateTip(evt.target.id);
    });
    input.parentElement.addEventListener("submit", (evt) => {
        evt.preventDefault();
        updateTip(evt.target.id);
    });
}

