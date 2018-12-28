// 分页
function paginate(page,pages,iter_pages) {
    var my_house_html = template('my_house_panigate_script',{pages: pages, page:page, iter_pages:iter_pages});
     $('.pagination').html(my_house_html)
}

//获取用户信息，判断是否进行过实名认证
$(function () {
    now_page = window.location.search
    $.get('/house/my_auth/'+now_page,function (data) {
        if(data.code== '200'){
            //已经完成实名认证
            $('#houses-list').show();
            var html=template('house_list',{hlist:data.hlist});
            //给父节点添加子节点
            $('#houses-list').append(html);
            paginate(data.paginate_page, data.paginate_pages, data.iter_pages);
        }else{
            //未实名认证
            $('#auth-warn').show();
        }
    });
});
