$(document).ready(function () {
    $(".button-collapse").sideNav();
    $('.parallax').parallax();
    $('#login').click(function () {

        var formDataJoin = new FormData();
        formDataJoin.append('name', $('#name').removeClass('invalid').val());
        formDataJoin.append('password', $('#password').removeClass('invalid').val());
        $.ajax({
            url: '/api/login',
            type: 'POST',
            data: formDataJoin,
            contentType: false,
            processData: false,
            success: function (result) {
                if (result['status'] == 'lacked') {
                    result['msg'].forEach(function (v, k) {
                        $('#' + v).removeClass('valid').addClass('invalid')
                    })
                }
                if (result['status'] == 'OK') {
                    window.location.href = "/admin";
                }

            }

        })
    });
});
