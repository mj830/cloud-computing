document.addEventListener('DOMContentLoaded', function() {
    // 调用上面定义的函数
    initializeContentDisplay();
});

$(document).ready(function() {
    // 恢复用户上次选择的模式
    var activeTab = localStorage.getItem('activeTab');
    var activeEmotion = localStorage.getItem('activeEmotion');
    if (activeTab) {
        displayActiveContent(activeTab);
    }
    if (activeEmotion) { // 新增代码
        setActiveEmotion(activeEmotion); // 新增代码
    }
});

function displayActiveContent(tabId) {
    var textContent = $('#text');
    var voiceContent = $('#voice');
    var selectedOption = $('#modeOption');

    if (tabId === 'text') {
        textContent.show();
        voiceContent.hide();
        selectedOption.text('Text Input');
    } else if (tabId === 'voice') {
        textContent.hide();
        voiceContent.show();
        selectedOption.text('Voice Input');
    }

    // 保存用户选择的模式到本地存储
    localStorage.setItem('activeTab', tabId);
}
function setActiveEmotion(emotion) { // 新增函数
    var allContent = $('#all');
    var happyContent = $('#happy');
    var neutralContent = $('#neutral');
    var sadContent = $('#sad');
    var fearContent = $('#fear');
    var angryContent = $('#angry');
    var selectedOption = $('#selectedOption');

    if (emotion === 'all') {
        allContent.show();
        happyContent.hide();
        neutralContent.hide();
        sadContent.hide();
        fearContent.hide();
        angryContent.hide();
        selectedOption.text('All Emotions');
    } else if (emotion === 'happy') {
        allContent.hide();
        happyContent.show();
        neutralContent.hide();
        sadContent.hide();
        fearContent.hide();
        angryContent.hide();
        selectedOption.text('Happy');
    } else if (emotion === 'neutral') {
        allContent.hide();
        happyContent.hide();
        neutralContent.show();
        sadContent.hide();
        fearContent.hide();
        angryContent.hide();
        selectedOption.text('Neutral');
    } else if (emotion === 'sad') {
        allContent.hide();
        happyContent.hide();
        neutralContent.hide();
        sadContent.show();
        fearContent.hide();
        angryContent.hide();
        selectedOption.text('Sad');
    } else if (emotion === 'fear') {
        allContent.hide();
        happyContent.hide();
        neutralContent.hide();
        sadContent.hide();
        fearContent.show();
        angryContent.hide();
        selectedOption.text('Fear');
    } else if (emotion === 'angry') {
        allContent.hide();
        happyContent.hide();
        neutralContent.hide();
        sadContent.hide();
        fearContent.hide();
        angryContent.show();
        selectedOption.text('Angry');
    }

    // 保存用户选择的情绪到本地存储
    localStorage.setItem('activeEmotion', emotion);
}