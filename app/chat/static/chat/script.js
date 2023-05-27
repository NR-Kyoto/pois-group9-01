console.log("loaded");

let global_chat_history_list = []

//get csrf token
function getCookie(name){
    let cookieValue = null;
    if (document.cookie && document.cookie !== ''){
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++){
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/*
function get_chat_history_list(){
    const chat_history_entries = document.querySelector(".chat_area").querySelectorAll(".entry");
    //for each entry, get .speaker and .lines
    let chat_history_list = [];
    chat_history_entries.forEach(entry => {
        const speaker = entry.querySelector(".speaker");
        const speaker_name = speaker.innerHTML.trim();
        const isAssistant = speaker.classList.contains('speaker_assistant');
        const lines = entry.querySelector(".lines").textContent.trim();
        chat_history_list.push({
            "speaker": speaker_name,
            "isAssistant": isAssistant,
            "lines": lines,
        });
    });
    return chat_history_list;
}
*/

function submit_text_with_chat_history(e,form,audio){
    e.preventDefault();
    setButtonDisabled(true);
    //let chat_history_list = ;
    //console.log(form);
    let form_data = new FormData(form);
    //form_data.append("chat_history", JSON.stringify(get_chat_history_list()));
    form_data.append("chat_history", JSON.stringify(global_chat_history_list));
    form_data.append("audio64" , (audio64_stash.length > 0 && (audio64_stash.split(",")[1]).length > 0) ? audio64_stash : "")

    const request = new Request(
        "/chat/mock_post/",
        {headers: {'X-CSRFToken': csrftoken},
        }
    );

    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: form_data,
    }).then(function(response){
        response.json().then(function(data){
            //console.log(data);
            updateEntries(data);
            //console.log(data["chat"][1]["audio"]);
            const audio_base64_uri = data["chat"][data["chat"].length-1]["audio"]
            //const audio = new Audio("data:audio/webm; codecs=opus;base64," + audio_base64);
            audio.src = audio_base64_uri;
            audio.play();
            setButtonDisabled(false);
        });
    });
}

let audio64_stash = "";

function audio_to_base64(e, audioChunks){
    e.preventDefault();
    mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/mpeg;';
    const audioBlob = new Blob(audioChunks , {type: mimeType});
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob)
    reader.onload = () =>{
        audio64_uri = reader.result;
        audio64_stash = audio64_uri;
        sendAudioFile(audio64_uri);
        setAudioOnInput(audio64_uri);
    }
}

function setAudioOnInput(audio_uri){
    const input_audio = document.querySelector(".user_input .voice");
    console.log(input_audio);
    input_audio.src = audio_uri;
}

function mic_setup(mediaRecorder){
    // get mic input
    const mic_button = document.querySelector("#mic_button");
    let isRecording = false;
    function mic_on(){
        mediaRecorder.start();
        console.log(mediaRecorder.state);
        console.log("recorder started");
        mic_button.style.background = "red";
        mic_button.style.color = "black";
        isRecording = true;
        setButtonDisabled(true);
    }
    function mic_off(){
        mediaRecorder.stop();
        console.log(mediaRecorder.state);
        console.log("recorder stopped");
        mic_button.style.background = "";
        mic_button.style.color = "";
        isRecording = false;
        setButtonDisabled(false);
    }
    let timeoutID;
    mic_button.addEventListener("click", function(e) {
        e.preventDefault();
        console.log("mic_button clicked");
        clearTimeout(timeoutID);
        if(isRecording){
            mic_off();
        } else {
            mic_on();
            timeoutID = setTimeout(() => {
                mic_off();
            }, 60000);
        }
    });
}

//send audio file to server
function sendAudioFile(audio64_uri){
    const form_data = new FormData();
    //form_data.append("audio", audioFile);
    form_data.append("audio", audio64_uri);


    const request = new Request(
        "/chat/mock_post_audio/",
        {headers: {'X-CSRFToken': csrftoken},
        }
    );

    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: form_data,
    }).then(function(response){
        response.json().then(function(data){
            //console.log(data)
            //const audio_base64 = data["audio"];
            const audio_text = data["text"];
            resetInputValue(audio_text);
            //const audio = new Audio("data:audio/webm; codecs=opus;base64," + audio_base64);
            //const audio = new Audio(data["audio"]);
            //audio.play();
        });
    });
}

function resetInputValue(text){
    const input = document.querySelector("#text_input");
    input.value = text;
}

//detect selected text
function sending_selected_texts_setup(){
    const chat_area = document.querySelector(".chat_area");
    chat_area.addEventListener("mouseup", () => {
        const selected_DOM = window.getSelection();
        if(!selected_DOM.isCollapsed){
            if(selected_DOM.anchorNode.parentElement.classList.contains("lines")
                && selected_DOM.anchorNode === selected_DOM.focusNode){
                    text = selected_DOM.toString().trim();
                    context = selected_DOM.anchorNode.parentElement.textContent.trim();
                    //console.log("selected text: " + text);
                    //console.log("context :" + context);
                    if(text){
                        range = selected_DOM.getRangeAt(0)
                        rect = range.getBoundingClientRect();
                        pos_x_y = [rect.x,rect.y+window.pageYOffset]
                        sendSelected(text, context, pos_x_y);
                    }
            } 
        }
    });
}

//send word to server
function sendSelected(text, context, pos_x_y){
    const form_data = new FormData();
    const selected_JSON = JSON.stringify({"text": text, "context": context});
    form_data.append("selected", selected_JSON);

    const request = new Request(
        "/vocab/mock_post_selected/",
        {headers: {'X-CSRFToken': csrftoken},
        }
    );

    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: form_data,
    }).then(function(response){
        response.json().then(function(data){
            //console.log(data);
            addWordTooltip(data,context);
            addWordTooltip_show(pos_x_y)
            document.addEventListener('click', (e)=>{
                if(!e.target.closest('.tooltip')) {
                    addWordTooltip_hide()
                }
            })
        });
    });
}

function addEntry(speaker, lines, isAssistant, audio_uri){
    const chat_area = document.querySelector(".chat_area");
    const template_assistant = document.querySelector("#chat_entry_template_assistant");
    const template_user = document.querySelector("#chat_entry_template_user");
    const template = isAssistant ? template_assistant : template_user;
    const clone = template.content.cloneNode(true);
    clone.querySelector(".speaker").innerHTML = speaker;
    clone.querySelector(".lines").innerHTML = lines;
    clone.querySelector(".voice").src = audio_uri;
    chat_area.appendChild(clone);
}

function updateEntries(data){
    global_chat_history_list = data["chat"]
    const adding_data = (data["chat"]).slice(data["chat"].length - 2);
    adding_data.forEach(entry => {
        addEntry(entry["speaker"], entry["lines"], entry["isAssistant"], entry["audio"]);
    });
    console.log(global_chat_history_list)
}


function addWordTooltip(data,context){
    tooltip = document.querySelector("#tooltip_instance")
    tooltip.querySelector(".word").innerHTML = data["text"];
    tooltip.querySelector(".meanings").innerHTML = data["meaning"];
    tooltip.querySelector(".context").innerHTML = context;
    if(data["word_falg"]){
        tooltip.querySelector(".category").innerHTML = data["category"];
        tooltip.querySelector("#register_button").style.display = "";
    }else{
        tooltip.querySelector(".category").innerHTML = "翻訳";
        tooltip.querySelector("#register_button").style.display = "none";
    }
}

function addWordTooltip_show(pos_x_y){
    const x = pos_x_y[0]
    const y = pos_x_y[1]
    tooltip = document.querySelector("#tooltip_instance")
    tooltip.style.setProperty("top", ("calc(1.5rem + " + y + "px)"));
    tooltip.style.setProperty("left", ("calc(1rem + " + x + "px)"));
    //tooltip.style.left = x + "px";
    tooltip.style.visibility = "visible";
}

function addWordTooltip_hide(){
    tooltip = document.querySelector("#tooltip_instance")
    tooltip.style.visibility = "hidden";
    tooltip.querySelector("#register_button").style.display = "none";
}

function registerWords(){
    const form_data = new FormData();
    const tooltip = document.querySelector("#tooltip_instance")
    const context = tooltip.querySelector(".context").textContent.trim();
    const text = tooltip.querySelector(".word").textContent.trim();
    const selected_JSON = JSON.stringify({"text": text, "context": context});
    form_data.append("selected", selected_JSON);
    //console.log(selected_JSON)
    console.log("registered")
    const request = new Request(
        "/vocab/mock_add_word/",//TODO: change to registering URL
        {headers: {'X-CSRFToken': csrftoken},
        }
    );

    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: form_data,
    }).then(function(response){
        response.json().then(function(data){
            console.log(data);
            //give feedback
            if(data["saved"]){
                alert("saved!");
            }else{
                alert("failed to save...");
            }
        });
    });
}


function initializeChat(audio){
    const request = new Request(
        "/chat/mock_init/",
        {headers: {'X-CSRFToken': csrftoken},
        }
    );

    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: "",
    }).then(function(response){
        response.json().then(function(data){
            console.log("initialized");
            console.log(data["chat"])
            global_chat_history_list = data["chat"];
            entry = data["chat"][0];
            addEntry(entry["speaker"], entry["lines"], entry["isAssistant"], entry["audio"]);
            console.log(global_chat_history_list)
            const audio_base64_uri = data["chat"][data["chat"].length-1]["audio"]
            //audio.src = ("data:audio/webm; codecs=opus;base64," + audio_base64);//TODO: enable autoplay for safari
            audio.src = audio_base64_uri;
            audio.play();
        });
    });
}

function onSubmit(){
    const button = document.querySelector("#submit_button");
    button.click();
    return false;
}

function setButtonDisabled(setDisabled){
    const button = document.querySelector("#submit_button");
    button.disabled = setDisabled;
}

function setStartButton(){
    const button = document.querySelector("#start_button");
    setButtonDisabled(true);
    button.addEventListener("click",(e)=>{
        e.preventDefault();
        const audio = new Audio();
        initializeChat(audio);
        button.style.display = "none";
        setButtonDisabled(false);
    });
}

function replayAudio(elem){
    elem.parentNode.querySelector(".voice").play();
}

//load functions after DOM is loaded
document.addEventListener('DOMContentLoaded', function(){


    /**read form, write on console*/
    const submit_button = document.querySelector("#submit_button");
    const form = document.querySelector("#form1");
    submit_button.addEventListener("click", (e) => {
        e.preventDefault();
        const audio = new Audio();
        submit_text_with_chat_history(e,form,audio);
    });

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        console.log('getUserMedia supported.');
        navigator.mediaDevices
            .getUserMedia (
                // constraints - only audio needed for this app
                {
                    audio: true
                }
            ).then(function(stream) {
                const mediaRecorder = new MediaRecorder(stream);
                mic_setup(mediaRecorder);
                let audioChunks = [];
                mediaRecorder.ondataavailable = function(e) {
                    audioChunks.push(e.data);
                };
                mediaRecorder.addEventListener("stop", function(e){
                    audio_to_base64(e, audioChunks)
                    audioChunks = [];
                });
            }).catch(function(err) {
                console.log('The following getUserMedia error occured: ' + err);
            });
    } else {
        console.log('getUserMedia not supported on your browser!');
    }
    sending_selected_texts_setup();

    document.querySelector("#register_button").addEventListener("click",(e)=>{
        e.preventDefault();
        registerWords();
    })

    setStartButton();
 });

window.addEventListener("beforeunload", function (e) {
    e.preventDefault();
    e.returnValue = "";
});