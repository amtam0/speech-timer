var msg_box = document.getElementById( 'msg_box' ),
    button = document.getElementById( 'button' ),
    canvas = document.getElementById( 'canvas' ),
lang = {
    'mic_error': 'Error accessing the microphone', //Ошибка доступа к микрофону
    'press_to_start': 'Press to start recording', //Нажмите для начала записи
    'recording': 'Recording', //Запись
    'play': 'Play', //Воспроизвести
    'stop': 'Stop', //Остановить
    'download': 'Download', //Скачать
    'use_https': 'This application in not working over insecure connection. Try to use HTTPS'
},
time;


msg_box.innerHTML = lang.press_to_start;

if ( navigator.mediaDevices === undefined ) {
    navigator.mediaDevices = {};
}


if ( navigator.mediaDevices.getUserMedia === undefined ) {
    navigator.mediaDevices.getUserMedia = function ( constrains ) {
        var getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia
        if ( !getUserMedia )  {
            return Promise.reject( new Error( 'getUserMedia is not implemented in this browser' ) );
        }

        return new Promise( function( resolve, reject ) {
            getUserMedia.call( navigator, constrains, resolve, reject );
        } );
    }
}


if ( navigator.mediaDevices.getUserMedia ) {
    var btn_status = 'inactive',
        mediaRecorder,
        chunks = [],
        audio = new Audio(),
        mediaStream,
        audioSrc,
        type = {
            type: 'audio/wav'
        },
        // ctx,
        // analys,
        blob;

    button.onclick = function () {
        if ( btn_status == 'inactive' ) {
            start();
            button.style.backgroundColor='White'; //amtam0 white background onclick
        } else if ( btn_status == 'recording' ) {
            stop();
        }
    }

    function parseTime( sec ) {
        var h = parseInt( sec / 3600 );
        var m = parseInt( sec / 60 );
        var sec = sec - ( h * 3600 + m * 60 );

        h = h == 0 ? '' : h + ':';
        sec = sec < 10 ? '0' + sec : sec;

        return h + m + ':' + sec;
    }


    function start() {
        navigator.mediaDevices.getUserMedia( { 'audio': true } ).then( function ( stream ) {
            mediaRecorder = new MediaRecorder( stream );
            mediaRecorder.start();

            button.classList.add( 'recording' );
            btn_status = 'recording';

            msg_box.innerHTML = lang.recording;
        
            if ( navigator.vibrate ) navigator.vibrate( 150 );

            time = Math.ceil( new Date().getTime() / 1000 );


            mediaRecorder.ondataavailable = function ( event ) {
                chunks.push( event.data );
            }

            mediaRecorder.onstop = function () {
                stream.getTracks().forEach( function( track ) { track.stop() } );

                blob = new Blob( chunks, {type: 'audio/wav' });
                audioSrc = URL.createObjectURL( blob );
                audio.src = audioSrc;

                var READER = new FileReader();
                READER.readAsDataURL(blob); 
                
                var base64data;
                const start = async function() {
                    data = {
                            // min_thresh : parseFloat(form.querySelector('#thresh').value),
                            model_name : "",
                            body64 : base64data.split(',')[1],
                            }
                    // console.log(JSON.stringify(data));  
                    let response = await fetch('https://timer-occqj5qb5a-ey.a.run.app/', {
                            method: 'POST', // or 'PUT'
                            headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                            },
                            mode: 'cors',
                            body: JSON.stringify(data),
                    })
                    let text = await response.text(); // read response body as text
                    let results = JSON.parse(text);
                    console.log(results["raw"]);
                    console.log(results["result"]);
                    console.log(results["process_time"]);

                    nb_rounds = results["result"]["nb_rounds"];
                    Br = results["result"]["br"];
                    Wt = results["result"]["wt"];
                    // console.log(nb_rounds, Br, Wt);

                    // https://stackoverflow.com/a/36929709
                    var scope = angular.element(document.getElementById('wrapper')).scope();
                    scope.changeRounds(nb_rounds, '+0');
                    scope.changeTimeOff(Br, '+0');
                    scope.changeTimeOn(Wt, '+0');
                    document.getElementById('button').style.backgroundColor="#66bb6a";
                    
                    angular.element('#Updator').triggerHandler('click'); //https://stackoverflow.com/a/24334176 //refresh
                    
                };

                READER.onloadend = function() {
                    base64data = READER.result;  
                    // console.log(base64data.split(',')[1]);
                    start();
                    }
                
                chunks = [];
            }   

            
            
        } ).catch( function ( error ) {
            if ( location.protocol != 'https:' ) {
            msg_box.innerHTML = lang.mic_error + '<br>'  + lang.use_https;
            } else {
            msg_box.innerHTML = lang.mic_error; 
            }
            button.disabled = true;
        });
    }

    function stop() {
        mediaRecorder.stop();
        button.classList.remove( 'recording' );
        btn_status = 'inactive';
    
        if ( navigator.vibrate ) navigator.vibrate( [ 200, 100, 200 ] );

        var now = Math.ceil( new Date().getTime() / 1000 );

        var t = parseTime( now - time );

        msg_box.innerHTML = '<a href="#" style="font-size:3vw" onclick="play(); return false;" class="txt_btn">' + lang.play + ' (' + t + 's)</a><br>' +
                            '<a href="#" style="font-size:3vw" onclick="save(); return false;" class="txt_btn">' + lang.download + '</a>'
    }

    

    function play() {
        audio.play();
        msg_box.innerHTML = '<a href="#" style="font-size:3vw" onclick="pause(); return false;" class="txt_btn">' + lang.stop + '</a><br>' +
                            '<a href="#" style="font-size:3vw" onclick="save(); return false;" class="txt_btn">' + lang.download + '</a>';
    }

    function pause() {
        audio.pause();
        audio.currentTime = 0;
        msg_box.innerHTML = '<a href="#" style="font-size:3vw" onclick="play(); return false;" class="txt_btn">' + lang.play + '</a><br>' +
                            '<a href="#" style="font-size:3vw" onclick="save(); return false;" class="txt_btn">' + lang.download + '</a>'
    }

    // function roundedRect(ctx, x, y, width, height, radius, fill) {
    //     ctx.beginPath();
    //     ctx.moveTo(x, y + radius);
    //     ctx.lineTo(x, y + height - radius);
    //     ctx.quadraticCurveTo(x, y + height, x + radius, y + height);
    //     ctx.lineTo(x + width - radius, y + height);
    //     ctx.quadraticCurveTo(x + width, y + height, x + width, y + height - radius);
    //     ctx.lineTo(x + width, y + radius);
    //     ctx.quadraticCurveTo(x + width, y, x + width - radius, y);
    //     ctx.lineTo(x + radius, y);
    //     ctx.quadraticCurveTo(x, y, x, y + radius);
        
    //     ctx.fillStyle = fill;
    //     ctx.fill();
    // }
    

    function save() {
        var a = document.createElement( 'a' );
        a.download = 'record.wav';
        a.href = audioSrc;
                
        document.body.appendChild( a );
        a.click();

        document.body.removeChild( a );
        
    }

} else {
    if ( location.protocol != 'https:' ) {
    msg_box.innerHTML = lang.mic_error + '<br>'  + lang.use_https;
    } else {
    msg_box.innerHTML = lang.mic_error; 
    }
    button.disabled = true;
}


// function getBase64(file, onLoadCallback) {
//         return new Promise(function(resolve, reject) {
//             var reader = new FileReader();
//             reader.onload = function() { resolve(reader.result); };
//             reader.onerror = reject;
//             reader.readAsDataURL(file);
//         });
//     }

// formElem.onsubmit = async (e) => {
//     e.preventDefault();
//     // $body.addClass("loading");
//     var form = document.querySelector("#formElem");

//     var selectedfile = form.querySelector('#imguploader').files[0];
//     var promise = getBase64(selectedfile);
//     promise.then(function(image64) {
//         // console.log(image64);
//     });
//     let image64 = await promise

    
//     // $body.removeClass("loading");
// };

// var openFile = function(event) {
//             var input = event.target; 
//             var reader = new FileReader();

//             reader.onload = function(){
//             var arrayBuffer = reader.result;

//             var base64str = btoa( arrayBuffer);
//             console.log(base64str);
//             // document.getElementById("base64textarea").value  = 'data:audio/wav;base64,' + base64str;
//             };

//             // reader.readAsBinaryString(input.files[0]);
// };