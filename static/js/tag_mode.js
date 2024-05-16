
    document.addEventListener('DOMContentLoaded', function() {
    // 调用上面定义的函数
    filterForumTopicAdds();
});

        $(document).ready(function() {
            // 恢复用户上次选择的模式
            var activeTag = localStorage.getItem('activeTag');
            if (activeTag) {
                setActiveTag(activeTag);
            }
        });

        function setActiveTag(tag) {
            var allTag = $('#all_tag');
            var happyTag = $('#happy_tag');
            var neutralTag = $('#neutral_tag');
            var sadTag = $('#sad_tag');
            var fearTag = $('#fear_tag');
            var angryTag = $('#angry_tag');
            var tagMode = $('#tagMode');

            if (tag === 'all_tag') {
                allTag.show();
                happyTag.hide();
                neutralTag.hide();
                sadTag.hide();
                fearTag.hide();
                angryTag.hide();
                tagMode.text('All Emotions');
            } else if (tag === 'happy_tag') {
                allTag.hide();
                happyTag.show();
                neutralTag.hide();
                sadTag.hide();
                fearTag.hide();
                angryTag.hide();
                tagMode.text('Happy');
            } else if (tag === 'neutral_tag') {
                allTag.hide();
                happyTag.hide();
                neutralTag.show();
                sadTag.hide();
                fearTag.hide();
                angryTag.hide();
                tagMode.text('Neutral');
            } else if (tag === 'sad_tag') {
                allTag.hide();
                happyTag.hide();
                neutralTag.hide();
                sadTag.show();
                fearTag.hide();
                angryTag.hide();
                tagMode.text('Sad');
            } else if (tag === 'fear_tag') {
                allTag.hide();
                happyTag.hide();
                neutralTag.hide();
                sadTag.hide();
                fearTag.show();
                angryTag.hide();
                tagMode.text('Fear');
            } else if (tag === 'angry_tag') {
                allTag.hide();
                happyTag.hide();
                neutralTag.hide();
                sadTag.hide();
                fearTag.hide();
                angryTag.show();
                tagMode.text('Angry');
            }

            // 保存用户选择的模式到本地存储
            localStorage.setItem('activeTag', tag);
        }