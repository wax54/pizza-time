
async function updateTip(id) {
    const input = document.getElementById(id);

    const num = input.dataset.num;
    const date = input.dataset.date;
    const tip = input.value;
    jsonPayload = { num, date, tip };
    const res = await axios.patch("/edit_order_tip", json = jsonPayload);
    const data = res.data;
    //let them know if the attempt failed
    if (data.status == false) {
        alert("something went wrong updating the Database.\
        \nPlease try reloading and updating the tip again!");
    }
}