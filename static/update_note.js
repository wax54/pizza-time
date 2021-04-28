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

function updateNoteText(customer_id, text) {
    const noteContainer = document.getElementById(makePersonalNoteDisplayId(customer_id));
    const note = noteContainer.querySelector('.note');
    const noteEditButton = noteContainer.querySelector('.note-edit-button');
    note.innerText = text;
    if (text == false) {
        noteEditButton.innerText = "Add Note";
    } else {
        noteEditButton.innerText = "Edit";
    }
}

function changeToShowNoteView(customer_id) {
    //get the hidden note showing from the dom
    const personalNote = document.getElementById(makePersonalNoteDisplayId(customer_id));
    const noteInput = document.getElementById(makeNoteInputContainerId(customer_id));
    //show the note
    //a little flimsy
    personalNote.style.display = "flex";
    //destroy the input
    noteInput.remove();
}

function changeToEditNoteView(evt) {
    //get the element and the data
    const personalNote = evt.target.parentElement;
    const custId = personalNote.dataset.custId;
    //maybe should clean this up
    const personalNoteMsg = personalNote.querySelector('.note').innerText;
    //make a note input to replace the note view
    const orderNoteContainer = createCustomNoteInput(custId, personalNoteMsg)

    //hide the note showing view
    //a little flimsy
    personalNote.style.display = "none";
    //display the note input
    personalNote.parentElement.append(orderNoteContainer);
}

function createCustomNoteInput(custId, defaultValue) {
    const inputId = makeNoteInputId(custId);
    const containerId = makeNoteInputContainerId(custId);
    const noteInputContainer = genericNoteInputContainer.cloneNode(true);
    const noteForm = noteInputContainer.querySelector('.update-note-form');
    const noteDeleteButton = noteInputContainer.querySelector('.note-delete-button');
    const noteInput = noteForm.querySelector('.note-input');
    const noteLabel = noteForm.querySelector('.note-label');

    noteInputContainer.id = containerId;
    //add a listener to the form
    noteForm.addEventListener("submit", (evt) => {
        evt.preventDefault();
        const custId = evt.target.dataset.custId;
        const newNote = document.getElementById(makeNoteInputId(custId)).value;

        if (newNote == '') {
            cancelEditNote(custId);
        }
        else {
            saveEditNote(custId, newNote);
        }
    });
    //add a listener to the delete button
    noteDeleteButton.addEventListener("click", (evt) => {
        const custId = evt.target.parentElement.dataset.custId;
        deleteNote(custId)
    });

    //load the data into the new form
    noteForm.dataset.custId = custId;
    //input the values
    noteInput.id = inputId;
    noteInput.value = defaultValue;
    noteInput.placeholder = defaultValue;
    noteLabel.htmlFor = inputId;
    return noteInputContainer;
}

async function updateNote(evt) {

}

async function cancelEditNote(custId) {
    changeToShowNoteView(custId);
}

async function saveEditNote(custId, newNote) {
    const result = await sendNoteUpdateRequest(custId, newNote);
    if (result.status) {
        updateNoteText(custId, newNote);
        changeToShowNoteView(custId);
    } else {
        alert(result.message)
    }
}

async function deleteNote(custId) {
    const result = await sendNoteDeleteRequest(custId)
if (result.status) {
    updateNoteText(custId, '');
    changeToShowNoteView(custId);
} else {
    alert(result.message)
}
}




async function sendNoteUpdateRequest(customer_id, note) {
    const jsonPayload = {
        customer_id, note
    }
    const res = await axios.post('/api/customers/note/update', json = jsonPayload);
    return res.data
}

async function sendNoteDeleteRequest(customer_id) {
    const jsonPayload = {
        customer_id
    }
    const res = await axios.post('/api/customers/note/delete', json = jsonPayload);
    return res.data
}


function makePersonalNoteDisplayId(uniqueString) {
    return `${uniqueString}-personal-note`
}
function makeNoteInputId(uniqueString) {
    return `${uniqueString}-note-input`
}
function makeNoteInputContainerId(uniqueString) {
    return `${uniqueString}-edit-note`
}