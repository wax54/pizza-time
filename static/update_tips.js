
let tipInputs = document.querySelectorAll(".tip-input");
for (let input of tipInputs) {
    input.addEventListener("change", tipChanged);
}
async function tipChanged(evt) {
    const input = evt.target;
    const success = await updateTipFromInputId(input.id);
    tipUpdateHTML(success, input);

}



function tipUpdateHTML(result, input) {
    // TODO 
    // notify user that the tip has been updated in a non annoying way
    if (result) {
        const tip = getTip(input);
        //input.value = "";
        input.placeholder = tip;
    } else {
        alert("something went wrong updating the Database.\
        \nPlease try reloading and updating the tip again!");
    }
}


async function updateTipFromInputId(id) {
    const input = document.getElementById(id);

    const num = input.dataset.num;
    const date = input.dataset.date;
    const tip = getTip(input);
    jsonPayload = { num, date, tip };
    const res = await axios.patch("/api/orders/edit_tip", json = jsonPayload);
    const data = res.data;
    //let them know if the attempt failed
    if (data.status == true) {
        return true;
    } else {
        return false;
    }
}

function getTip(input) {
    let tip = input.value;
    if (tip == '') {
        tip = '0.00';
    }
    return tip;
}