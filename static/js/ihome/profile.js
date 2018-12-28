function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}



//阻止该button的默认提交事件，然后添加新的ajax请求
$(document).ready(function() {
    $('#form-avatar').submit(function (e) {
        e.preventDefault();
        // 给该标签添加ajax提交事件
        $(this).ajaxSubmit({
            url: "/user/profile/",
            type: "PATCH",
            dataType: "json",
            success: function (data) {
                if (data.code == '200') {
                    //给图片写入属性
                    $('#user-avatar').attr('src',data.url);
                    $('#image_error').css('display', 'none');
                } else {
                    $('#image_error').html('<i class="fa fa-exclamation-circle"></i>' +data.msg);
                    $('#image_error').css('display', 'block');
                }
            }
        });
         return false;
    });

    $('#form-name').submit(function (e) {
        e.preventDefault();
        var name = $('#user-name').val();
        $.ajax({
            url:'/user/profile/',
            type:'PUT',
            data:{'name':name},
            success:function (data) {
                if(data.code== '200'){
                    showSuccessMsg();
                }else{
                    $('#username_error').html('<i class="fa fa-exclamation-circle"></i>' +data.msg);
                    $('#username_error').css('display', 'block');
                }
            }
        });
        return false;
    });
    $('#user-name').on('focus',function () {
        $('#username_error').css('display', 'none');
    })
})

