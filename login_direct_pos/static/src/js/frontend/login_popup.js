/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
var registry = publicWidget.registry;

registry.LoginSigninPopup = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events: {
        'click .te_signin': '_te_signin',
        'click .open_reset_password': '_open_reset_password',
        'click .back_to_login': '_back_login',
        'click .close': '_close',
        'click .validate-sign-in': '_validateSignin',
        'click .open_signup': '_open_signup',
    },
    

    _te_signin: function () {
        let loginRegisterPopup = $("#loginRegisterPopup");
        loginRegisterPopup.modal().show().addClass("show modal_shown");
        loginRegisterPopup.find(".te_signup_section").show();

        
        // Show login form, hide others
        loginRegisterPopup.find(".te_login_form_wrapper").show();
        loginRegisterPopup.find(".te_signup_form_wrapper").hide();
        loginRegisterPopup.find(".te_reset_form_wrapper").hide();

        // // Close on outside click
       
        $(document).on('mouseup', function (e) {
    const $modal = $('#loginRegisterPopup');
    const $dialog = $modal.find('.modal-dialog');

    if ($modal.hasClass('show') && !$dialog.is(e.target) && $dialog.has(e.target).length === 0) {
        bootstrap.Modal.getInstance($modal[0]).hide();
    }
});
    },

    _open_reset_password: function (e) {
        e.preventDefault();
        let loginRegisterPopup = $("#loginRegisterPopup");
        loginRegisterPopup.find(".te_login_form_wrapper").hide();
        loginRegisterPopup.find(".te_signup_form_wrapper").hide();
        loginRegisterPopup.find(".te_reset_form_wrapper").show();
        loginRegisterPopup.find(".te_signup_section").hide();

    },

    _back_login: function (e) {
        e.preventDefault();
        let loginRegisterPopup = $("#loginRegisterPopup");
        loginRegisterPopup.find(".te_login_form_wrapper").show();
        loginRegisterPopup.find(".te_signup_form_wrapper").hide();
        loginRegisterPopup.find(".te_reset_form_wrapper").hide();
        loginRegisterPopup.find(".te_signup_section").show();

    },

    _close: function () {
        $("#loginRegisterPopup").hide();
    },

    _open_signup: function () {
        let loginRegisterPopup = $("#loginRegisterPopup");
        loginRegisterPopup.find(".te_login_form_wrapper").hide();
        loginRegisterPopup.find(".te_signup_section").hide();
        loginRegisterPopup.find(".te_signup_form_wrapper").show();
        // loginRegisterPopup.find(".te_signup_form_wrapper").style.flexBasis = '100%';
        loginRegisterPopup.find(".te_reset_form_wrapper").hide();
    },

    _validateSignin: function (e) {
        $("#loginRegisterPopup").modal();
        $("#loginRegisterPopup, .modal-body").show();
        $("#loginRegisterPopup").addClass("show modal_shown");

        var tab = e && $(e.currentTarget).attr('href');
        $('.nav-tabs a[href="' + tab + '"]').tab('show');
        
        $(document).mouseup(function (e) {
            if ($(e.target).closest(".modal-body").length === 0) {
                $("#loginRegisterPopup").removeClass("show modal_shown").hide();
            }
        });
    },
});

registry.LoginPopup = publicWidget.Widget.extend({
    selector: "#wrapwrap",
    events: {
        'submit #loginRegisterPopup .oe_login_form': '_customerLogin',
        'submit #loginRegisterPopup .oe_reset_password_form': '_resetPassword',
        'submit #loginRegisterPopup .oe_signup_form': '_customerRegistration',
        'click #btn_send_otp': '_onSendOTP', // Added this event
        'keyup #entered_otp': '_onCheckOTP',
    },

    start: function () {
        this.timerInterval = null;
        this.otpSent = false;
       
        
        return this._super.apply(this, arguments);
        
        
    },

    
    _onSendOTP: function (ev) {
    var self = this; // <--- This MUST be here
    var email = $('#signup_email').val();
     if (!email) {
            alert("Please enter email first");
            return;
        }
    
    $.ajax({
        url: '/web/signup/send_otp',
        type: 'POST',
        data: { 'email': email, 'csrf_token': odoo.csrf_token },
        success: function (res) {
            var data = JSON.parse(res);
            if (data.success) {
                $('#otp_section').removeClass('d-none');
                self._startTimer(); // Use 'self', not 'this'
            }
        }
    });
},

    // _startTimer: function () {
    //     var self = this;
    //     var timeLeft = 60;
    //     clearInterval(this.timerInterval); // Clear any existing timer
        
    //     this.timerInterval = setInterval(function () {
    //         timeLeft--;
    //         $('#timer').text(timeLeft);
    //         if (timeLeft <= 0) {
    //             clearInterval(self.timerInterval);
    //             $('#btn_send_otp').prop('disabled', false).text('Resend OTP');
    //             self.otpSent = false;
    //         }
    //     }, 1000);
    // },

    _startTimer: function () {
        var self = this;
        var timeLeft = 60;
        if (this.timerInterval) clearInterval(this.timerInterval);
        
        this.timerInterval = setInterval(function () {
            timeLeft--;
            $('#timer').text(timeLeft);
            const isValidIconHidden = $('#otp_icon_valid').hasClass('d-none');
            console.log('Timer tick:', timeLeft, 'Valid Icon Hidden:', isValidIconHidden);
            
            if (timeLeft <= 0 && !isValidIconHidden) {
                clearInterval(self.timerInterval);
                $('#btn_send_otp').prop('disabled', false).text('Resend OTP');
                // Optional: Hide icons if time runs out
                $('#otp_icon_valid, #otp_icon_invalid').addClass('d-none');
            }
        }, 1000);
    },
    
    // _onCheckOTP: function (ev) {
    //     var self = this;
    //     var otp = $(ev.currentTarget).val();
    //     var email = $('#signup_email').val();

    //     // Only check if user has finished entering 6 digits
    //     if (otp.length < 6) {
    //         $('#otp_icon_valid, #otp_icon_invalid').addClass('d-none');
    //         $('#entered_otp').css('border', '1px solid #ced4da'); // Reset border
    //         return;
    //     }

    //     $.ajax({
    //         url: '/web/signup/verify_otp',
    //         type: 'POST',
    //         data: {
    //             'otp': otp,
    //             'email': email,
    //             'csrf_token': odoo.csrf_token
    //         },
    //         success: function (res) {
    //             var data = JSON.parse(res);
    //             if (data.status === 'valid') {
    //                 // Correct Code: Green border + Tick
    //                 $('#entered_otp').css('border', '2px solid green');
    //                 $('#otp_icon_valid').removeClass('d-none');
    //                 $('#otp_icon_invalid').addClass('d-none');
    //                 self.otpVerified = true;
    //             } else {
    //                 // Wrong Code: Red border + X
    //                 $('#entered_otp').css('border', '2px solid red');
    //                 $('#otp_icon_invalid').removeClass('d-none');
    //                 $('#otp_icon_valid').addClass('d-none');
    //                 self.otpVerified = false;
    //             }
    //         }
    //     });
    // },

//     _onCheckOTP: function (ev) {
//     var self = this;
//     var otp = $(ev.currentTarget).val();
//     var email = $('#signup_email').val();
//     var signupBtn = $('.te_signup_button'); // Select your Submit button

//     if (otp.length < 6) {
//         $('#otp_icon_valid, #otp_icon_invalid').addClass('d-none');
//         signupBtn.prop('disabled', true); // Keep disabled while typing
//         return;
//     }

//     $.ajax({
//         url: '/web/signup/verify_otp',
//         type: 'POST',
//         data: {
//             'otp': otp,
//             'email': email,
//             'csrf_token': odoo.csrf_token
//         },
//         success: function (res) {
//             var data = JSON.parse(res);
//             if (data.status === 'valid') {
//                 // 1. Visual Success
//                 $('#entered_otp').css('border', '2px solid green');
//                 $('#otp_icon_valid').removeClass('d-none');
//                 $('#otp_icon_invalid').addClass('d-none');
                
//                 // 2. Stop Timer
//                 clearInterval(self.timerInterval);
                
//                 // 3. Enable Sign Up Button
//                 signupBtn.prop('disabled', false);
//                 self.otpVerified = true;
//             } else {
//                 // 1. Visual Failure
//                 $('#entered_otp').css('border', '2px solid red');
//                 $('#otp_icon_invalid').removeClass('d-none');
//                 $('#otp_icon_valid').addClass('d-none');
                
//                 // 2. Keep Button Disabled
//                 signupBtn.prop('disabled', true);
//                 self.otpVerified = false;
//             }
//         }
//     });
// },

_onCheckOTP: function (ev) {
    var self = this;
    var $otpInput = $(ev.currentTarget);
    var $emailInput = $('#signup_email');
    var $signupBtn = $('.te_signup_button');
    var otp = $otpInput.val();
    var email = $emailInput.val();

    if (otp.length < 6) {
        $('#otp_icon_valid, #otp_icon_invalid').addClass('d-none');
        $signupBtn.prop('disabled', true);
        return;
    }

    $.ajax({
        url: '/web/signup/verify_otp',
        type: 'POST',
        data: {
            'otp': otp,
            'email': email,
            'csrf_token': odoo.csrf_token
        },
        success: function (res) {
            var data = JSON.parse(res);
            if (data.status === 'valid') {
                // 1. Stop the Timer immediately
                clearInterval(self.timerInterval);
                
                // 2. Set UI to Read-Only (User cannot change email/otp anymore)
                // $otpInput.prop('readonly', true).css('background-color', '#e9ecef');
                $otpInput.addClass('otp-readonly');
                // $emailInput.prop('readonly', true).css('background-color', '#e9ecef');
                $('#btn_send_otp').addClass('d-none'); // Hide send button
                
                // 3. Visual Success & Enable Sign Up
                $('#otp_icon_valid').removeClass('d-none');
                $('#otp_icon_invalid').addClass('d-none');
                $otpInput.css('border', '2px solid green');
                $signupBtn.prop('disabled', false);
                
                self.otpVerified = true;
            } else {
                // Failure logic
                $('#otp_icon_invalid').removeClass('d-none');
                $otpInput.css('border', '2px solid red');
                $signupBtn.prop('disabled', true);
                self.otpVerified = false;
            }
        }
    });
},
    _customerLogin: function (e) {
        e.preventDefault();
        var $form = $(e.currentTarget);
        var submit_btn = $("#loginRegisterPopup .oe_login_form .te_login_button");
        var alert_succ_err = $("#loginRegisterPopup .oe_login_form .alert-success-error");

        // Show loading state
        // $(submit_btn).addClass('o_website_btn_loading disabled pe-none o_btn_loading').attr('disabled', 'disabled');

        $.ajax({
            url: '/web/login',
            type: 'POST',
            data: $($form).serialize(),
            dataType: 'text',
            success: function (data) {
                console.log('Login response data: ', data);

                var data_main;

                // Try to parse as JSON
                try {
                    data_main = JSON.parse(data);
                    console.log('Parsed JSON response: ', data_main);
                    
                    if (data_main.login_success && data_main.redirect) {
                        if (data_main.redirect != '1') {
                            if (typeof data_main.hide_msg == 'undefined' || !data_main.hide_msg) {
                                $(alert_succ_err).find(".alert-success").removeClass('d-none');
                            }
                            window.location.replace(data_main.redirect);
                        } else {
                            var errorMsg = data_main.error || 'Login failed';
                            $(alert_succ_err).find(".alert-danger").html(errorMsg).removeClass('d-none');
                            // $(submit_btn).removeClass('o_website_btn_loading disabled pe-none o_btn_loading').removeAttr('disabled');
                        }
                    } else if (!data_main.login_success && data_main.error) {
                        $(alert_succ_err).find(".alert-danger").html(data_main.error).removeClass('d-none');
                        // $(submit_btn).removeClass('o_website_btn_loading disabled pe-none o_btn_loading').removeAttr('disabled');
                    } else {
                        $(alert_succ_err).find(".alert-danger").html('Login failed: Unknown error').removeClass('d-none');
                        // $(submit_btn).removeClass('o_website_btn_loading disabled pe-none o_btn_loading').removeAttr('disabled');
                    }
                } catch (e) {
                    // Response is not JSON (likely HTML)
                    console.log('Response is not JSON, treating as HTML response',data.indexOf('alert-danger'));
                    var $htmlResponse = $(data);
                    var $errorMessage = $htmlResponse.find('.alert-danger').text().trim();

                    // Check if response contains error
                    if ($errorMessage) {
                        // Extract error message from HTML
                        var errorMatch = data.match(/<p[^>]*class="[^"]*alert[^"]*alert-danger[^"]*"[^>]*>([^<]*)<\/p>/);
                        var errorMsg = errorMatch ? errorMatch[1] : 'Login failed. Please try again.';
                        $(alert_succ_err).find(".alert-danger").html(errorMsg).removeClass('d-none');
                        // $(submit_btn).removeClass('o_website_btn_loading disabled pe-none o_btn_loading').removeAttr('disabled');
                    } else {
                        // Assume HTML response = successful redirect
                        window.location.reload();
                    }
                }
            },
            error: function (xhr, status, error) {
                console.log('AJAX error:', error);
                console.log('Response:', xhr.responseText);
                $(alert_succ_err).find(".alert-danger").html('An error occurred during login. Please try again.').removeClass('d-none');
                // $(submit_btn).removeClass('o_website_btn_loading disabled pe-none o_btn_loading').removeAttr('disabled');
            },
        });
    },

    //  _customerRegistration: function (e) {
    //     e.preventDefault()
    //     var $form = $(e.currentTarget)
    //     var alert_succ_err = $("#loginRegisterPopup .oe_signup_form .alert-success-error")
    //     var signup_btn = $("#loginRegisterPopup .oe_signup_form .te_signup_button")

    //     $.ajax({
    //         url: '/web/signup',
    //         type: 'POST',
    //         data: $($form).serialize(),
    //         async: false,
    //         dataType: 'text',
    //         success: function (data) {
    //             var data_main;

    //             try {
    //                 data_main = JSON.parse(data);
    //             } catch (e) {
    //                 // HTML response = successful signup
    //                 $(alert_succ_err).find(".alert-success").html('Registration successful!').removeClass('d-none');
    //                 setTimeout(function () {
    //                     window.location.reload();
    //                 }, 1000);
    //                 return;
    //             }

    //             if (data_main.login_success && data_main.redirect) {
    //                 $(alert_succ_err).find(".alert-success").removeClass('d-none');
    //                 window.location.reload()
    //             } else if (!data_main.login_success && data_main.error) {
    //                 $(alert_succ_err).find(".alert-danger").html(data_main.error).removeClass('d-none');
    //                 $(signup_btn).removeAttr('disabled').removeClass('fa-refresh fa-spin pe-none o_btn_loading');
    //             }
    //         },
    //         error: function (xhr, status, error) {
    //             console.log('Signup error:', error);
    //             $(alert_succ_err).find(".alert-danger").html('An error occurred during registration. Please try again.').removeClass('d-none');
    //             $(signup_btn).removeAttr('disabled').removeClass('fa-refresh fa-spin pe-none o_btn_loading');
    //         },
    //     });
    // },
_customerRegistration: function (e) {
    e.preventDefault();

    const $form = $(e.currentTarget);
    const alertBox = $("#loginRegisterPopup .oe_signup_form .alert-success-error");
    const signupBtn = $("#loginRegisterPopup .oe_signup_form .te_signup_button");

    alertBox.find('.alert').addClass('d-none');

    // signupBtn.attr('disabled', true);

    $.ajax({
        url: '/web/signup',
        type: 'POST',
        data: $form.serialize(),
        dataType: 'json',

        success: function (res) {

            if (res.success) {
                alertBox.find(".alert-success")
                    .html('Registration successful!')
                    .removeClass('d-none');

                setTimeout(function () {
                    window.location.href = res.redirect || '/web';
                }, 1000);

            } else {
                alertBox.find(".alert-danger")
                    .html(res.error || 'Registration failed')
                    .removeClass('d-none');

                // signupBtn.removeAttr('disabled');
            }
        },

        error: function () {
            alertBox.find(".alert-danger")
                .html('Server error. Please try again.')
                .removeClass('d-none');

            // signupBtn.removeAttr('disabled');
        }
    });
}
,
    _resetPassword: function (e) {
        e.preventDefault();
        var $form = $(e.currentTarget);
        var alert_succ_err = $("#loginRegisterPopup .oe_reset_password_form .alert-danger");

        $.ajax({
            url: '/web/reset_password',
            type: 'POST',
            data: $($form).serialize(),
            dataType: 'text',
            success: function (data) {
                var data_main;

                try {
                    data_main = JSON.parse(data);
                } catch (e) {
                    // HTML response
                    alert('Password reset email sent successfully. Please check your email.');
                    $("#loginRegisterPopup").modal('hide');
                    return;
                }

                if (data_main.error) {
                    alert_succ_err.html(data_main.error).removeClass('d-none');
                } else if (data_main.message) {
                    alert('Password reset email sent successfully. Please check your email.');
                    setTimeout(function () {
                        $("#loginRegisterPopup").modal('hide');
                    }, 1500);
                }
            },
            error: function (xhr, status, error) {
                console.log('Reset password error:', error);
                alert('An error occurred. Please try again.');
            },
        });
    },


    async ForgotPassword() {
        try {
            this.forget_password_state.ResendOtp = false;
            // Generate a 6-digit OTP
            const otp = Math.floor(100000 + Math.random() * 900000);
            // Store the OTP in state with a timestamp
            this.forget_password_state.otp = otp;
            this.forget_password_state.otp_expiry = Date.now() + 60 * 1000; // 1 minute expiry
            // Fetch user email
            const loginData = await this.orm.searchRead("res.users", [['id', '=', user.userId]], ['login']);
            if (!loginData.length) {
                this.forget_password_state.message = "User  email not found.";
                return;
            }
            const userEmail = loginData[0].login;
            const otp_expiry_time = await this.orm.searchRead("res.users", [['id', '=', user.userId]], ['otp_expires']);

            
            const mail_creation = await rpc('/mail_creation', {
                subject: "Password Reset OTP",
                email_to: userEmail,
                body_html: `<p>Your OTP for password reset is: <strong>${otp}</strong></p> <p>This OTP is valid for ${otp_expiry_time[0].otp_expires} minute.</p>`

            });
            if (mail_creation.success) {
                this.notification.add("😊Mail sent successfully!✅", {
                    type: "success",
                });
            }

            this.forget_password_state.message = `OTP sent to ${userEmail}.`;

            this.forget_password_state.showOtpInput = true; // Show OTP input field
            if (otp_expiry_time[0].otp_expires === 0) {
                this.forget_password_state.countdown = 60; // Reset countdown
            }
            else {
                this.forget_password_state.countdown = otp_expiry_time[0].otp_expires * 60; // Reset countdown
            }

            const interval = setInterval(() => {
                if (this.forget_password_state.countdown > 0) {
                    this.forget_password_state.countdown--;
                    if (this.forget_password_state.countdown === 0) {
                        this.forget_password_state.showOtpInput = false
                        this.forget_password_state.ResendOtp = true
                    }

                } else {
                    clearInterval(interval);
                    this.forget_password_state.otp = null; // Invalidate OTP
                    this.forget_password_state.message = "OTP expired.";

                }
            }, 1000);

        } catch (error) {

            this.forget_password_state.message = "An error occurred while sending the OTP.";
        }
    },

    async validateOtp() {
        if (this.forget_password_state.otp_input === String(this.forget_password_state.otp)) {
            this.notification.add("OTP validated successfully!😊", {
                type: "success",
            });
            this.forget_password_state.reset_password_open = true;
        } else {

            this.notification.add("Invalid OTP😔!. Please try again.", {
                type: "danger",
            });
        }
    },
    

    
});


