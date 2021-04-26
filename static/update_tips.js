
let tipInputs = document.querySelectorAll(".tip-input");
for (let input of tipInputs) {
    input.addEventListener("change", (evt) => {
        updateTipFromInputId(evt.target.id);
    });
    input.parentElement.addEventListener("submit", tipSubmitted);
}

async function tipSubmitted(evt) {
    evt.preventDefault();
    //get the input from the form
    const input = evt.target.querySelector('input')
    const success = await updateTipFromInputId(input.id);
    // TODO 
    // notify user that the tip has been updated in a non annoying way
    if (success) {
        input.value = "";
    }
}


async function updateTipFromInputId(id) {
    const input = document.getElementById(id);

    const num = input.dataset.num;
    const date = input.dataset.date;
    let tip = input.value;
    if (tip == '') {
        tip = '0';
    }
    jsonPayload = { num, date, tip };
    const res = await axios.patch("/edit_order_tip", json = jsonPayload);
    const data = res.data;
    //let them know if the attempt failed
    if (data.status == true) {
        console.log('hello')
        input.placeholder = tip;
    } else {
        alert("something went wrong updating the Database.\
        \nPlease try reloading and updating the tip again!");
    }
}