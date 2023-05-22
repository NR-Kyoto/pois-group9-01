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

//load functions after DOM is loaded
document.addEventListener('DOMContentLoaded', function(){

    //create JSON of chat history
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


    /**read form, write on console*/
    const submit_button = document.querySelector("#submit_button");
    const form = document.querySelector("#form1");
    submit_button.addEventListener("click", (e) => {
        e.preventDefault();
        console.log(form);
        let form_data = new FormData(form);
        form_data.append("chat_history", JSON.stringify(chat_history_list));

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
                console.log(data);

            });
        });

        //form.action = "/chat/mock_post/";
        //form.submit();
        //console.log("form submitted");

    });

    // get mic input
    const mic_button = document.querySelector("#mic_button");
    
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        console.log('getUserMedia supported.');
        navigator.mediaDevices
            .getUserMedia (
                // constraints - only audio needed for this app
                {
                    audio: true
                }
            )
            .then(function(stream) {
                const mediaRecorder = new MediaRecorder(stream);
                let isRecording = false;
                mic_button.onclick = function(e) {
                    e.preventDefault();
                    if(isRecording){
                        mediaRecorder.stop();
                        console.log(mediaRecorder.state);
                        console.log("recorder stopped");
                        mic_button.style.background = "";
                        mic_button.style.color = "";
                        isRecording = false;
                    } else {
                        mediaRecorder.start();
                        console.log(mediaRecorder.state);
                        console.log("recorder started");
                        mic_button.style.background = "red";
                        mic_button.style.color = "black";
                        isRecording = true;
                        setTimeout(() => {
                            mediaRecorder.stop();
                            console.log(mediaRecorder.state);
                            console.log("recorder stopped");
                            mic_button.style.background = "";
                            mic_button.style.color = "";
                            isRecording = false;
                        }, 60000);
                    }
                };

                let audioChunks = [];

                mediaRecorder.ondataavailable = function(e) {
                    audioChunks.push(e.data);
                };

                
                mediaRecorder.addEventListener("stop", (e) => {
                    e.preventDefault();
                    const audioBlob = new Blob(audioChunks, {type: 'audio/webm; codecs=opus'});
                    const reader = new FileReader();
                    //audioFile = new File([audioBlob], "audio.wav", {type: 'audio/wav'});
                    reader.readAsDataURL(audioBlob)
                    reader.onload = () => {
                        audio64 = (reader.result).split(",")[1];
                        audioChunks = [];
                        sendAudioFile(audio64);
                    }
                    

                    //const audioUrl = URL.createObjectURL(audioBlob);
                    

                    /*to download audio file
                    const a = document.createElement("a");
                    document.body.appendChild(a);
                    a.style = "display: none";
                    a.download = "audio.wav";
                    a.href = audioUrl;
                    a.click();
                    document.body.removeChild(a);
                    delete a;
                    */

                    //to play audio
                    //const audio = new Audio(audioUrl);
                    //audio.play();
                });

            })
            .catch(function(err) {
                console.log('The following getUserMedia error occured: ' + err);
            });
    } else {
        console.log('getUserMedia not supported on your browser!');
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
                const audio_base64 = data["audio"];
                const audio = new Audio("data:audio/webm; codecs=opus;base64," + audio_base64);
                audio.play();
            });
        });
    }

    //notice for the mic_button is clicked
    mic_button.addEventListener("click", (e) => {
        e.preventDefault();
        console.log("mic_button clicked");
    });


    //detect selected text
    const chat_area = document.querySelector(".chat_area");
    chat_area.addEventListener("mouseup", () => {
        const selected_DOM = window.getSelection();
        if(!selected_DOM.isCollapsed){
            if(selected_DOM.anchorNode.parentElement.classList.contains("lines")
                && selected_DOM.anchorNode === selected_DOM.focusNode){
                    text = selected_DOM.toString();
                    context = selected_DOM.anchorNode.parentElement.textContent.trim();
                    console.log("selected text: " + text);
                    console.log("context :" + context);
                    sendSelected(text, context)
            } 
        }
    });

    //send word to server
    function sendSelected(text, context){
        const form_data = new FormData();
        const selected_JSON = JSON.stringify({"text": text, "context": context});
        form_data.append("selected", selected_JSON); 

        const request = new Request(
            "/chat/mock_post_selected/",
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
            });
        });
    }

 });

