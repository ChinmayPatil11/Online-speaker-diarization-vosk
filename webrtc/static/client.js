// peer connection
var pc = null;
var dc = null, dcInterval = null;

start_btn = document.getElementById('start');
stop_btn = document.getElementById('stop');
statusField = document.getElementById('status');

function btn_show_stop() {
    start_btn.classList.add('d-none');
    stop_btn.classList.remove('d-none');
}

function btn_show_start() {
    stop_btn.classList.add('d-none');
    start_btn.classList.remove('d-none');
    statusField.innerText = 'Press start';
}

function negotiate() {
    return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
    }).then(function () {
        return new Promise(function (resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }

                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function () {
        var offer = pc.localDescription;
        console.log(offer.sdp);
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function (response) {
        return response.json();
    }).then(function (answer) {
        console.log(answer.sdp,'answer');
        return pc.setRemoteDescription(answer);
    }).catch(function (e) {
        console.log(e);
        btn_show_start();
    });
}

function performRecvText(str) {
    htmlStr = document.getElementById('list').innerHTML
    listItemHtmlStr = "<div>" + str + "</div>\n";
    htmlStr += listItemHtmlStr;
    document.getElementById('list').innerHTML = htmlStr; 
}

function performRecvPartial(str) {
    document.getElementById('partial').innerText = str
    //document.getElementById('partial').innerText = str+spk
}

function performRecvPartial_spk(str,spk) {
    document.getElementById('partial').innerText = spk + str
}

function start() {
    btn_show_stop();
    statusField.innerText = 'Connecting...';
    var config = {
        sdpSemantics: 'unified-plan'
    };

    pc = new RTCPeerConnection(config);

    var parameters = {};

    dc = pc.createDataChannel('chat', parameters);
    dc.onclose = function () {
        clearInterval(dcInterval);
        console.log('Closed data channel');
        btn_show_start();
    };
    dc.onopen = function () {
        console.log('Opened data channel');
    };
    dc.onmessage = function (evt) {
        //console.log(evt,'evt');
        if(evt.data !== undefined) {
            getData =JSON.parse(evt.data)
            console.log(getData)
            if(getData.text !== undefined) {
                performRecvText(getData.text)
                //performRecvText(getData.text,getData.spk)
            } else if (getData.partial !== undefined) {
                performRecvPartial(getData.partial)
                //performRecvPartial(getData.partial,getData.spk)
            } 
        }
        statusField.innerText = 'Listening...';
    };
    // dc.onmessage = function (evt) {
    //     //console.log(evt,'evt');
    //     if(evt.data !== undefined) {
    //         getData =JSON.parse(evt.data)
    //         console.log(getData)
    //         if(getData.text !== undefined) {
    //             performRecvText(getData.text)
    //             //performRecvText(getData.text,getData.spk)
    //         } else if (getData.partial !== undefined) {
    //             performRecvPartial(getData.partial)
    //             //performRecvPartial(getData.partial,getData.spk)
    //         }
    //     }
    //     statusField.innerText = 'Listening...';
    // };

    pc.oniceconnectionstatechange = function () {
        if (pc.iceConnectionState == 'disconnected') {
            console.log('Disconnected');
            btn_show_start();
        }
    }

    var constraints = {
        audio: true,
        video: false,
    };

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        stream.getTracks().forEach(function (track) {
            pc.addTrack(track, stream);
        });
        return negotiate();
    }, function (err) {
        console.log('Could not acquire media: ' + err);
        btn_show_start();
    });
}

function stop() {

    // close data channel
    if (dc) {
        dc.close();
    }

    // close transceivers
    if (pc.getTransceivers) {
        pc.getTransceivers().forEach(function (transceiver) {
            if (transceiver.stop) {
                transceiver.stop();
            }
        });
    }

    // close local audio / video
    pc.getSenders().forEach(function (sender) {
        sender.track.stop();
    });

    // close peer connection
    setTimeout(function () {
        pc.close();
    }, 500);
}
