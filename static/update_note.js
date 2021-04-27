let genericNoteInputContainer = "goodMorning";
const NOTE_INPUT_URI = "/static/note-input-form.html";
start();

async function start() {
    genericNoteInputContainer = await getNoteInputHTML();

    let editNoteButtons = document.querySelectorAll(".note-edit-button");
    if (editNoteButtons.length)
    for (let button of editNoteButtons) {
        button.addEventListener("click", changeToEditNoteView);
    }


}

async function getNoteInputHTML() {
    const res = await axios.get(NOTE_INPUT_URI);
    const form = res.data;
    const inputContainer = document.createElement('div');
    inputContainer.innerHTML = form;
    return inputContainer;

}
function updateNoteText(orderNum, text) {
    const noteContainer = document.getElementById(makePersonalNoteDisplayId(orderNum));
    const note = noteContainer.querySelector('.note');
    note.innerText = text;
}
function changeToShowNoteView(orderNum) {
    //get the hidden note showing from the dom
    const personalNote = document.getElementById(makePersonalNoteDisplayId(orderNum));
    const noteInput = document.getElementById(makeNoteInputContainerId(orderNum));
    //show the note
    //a little flimsy
    personalNote.style.display = "flex";
    //destroy the input
    noteInput.remove();
    console.log(orderNum, 'success!');
}

function changeToEditNoteView(evt) {
    //get the element and the data
    const personalNote = evt.target.parentElement;
    const orderNum = personalNote.dataset.num;
    const date = personalNote.dataset.date;
    //maybe should clean this up
    const personalNoteMsg = personalNote.querySelector('.note').innerText;
    //make a note input to replace the note view
    const orderNoteContainer = createCustomNoteInput(orderNum, date, personalNoteMsg)

    //hide the note showing view
    //a little flimsy
    personalNote.style.display = "none";
    //display the note input
    personalNote.parentElement.append(orderNoteContainer);
}

function createCustomNoteInput(num, date, defaultValue) {
    const inputId = makeNoteInputId(num);
    const containerId = makeNoteInputContainerId(num);
    const noteInputContainer = genericNoteInputContainer.cloneNode(true);
    const noteForm = noteInputContainer.querySelector('.update-note-form');
    const noteInput = noteForm.querySelector('.note-input');
    const noteLabel = noteForm.querySelector('.note-label');

    noteInputContainer.id = containerId;
    //add a listener to the form
    noteForm.addEventListener("submit", updateNote)

    //load the data into the new form
    noteForm.dataset.num = num;
    noteForm.dataset.date = date;
    //input the values
    noteInput.id = inputId;
    noteInput.value = defaultValue;
    noteInput.placeholder = defaultValue;
    noteLabel.htmlFor = inputId;
    return noteInputContainer;
}

async function updateNote(evt) {
    evt.preventDefault();
    const orderNum = evt.target.dataset.num;
    const date = evt.target.dataset.date;
    const newNote = document.getElementById(makeNoteInputId(orderNum)).value;

    const result = await sendNoteUpdateRequest(orderNum, date, newNote);
    if (result.status) {
        updateNoteText(orderNum, newNote);
        changeToShowNoteView(orderNum);
    } else {
        alert(result.message)
    }
}

async function sendNoteUpdateRequest(num, date, note) {
    const jsonPayload = {
        num, date, note
    }

    const res = await axios.post('/orders/note/update', json = jsonPayload);
    return res.data
}

function makePersonalNoteDisplayId(num) {
    return `${num}-personal-note`
}
function makeNoteInputId(num) {
    return `${num}-note-input`
}
function makeNoteInputContainerId(num) {
    return `${num}-edit-note`
}