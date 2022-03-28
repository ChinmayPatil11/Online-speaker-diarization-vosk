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

// function performRecvText(str) {
//     htmlStr = document.getElementById('list').innerHTML
//     listItemHtmlStr = "<div>" + str + "</div>\n";
//     htmlStr += listItemHtmlStr;
//     document.getElementById('list').innerHTML = htmlStr; 
// }
var spk_name = 'Chinmay'
// const spk_array = [-0.891684, -0.130390, 1.368452, 0.209146, -0.008386, 0.731464, 0.856996, 0.177553, 1.316603, 1.637085, -0.343187, 0.312126, -0.743909, 0.739855, -1.235087, 0.763318, 2.273797, -1.281516, 0.633055, -0.363363, -0.357788, 0.798039, 2.180442, 0.073130, -1.248862, 0.907360, 1.057549, -0.422057, -0.223189, -0.628476, -0.225164, 0.772648, 0.048056, -0.942278, -0.931837, -1.090142, 0.144348, 0.087319, 0.221830, 0.665487, 0.254930, 0.269606, 2.065293, -1.073388, -0.571818, 0.210244, -0.229996, -0.781241, -0.249673, 0.015498, 0.661528, 0.598963, -2.868980, -0.995247, 0.010761, 0.401485, 0.294723, 1.188548, -0.692303, -1.621983, 0.707475, 1.241550, -1.892505, -0.050193, -1.430929, 0.176586, -1.172653, 0.981032, -0.745509, 1.914016, 1.173026, -1.093171, -0.363510, 2.389551, -0.379826, -0.164128, -1.401292, -2.165837, -0.146951, 0.701714, 0.134839, -0.346942, 1.262309, 0.616360, -0.485776, -1.527874, -0.019630, 1.045032, -1.120039, 2.957704, 0.252245, 1.071884, -0.470590, 1.534587, -0.025618, 0.026857, 0.765317, 0.321612, -1.029844, 0.131316, -1.619612, 0.091628, -0.575747, -0.531433, 1.625027, 0.165951, 0.238775, 0.173136, 0.271162, 0.837523, -0.629695, -0.748469, 1.368035, -0.490642, 1.784966, 1.125934, -1.143485, -0.026725, 0.939180, -0.984909, -0.480827, 0.256497, -0.678360, 0.933805, 0.178494, 0.795298, -1.261258, 0.943654];
const spk_array = [-0.701766, 0.313454, 0.285104, -1.157942, -1.025656, 0.359487, -0.397543, -0.738973, 1.633481, -0.077619, 0.011297, -0.023481, -0.990958, -0.921590, -0.902737, -0.254562, 0.478593, 0.081016, 2.043904, 0.215783, -0.296242, 2.049364, 1.969494, -0.381765, -1.040035, -0.636572, -0.671292, -1.647781, 0.562115, 0.728833, -0.559134, -1.370062, 0.188702, -1.041054, 0.293849, -2.449665, 1.236091, 1.086694, -0.957984, 0.546023, 0.734656, 1.330279, 0.438040, 0.081506, -0.930533, 1.371469, 0.052700, -0.599288, 0.187568, 0.868085, 0.107612, 0.932629, 0.196172, 1.043293, -0.365125, 0.157180, 0.250023, -0.250561, -0.656860, -1.249357, 0.954533, 0.354545, 0.005050, -1.438345, -0.137508, -0.992737, -0.565105, 0.281953, -1.195023, 2.748891, -0.586424, -2.366060, -0.605496, -0.659102, 0.303107, 0.115082, -1.137468, -0.366137, -0.188624, -1.305033, 0.387655, -1.230271, -0.223709, -0.165224, -0.592402, -0.331704, 0.071005, 1.486784, 0.599618, -0.233855, 0.503320, -0.620836, -0.224790, 0.052773, -0.929046, 0.081823, -0.366624, -1.166075, 0.810104, 2.258941, 0.908314, -0.301767, -0.180385, -1.584045, -0.037256, -1.478272, 0.285490, -1.095387, -0.696070, -0.104534, -1.608816, 0.968370, 1.192020, -1.002699, 2.961337, 0.216760, -0.145203, 1.073298, -0.002436, -0.253612, 0.700424, 1.986816, -1.314074, 1.693625, 0.702341, 1.354820, -2.112917, 0.155190]
function cosine_similarity(A,B) {
    var dotproduct=0;
    var mA=0;
    var mB=0;
    for(i = 0; i < A.length; i++){ // here you missed the i++
        dotproduct += (A[i] * B[i]);
        mA += (A[i]*A[i]);
        mB += (B[i]*B[i]);
    }
    mA = Math.sqrt(mA);
    mB = Math.sqrt(mB);
    var similarity = (dotproduct)/((mA)*(mB))
    var distance = 1 - similarity
    return distance
}

function performRecvText(str,spkarray) {
    console.log(spkarray)
    const spk_sig = spkarray
    distance = cosine_similarity(spk_array,spk_sig)
    console.log(distance)
    if (distance < 0.6){
        console.log('Chinmay')
        htmlStr = document.getElementById('list').innerHTML
        listItemHtmlStr = "<div>" + "<b>" + spk_name + "</b>" + ':' + str + "</div>\n";
        //listItemHtmlStr = "<div>" + "<b>" + 'Person' + "</b>" + ':' + str + "</div>\n";
        htmlStr += listItemHtmlStr;
        document.getElementById('list').innerHTML = htmlStr; 
    }
    else{
        console.log('Person')
        htmlStr = document.getElementById('list').innerHTML
        listItemHtmlStr = "<div>" + "<b>" + 'Person' + "</b>" + ':' + str + "</div>\n";
        //listItemHtmlStr = "<div>" + "<b>" + spk_name + "</b>" + ':' + str + "</div>\n";
        htmlStr += listItemHtmlStr;
        document.getElementById('list').innerHTML = htmlStr; 
    }
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
            if(getData.text !== undefined) {
                //performRecvText(getData.text)
                console.log('Logging here')
                performRecvText(getData.text,getData.spk)
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
