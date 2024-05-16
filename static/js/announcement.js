document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('.widget-comment .group-list  a');

    links.forEach(function(link) {
        link.addEventListener('click', function(event) {
            const userConfirmed = confirm('You are about to leave the current page, which may result in leaking personal information. Are you sure to continue?');

            if (!userConfirmed) {
                event.preventDefault();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const external_link = document.querySelectorAll('.members-list a');

    external_link.forEach(function(link) {
        link.addEventListener('click', function(event) {
            const userConfirmed = confirm('You are about to leave the current page, which may result in leaking personal information. Are you sure to continue?');

            if (!userConfirmed) {
                event.preventDefault();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const external_website = document.querySelectorAll('.author-heading a');

    external_website.forEach(function(link) {
        link.addEventListener('click', function(event) {
            const userConfirmed = confirm('You are about to leave the current page, which may result in leaking personal information. Are you sure to continue?');

            if (!userConfirmed) {
                event.preventDefault();
            }
        });
    });
});