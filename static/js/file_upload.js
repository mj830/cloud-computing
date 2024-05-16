// 获取 HTML 元素
let fileSubmit = document.getElementById("fileSubmit");
let audioInput = document.getElementById("audioInput");
let audioFile = document.getElementById("audioFile");
const fileNameDisplay = document.getElementById("fileNameDisplay");

// 当文件选择更改时播放文件
audioInput.addEventListener("change", function() {
    // 检查是否选择了文件
    const file = audioInput.files[0];

    if (file) {
        const fileUrl = URL.createObjectURL(file);
        audioFile.src = fileUrl; // 设置音频源为选定的文件

        const prefixSpan = document.createElement("span");
        const fileNameSpan = document.createElement("span");

        // 设置文本内容
        prefixSpan.textContent = "Your uploaded audio file is: ";
        fileNameSpan.textContent = file.name;


        fileNameSpan.style.color = "#9a78ff"; // 红色文件名
        fileNameSpan.style.fontStyle = "italic"; // 斜体字文件名

        // 清空 fileNameDisplay 内的内容
        fileNameDisplay.innerHTML = "";
        // 将两个元素添加到 fileNameDisplay
        fileNameDisplay.appendChild(prefixSpan);
        fileNameDisplay.appendChild(fileNameSpan);

        fileNameDisplay.style.display = "inline"; // 显示文件名显示元素
    } else {
        // 未选择文件时隐藏文件名显示元素
        fileNameDisplay.style.display = "none";
    }
});

// 文件上传按钮点击事件
fileSubmit.onclick = function() {
    // 获取表单数据
    const title = document.querySelector('input[name="title2"]').value;
    const weather = document.querySelector('select[name="weather2"]').value;
    const sleepDuration = document.querySelector('select[name="sleepDuration2"]').value;
    const file = audioInput.files[0];

    if (title.trim() === '' || weather.trim() === '' || sleepDuration.trim() === '') {
        if (!file) {
            alert("Please fill in all required fields!");
            return; // 如果 title、weather、sleepDuration 和 audioBlob 均为空，阻止表单提交
        } else {
            alert("Please fill in all required fields!");
            return; // 如果 title、weather、sleepDuration 其中之一为空但 audioBlob 不为空，阻止表单提交
        }
    } else {
        if (!file) {
            alert("No Uploaded file! Please upload your audio file before submitting!");
            return; // 如果 title、weather、sleepDuration 不为空但 audioBlob 为空，阻止表单提交
        }
    }

    // 使用 FormData 对象创建表单数据
    const formData = new FormData();
    formData.append("audio", file);
    formData.append("title", title);
    formData.append("weather", weather);
    formData.append("sleepDuration", sleepDuration);

    // 发送请求
    fetch("/dream/upload_audio", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert("Your dream audio file uploaded successfully!"); // 提示用户上传成功
        // 根据需要跳转页面
        window.location.href = "/dream/my_dream";
    })
    .catch(error => {
        console.error(error);
        alert("Upload failed! Please try again.");
    });
};
