console.log("loaded");

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

document.addEventListener('DOMContentLoaded', function(){
    //create JSON of chat history
    const chat_history_entries = document.querySelector(".chat_area").querySelectorAll(".entry");
    //for each entry, get .speaker and .lines
    let chat_history_list = [];
    chat_history_entries.forEach(entry => {
        const speaker = entry.querySelector(".speaker");
        const speaker_name = speaker.innerHTML;
        const isAssistant = speaker.classList.contains('speaker_assistant');
        const lines = entry.querySelector(".lines").textContent;
        chat_history_list.push({
            "speaker": speaker_name,
            "isAssistant": isAssistant,
            "lines": lines,
        });
    });

    //read form, write on console
    const submit_button = document.querySelector("#submit_button");
    const form = document.querySelector("#form1");
    submit_button.addEventListener("click", () => {
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

    //notice for the mic_button is clicked
    const mic_button = document.querySelector("#mic_button");
    mic_button.addEventListener("click", () => {
        console.log("mic_button clicked");
    });
 });

