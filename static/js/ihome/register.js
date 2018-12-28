function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode(){
 $.ajax({
    url: "/user/get_code/",
    type: "GET",
    dataType: "json",
    success: function(data){
        if(data.code == '200'){
            $('#yanzhengma img').attr('src','data:image/jpg;base64,'+data.img)
            $('#yanzhengma img').css('display','inline-block')
        }
     }
});
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imageCode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $(".form-register").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        imageCode = $("#imageCode").val();
        password = $("#password").val();
        password2 = $("#password2").val();
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
        if (password != password2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }
        $.ajax({
            url:'/user/register/',
            type:'POST',
            dataType:'json',
            data:{'mobile':mobile, 'imageCode':imageCode,'password':password, 'password2':password2},
            success: function(msg){
                if(msg.code == '200'){
                    location.href='/user/login/';
                }
                if(msg.code == '10001' || msg.code == '10004'){
                    $('#mobile-err').text(msg.msg);
                    $('#mobile-err').css('display', 'block');
                }
                if(msg.code == '10002'){
                    $('#image-code-err').text(msg.msg);
                    $('#image-code-err').css('display', 'block');
                }
                if(msg.code == '10003'){
                    $('#password2-err').text(msg.msg);
                    $('#password2-err').css('display', 'block');
                }
                generateImageCode();
            },
            error: function(msg){
                console.log(msg)
            }
        });

    });
})


