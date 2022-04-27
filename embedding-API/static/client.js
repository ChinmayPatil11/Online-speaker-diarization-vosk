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
var spk_name = 'Doctor'
//const spk_array = [-0.672707, -0.047609, 0.468263, -0.821483, -0.217943, 0.982222, -1.017249, 0.233793, 1.179950, -0.488690, 0.174299, -0.017398, -0.493793, -0.093906, -0.361359, 0.739860, 1.460465, 0.749960, 1.401321, 0.971038, -0.633923, 0.876363, 1.306341, -0.157411, -0.564482, -0.711235, -0.872928, -1.176448, 0.421054, 1.304956, -1.055351, -0.837502, 1.448099, -1.413884, -0.123753, -1.720728, 0.299573, -0.422326, -0.811393, 1.151599, 1.629723, 0.327594, 0.867519, 0.540016, -1.221978, -0.438555, 0.199967, -0.441308, 1.728791, 0.685041, -0.618314, 1.377646, -1.502081, 1.235973, -0.064608, 0.410782, -0.063814, -0.828358, -0.099752, -0.750580, 0.521286, 1.379840, 1.159643, 0.297913, -0.914591, -1.931818, -1.029044, 0.088539, -0.181218, 3.606820, -0.662383, -2.047054, -1.047408, 0.331896, 1.017010, -0.360542, -1.164094, -0.346461, 0.394493, -0.342114, 0.899842, -0.940411, 0.404496, 0.394852, -1.049101, -1.854556, 1.236909, 0.200333, -0.687299, 0.421603, -0.489067, -1.133949, -0.320870, 0.312042, -0.366211, -0.803710, 0.132593, -1.342289, 0.699737, 1.178294, -0.219750, -0.817095, 0.347680, -0.635192, -0.178326, -1.838724, -0.596655, 0.045482, -1.598971, 0.306272, -1.903477, 0.622982, 2.377664, -0.944780, 2.666173, 1.099456, -0.132282, -0.239916, -0.903252, -0.468311, 1.279603, 0.344250, -0.918579, -0.486798, -0.221668, 1.253554, -1.539697, 0.539431];
// og
const spk_array = [-0.701766, 0.313454, 0.285104, -1.157942, -1.025656, 0.359487, -0.397543, -0.738973, 1.633481, -0.077619, 0.011297, -0.023481, -0.990958, -0.921590, -0.902737, -0.254562, 0.478593, 0.081016, 2.043904, 0.215783, -0.296242, 2.049364, 1.969494, -0.381765, -1.040035, -0.636572, -0.671292, -1.647781, 0.562115, 0.728833, -0.559134, -1.370062, 0.188702, -1.041054, 0.293849, -2.449665, 1.236091, 1.086694, -0.957984, 0.546023, 0.734656, 1.330279, 0.438040, 0.081506, -0.930533, 1.371469, 0.052700, -0.599288, 0.187568, 0.868085, 0.107612, 0.932629, 0.196172, 1.043293, -0.365125, 0.157180, 0.250023, -0.250561, -0.656860, -1.249357, 0.954533, 0.354545, 0.005050, -1.438345, -0.137508, -0.992737, -0.565105, 0.281953, -1.195023, 2.748891, -0.586424, -2.366060, -0.605496, -0.659102, 0.303107, 0.115082, -1.137468, -0.366137, -0.188624, -1.305033, 0.387655, -1.230271, -0.223709, -0.165224, -0.592402, -0.331704, 0.071005, 1.486784, 0.599618, -0.233855, 0.503320, -0.620836, -0.224790, 0.052773, -0.929046, 0.081823, -0.366624, -1.166075, 0.810104, 2.258941, 0.908314, -0.301767, -0.180385, -1.584045, -0.037256, -1.478272, 0.285490, -1.095387, -0.696070, -0.104534, -1.608816, 0.968370, 1.192020, -1.002699, 2.961337, 0.216760, -0.145203, 1.073298, -0.002436, -0.253612, 0.700424, 1.986816, -1.314074, 1.693625, 0.702341, 1.354820, -2.112917, 0.155190]
//const spk_array = [-0.627471, 0.233518, -0.036421, -0.612026, -0.856409, -0.42471, -0.156001, -1.145928, 0.420171, -0.223704, 1.078933, 0.328102, -1.765677, -0.563932, 0.376271, 0.923973, 0.370996, 0.774722, 2.219754, 0.097758, -0.125401, 1.446539, 1.70555, -0.650565, 0.847408, -1.104186, -0.734282, -2.276538, 0.377283, -0.097009, -0.70963, -0.896112, -0.333233, -0.978881, -0.514981, -0.892428, 0.698612, 0.620577, -0.249454, 0.192746, 0.65744, 1.995431, 0.972619, -0.729996, -0.388628, 0.453595, 0.005919, -1.005641, 1.380846, 1.092274, 0.929975, -0.688762, -2.179149, 1.631618, 0.069097, -0.351963, 1.755905, -0.893287, 0.059224, -1.466929, 0.044531, 0.422845, 0.255074, -1.325903, -0.629481, -1.217768, -1.022184, 0.016126, -0.763786, 1.926774, -0.587863, -2.358357, -0.879979, 1.211813, -0.456017, 0.526188, -0.103051, -0.411619, 0.181453, 0.518209, 0.060176, -0.64694, -0.562274, 1.225398, -0.674513, 0.711186, 0.042938, 1.499472, -0.05928, 0.296919, 0.426169, -0.138544, -0.145528, -0.614359, -2.519151, -0.153244, -0.285164, -0.295279, 0.810506, 0.980929, 1.348859, -1.628181, 0.139292, -0.412345, 0.316658, -0.402544, 0.2516, 0.266766, -2.58591, 0.024123, -1.491179, 0.858061, 1.984157, -1.351458, 1.39619, 0.083226, -0.510234, 0.709808, 0.229031, -0.269491, 0.563194, 1.646309, -0.418847, 1.320732, -0.247325, 2.482199, -1.805388, -0.036377]
//const spk_array = [-0.451897, -0.444007, 1.268619, -0.332527, -0.977250, 0.173499, 0.359306, 0.025862, 0.373321, 0.748233, -0.522534, -0.155455, -0.857879, 1.317628, -1.871878, 1.482882, 2.398571, -0.082286, 0.231666, -0.026600, -0.666550, -0.997459, 1.259036, 0.756420, 0.118928, 0.511769, 0.617804, -1.007591, -1.026291, -1.426944, 0.464411, -0.678818, 1.110846, -0.029000, -0.206112, -1.056092, 0.168807, 0.968117, -1.708749, 2.707235, 0.280462, 0.548490, 2.132867, -0.020169, 1.226383, 0.322704, -0.877537, -2.895064, -0.832466, 0.580100, -0.011157, 0.398427, -0.516498, 0.444177, 1.746005, 0.852486, 0.521353, -0.577582, 0.305218, -2.094894, 0.634369, 0.680946, 0.151079, -0.439590, -1.524950, -0.760604, 0.470993, 1.252833, -0.008899, 0.195521, 0.296812, -0.327304, 1.206535, 1.011823, 1.183142, 2.517022, -1.594767, -1.389926, -0.971002, -0.468076, -0.349498, 0.399458, -1.054026, 0.318237, -0.102632, -0.657314, 0.241016, 1.755937, -1.241493, 0.881260, 1.199239, -0.256417, -0.275380, -0.444430, -0.448080, -0.093687, -0.255025, 0.746001, -0.642210, 0.899121, 0.530841, -0.846217, -0.794234, -0.924164, 0.039670, -0.678713, 0.904241, 1.670486, -0.177099, 1.099747, -2.455291, -0.073137, 0.708438, -0.530427, 0.069753, -1.002565, -0.365789, -1.234229, -0.953123, 1.129236, -0.153986, -0.036723, 0.139527, -1.587889, 0.495315, 1.006195, -1.447421, 1.569484]
function cosine_similarity(A,B) {
    var dotproduct=0;
    var mA=0;
    var mB=0;
    for(i = 0; i < A.length; i++){
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
    //console.log(spkarray)
    const spk_sig = spkarray
    distance = cosine_similarity(spk_array,spk_sig)
    console.log(distance)
    if (distance < 0.5){
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
        listItemHtmlStr = "<div>" + "<b>" + 'Patient' + "</b>" + ':' + str + "</div>\n";
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
                performRecvText(getData.text,getData.spk) //
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
