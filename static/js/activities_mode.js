document.addEventListener('DOMContentLoaded', function () {


    const searchForm = document.getElementById('search_FORM');
    searchForm.addEventListener('submit', function(event) {
        // 在提交表单时，将选择模式设置为 'all_choice'
        // event.preventDefault();
        setActiveChoice('all_choice');
    });
});

$(document).ready(function () {
    // 恢复用户上次选择的模式
    var activeChoice = localStorage.getItem('activeChoice');
    if (activeChoice) {
        setActiveChoice(activeChoice);
    }
});

function setActiveChoice(choice) {
    var allChoice = $('#all_choice');
    var artChoice = $('#art_choice');
    var entertainmentChoice = $('#entertainment_choice');
    var foodChoice = $('#food_choice');
    var leisureChoice = $('#leisure_choice');
    var sportChoice = $('#sport_choice');
    var otherChoice = $('#other_choice');
    var choiceMode = $('#choiceMode');

    if (choice === 'all_choice') {
        allChoice.show();
        artChoice.hide();
        entertainmentChoice.hide();
        foodChoice.hide();
        leisureChoice.hide();
        sportChoice.hide();
        otherChoice.hide();
        choiceMode.text('All Activities');
    } else if (choice === 'art_choice') {
        allChoice.hide();
        artChoice.show();
        entertainmentChoice.hide();
        foodChoice.hide();
        leisureChoice.hide();
        sportChoice.hide();
        otherChoice.hide();
        choiceMode.text('Art');
    } else if (choice === 'entertainment_choice') {
        allChoice.hide();
        artChoice.hide();
        entertainmentChoice.show();
        foodChoice.hide();
        leisureChoice.hide();
        sportChoice.hide();
        otherChoice.hide();
        choiceMode.text('Entertainment');
    } else if (choice === 'food_choice') {
        allChoice.hide();
        artChoice.hide();
        entertainmentChoice.hide();
        foodChoice.show();
        leisureChoice.hide();
        sportChoice.hide();
        otherChoice.hide();
        choiceMode.text('Food');
    } else if (choice === 'leisure_choice') {
        allChoice.hide();
        artChoice.hide();
        entertainmentChoice.hide();
        foodChoice.hide();
        leisureChoice.show();
        sportChoice.hide();
        otherChoice.hide();
        choiceMode.text('Leisure');
    } else if (choice === 'sport_choice') {
        allChoice.hide();
        artChoice.hide();
        entertainmentChoice.hide();
        foodChoice.hide();
        leisureChoice.hide();
        sportChoice.show();
        otherChoice.hide();
        choiceMode.text('Sport');
    } else if (choice === 'other_choice') {
        allChoice.hide();
        artChoice.hide();
        entertainmentChoice.hide();
        foodChoice.hide();
        leisureChoice.hide();
        sportChoice.hide();
        otherChoice.show();
        choiceMode.text('Other');
    }


    // 保存用户选择的模式到本地存储
    localStorage.setItem('activeChoice', choice);
}