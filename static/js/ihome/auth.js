function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){});
            location.reload();
        },1000) 
    });
}

// 当页面加载完成之后，对服务器发送get请求，获取用户的数据，当这个数据已经存在的时候，则不能再进行输入，则将input标签的disabled属性设置成disabled
//就是讲input标签隐藏掉，因为实名认证只能认证一次
$(document).ready(function(){
    $.get('/user/auths/',function (data) {
    $('#real-name').val(data.id_name);
    $('#id-card').val(data.id_card);
    if(data.id_name!=null && data.id_card!= '') {
        $('.btn-success').hide();
        $('#real-name').attr('disabled','disabled');
        $('#id-card').attr('disabled','disabled');
        $('.error-msg').hide();
    }
    });
    $('#form-auth').submit(function (){
        $.ajax({
            url:'/user/auths/',
            type:'put',
            data:{
                id_name:$('#real-name').val(),
                id_card:$('#id-card').val()
            },
            dataType:'json',
            success:function (data) {
                if(data.code=='200'){
                    $('.btn-success').hide();
                    $('.error-msg').hide();
                    $('#real-name').attr('disabled','disabled');
                    $('#id-card').attr('disabled','disabled');
                    showSuccessMsg();
                }else{
                    $('.error-msg').html('<i class="fa fa-exclamation-circle"></i>'+data.msg);
                    $('.error-msg').show();
                }
            }
        });
        return false
    });
})

