$(document).ready(function () {
    $("#captcha-btn").click(function () {
        $this = $(this);
        var email = $("#email").val();
        if (!email) {
            alert("Please enter your email first!");
        } else {
            $.ajax({
                url: "/user/captcha",
                method: "POST",
                data: {
                    "email": email,
                },
                success: function (res) {
                    var code = res["code"];
                    if (code === "200") {
                        // Turn off listening to events
                        $this.off("click");
                        alert("Verification code sent successfully!");
                        // Countdown to 30 seconds
                        var countDown = 60;
                        var timer = setInterval(function () {
                            countDown -= 1;
                            if (countDown > 0) {
                                $this.text(countDown + "seconds to resend");
                            } else {
                                $this.text("Get verification code");
                                // Turn on click events
                                $this.on("click");
                                // Stop the countdown
                                clearInterval(timer);
                            }
                        }, 1000);
                    } else {
                        alert(res["message"]);
                    }
                }
            });
        }
    });
});
