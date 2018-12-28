function logout() {
   $.ajax({
    url:'/user/logout/',
    type:'DELETE',
    success:function(data){
        if(data.code=='200'){
            location.href='/house/index/';
        }
    }
   });
}


// 在进入页面的时候，对页面进行刷新的操作
$(document).ready(function(){
     $.ajax({
        url:'/user/user/',
        type:'GET',
        dataType:'json',
        success:function(data) {
            $('#user-avatar').attr('src',data.user.avatar);
            $('#user-name').html(data.user.name);
            $('#user-mobile').text(data.user.phone);
        },
        error:function(data){
            alert('请求失败')
        }
    });
})