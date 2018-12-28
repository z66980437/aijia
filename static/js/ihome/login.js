function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        password = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        $.ajax({
            url : '/user/login/',
            method : 'POST',
            data:{'mobile':mobile,'password':password},
            dataType:'json',
            success: function(msg){
                if(msg.code == '200'){
                    location.href='/user/my/';
                }
                if (msg.code == '9998') {
                    $('#mobile-err').text(msg.msg)
                    $('#mobile-err').css('display', 'block')
                }
                if (msg.code == '9999') {
                    $('#password-err').text(msg.msg)
                    $('#password-err').css('display', 'block')
                }
            },
            error: function(msg){
                console.log(msg)
            }
        });
    });

})