console.log("loaded");

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

function submit_text_with_chat_history(e,form, chat_history_list){
    e.preventDefault();
    //let chat_history_list = ;
    //console.log(form);
    let form_data = new FormData(form);
    form_data.append("chat_history", JSON.stringify(get_chat_history_list()));
    form_data.append("audio64" , audio64_stash.length > 0 ? audio64_stash : null)

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
        });
    });
}

let audio64_stash = "";

function audio_to_base64(e, audioChunks){
    e.preventDefault();
    const audioBlob = new Blob(audioChunks, {type: 'audio/webm; codecs=opus'});
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob)
    reader.onload = () =>{
        audio64 = (reader.result).split(",")[1];
        audio64_stash = audio64;
        sendAudioFile(audio64);
    }
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
    }
    function mic_off(){
        mediaRecorder.stop();
        console.log(mediaRecorder.state);
        console.log("recorder stopped");
        mic_button.style.background = "";
        mic_button.style.color = "";
        isRecording = false;
    }
    mic_button.addEventListener("click", function(e) {
        e.preventDefault();
        console.log("mic_button clicked");
        if(isRecording){
            mic_off();
        } else {
            mic_on();
            setTimeout(() => {
                mic_off();
            }, 60000);
        }
    });
}

//send audio file to server
function sendAudioFile(audio64){
    const form_data = new FormData();
    //form_data.append("audio", audioFile);
    form_data.append("audio", audio64);


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
            console.log(data)
            //const audio_base64 = data["audio"];
            const audio_text = data["text"];
            resetInputValue(audio_text);
            //const audio = new Audio("data:audio/webm; codecs=opus;base64," + audio_base64);
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
                    console.log("selected text: " + text);
                    console.log("context :" + context);
                    if(text){
                        range = selected_DOM.getRangeAt(0)
                        rect = range.getBoundingClientRect();
                        pos_x_y = [rect.x,rect.y]
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
            console.log(data);
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

function addEntry(speaker, lines, isAssistant){
    const chat_area = document.querySelector(".chat_area");
    const template_assistant = document.querySelector("#chat_entry_template_assistant");
    const template_user = document.querySelector("#chat_entry_template_user");
    const template = isAssistant ? template_assistant : template_user;
    const clone = template.content.cloneNode(true);
    clone.querySelector(".speaker").innerHTML = speaker;
    clone.querySelector(".lines").innerHTML = lines;
    chat_area.appendChild(clone);
}

function updateEntries(data){
    const adding_data = (data["chat"]).slice(data["chat"].length - 2);
    adding_data.forEach(entry => {
        addEntry(entry["speaker"], entry["text"], entry["isAssistant"]);
    });
}


function addWordTooltip(data,context){
    tooltip = document.querySelector("#tooltip_instance")
    tooltip.querySelector(".word").innerHTML = data["text"];
    tooltip.querySelector(".meanings").innerHTML = data["meaning"];
    tooltip.querySelector(".context").innerHTML = context;
    if(data["word_flag"]){
        tooltip.querySelector(".category").innerHTML = data["category"];
        tooltip.querySelector("#register_button").style.display = "";
    }
    document.body.appendChild(tooltip);
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
    console.log(selected_JSON)
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
        });
    });
}








//load functions after DOM is loaded
document.addEventListener('DOMContentLoaded', function(){


    /**read form, write on console*/
    const submit_button = document.querySelector("#submit_button");
    const form = document.querySelector("#form1");
    submit_button.addEventListener("click", (e) => {
        submit_text_with_chat_history(e,form);
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
 });
