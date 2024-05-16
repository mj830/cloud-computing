let startRecord = document.getElementById("startRecord");
let stopRecord = document.getElementById("stopRecord");
let uploadRecord = document.getElementById("uploadRecord");
let audio = document.getElementById("audio");
let canvas = document.getElementById("waveformCanvas");
let canvasCtx = canvas.getContext("2d");

let recorder, stream;
let audioBlob; // 用来存储录音文件

async function startRecording() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);
        const audioChunks = [];

        // Visualization setup
        canvas.style.display = "block"; // Show visualization
        canvas.width = 400; // Set canvas width
        canvas.height = 200; // Set canvas height

        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const draw = () => {
            analyser.getByteTimeDomainData(dataArray);

            canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

            canvasCtx.lineWidth = 2;
            canvasCtx.strokeStyle = '#C9C6FF';

            canvasCtx.beginPath();

            const sliceWidth = canvas.width / dataArray.length;
            let x = 0;

            for (let i = 0; i < dataArray.length; i++) {
                const v = dataArray[i] / 128.0;
                const y = v * canvas.height / 2;

                if (i === 0) {
                    canvasCtx.moveTo(x, y);
                } else {
                    canvasCtx.lineTo(x, y);
                }

                x += sliceWidth;
            }

            canvasCtx.lineTo(canvas.width, canvas.height / 2);
            canvasCtx.stroke();

            requestAnimationFrame(draw);
        };

        draw(); // Start drawing the waveform

        // Recorder setup
        recorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        recorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audio.src = audioUrl;
            uploadRecord.disabled = false; // 允许用户上传录音
            alert("You have stopped the recording!!!");
            canvas.style.display = "none"; // Hide visualization when recording stops
        };

        recorder.start();
        alert("You have started recording, please describe your dream.");
    } catch (error) {
        console.error('Error accessing microphone:', error);
    }
}

startRecord.onclick = () => {
    startRecording();
    startRecord.disabled = true;
    stopRecord.disabled = false;
};

stopRecord.onclick = () => {
    recorder.stop();
    stream.getTracks().forEach(track => track.stop());
    startRecord.disabled = false;
    stopRecord.disabled = true;
};

// 当用户点击上传按钮时，调用此函数上传录音
uploadRecord.onclick = () => {
    const title = document.querySelector('input[name="title2"]').value; // 获取输入框的标题内容
    // const weather = document.querySelector('input[name="weather2"]').value;
    const weatherSelect = document.querySelector('select[name="weather2"]');
    const weather = weatherSelect.options[weatherSelect.selectedIndex].value;
    const sleepDurationSelect = document.querySelector('select[name="sleepDuration2"]');
    const sleepDuration = sleepDurationSelect.options[sleepDurationSelect.selectedIndex].value;
    console.log(title,weather)
    if (title.trim() === '' || weather.trim() === '' || sleepDuration.trim() === '') {
        if (!audioBlob) {
            alert("Please fill in all required fields!");
            return; // 如果 title、weather、sleepDuration 和 audioBlob 均为空，阻止表单提交
        } else {
            alert("Please fill in all required fields!");
            return; // 如果 title、weather、sleepDuration 其中之一为空但 audioBlob 不为空，阻止表单提交
        }
    } else {
        if (!audioBlob) {
            alert("No Record file! Please record before submitting!");
            return; // 如果 title、weather、sleepDuration 不为空但 audioBlob 为空，阻止表单提交
        }
    }

    sendAudioToServer(audioBlob, title, weather, sleepDuration); // 将标题内容传递给 sendAudioToServer 函数
};

// 发送音频到服务器的函数
function sendAudioToServer(audioBlob, title, weather, sleepDuration) {
    const formData = new FormData();
    formData.append("audio", audioBlob, "audio.webm");
    formData.append("title", title); // 添加标题内容到 FormData 对象中
    formData.append("weather", weather);
    formData.append("sleepDuration", sleepDuration);
    console.log(title, weather, audioBlob, sleepDuration)

    fetch("/dream/upload_audio", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert("Audio Upload Successfully！");
        window.location.href = "/dream/my_dream";
    })
    .catch(error => {
        console.error(error);
        alert("Upload Failed! Please try again!");
    });
}
