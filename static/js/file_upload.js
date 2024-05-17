// 获取 HTML 元素
// let fileSubmit = document.getElementById("fileSubmit");
let audioInput = document.getElementById("audioInput");
let audioFile = document.getElementById("audioFile");
const fileNameDisplay = document.getElementById("fileNameDisplay");

// 当文件选择更改时播放文件
audioInput.addEventListener("change", function() {
    // 清空 fileNameDisplay 内的内容
    fileNameDisplay.innerHTML = "";

    // 检查是否选择了文件
    const files = audioInput.files;

    if (files.length > 0) {
        const prefixSpan = document.createElement("span");

        // 判断文件数量并设置前缀文本
        if (files.length === 1) {
            prefixSpan.textContent = "Your uploaded audio file is: ";
        } else {
            prefixSpan.textContent = "Your uploaded audio files are: ";
        }

        fileNameDisplay.appendChild(prefixSpan);

        // 遍历所有上传的文件
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileNameSpan = document.createElement("span");

            // 设置文件名文本
            fileNameSpan.textContent = file.name;
            fileNameSpan.style.color = "#9a78ff"; // 设置文件名颜色
            fileNameSpan.style.fontStyle = "italic"; // 设置文件名斜体

            // 添加文件名前的分隔符
            if (i > 0) {
                const separator = document.createElement("span");
                separator.textContent = ", ";
                fileNameDisplay.appendChild(separator);
            }

            fileNameDisplay.appendChild(fileNameSpan);
        }

        fileNameDisplay.style.display = "inline"; // 显示文件名显示元素
    } else {
        // 未选择文件时隐藏文件名显示元素
        fileNameDisplay.style.display = "none";
    }
});


// 文件上传按钮点击事件
// fileSubmit.onclick = function() {
//     const file = audioInput.files[0];
//
//     if (!file) {
//         alert("No Uploaded file! Please upload your audio file before submitting!");
//         return; // 如果 title、weather、sleepDuration 不为空但 audioBlob 为空，阻止表单提交
//     }
//
//
//     // 使用 FormData 对象创建表单数据
//     const formData = new FormData();
//     formData.append("audio", file);
//
//     // 发送请求
//     fetch("/dream/upload_audio", {
//         method: "POST",
//         body: formData,
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log(data);
//         alert("Your dream audio file uploaded successfully!"); // 提示用户上传成功
//         // 根据需要跳转页面
//         window.location.href = "/dream/my_dream";
//     })
//     .catch(error => {
//         console.error(error);
//         alert("Upload failed! Please try again.");
//     });
// };
