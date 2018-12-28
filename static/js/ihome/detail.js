function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    $(".book-house").show();
})

//document.location.search,这是一个Javascript函数，其作用是从当前页面的地址的参数中提取出指定的参数值。
//如：假设一个网页的地址最后是 test.html?aaa=123&bbb=456$ccc=789
//在这个页面中调用该函数，当key的值是aaa时，函数返回123；key是bbb时，返回456...
//document.location.search,这部分代码提取了前面页面地址中的参数列表，如：?aaa=123&bbb=456$ccc=789
$.get('/house/detail/', function(data){
    //从当前页面的地址参数中提取出指定的参数
    var search = document.location.search
    id = search.split('=')[1]
    $.get('/house/detail/' + id + '/', function(data){
        var banner_image = ''
        console.log(data.house)
        for(var i=0; i<data.house.images.length; i++){
            banner_li = '<li class="swiper-slide"><img style="height: 280px;width: 100%" src="' + data.house.images[i] + '"></li>'
            banner_image += banner_li
        }
        // swiper-wrapper表示轮播图的内容
        $('.swiper-wrapper').html(banner_image)
        // 新建一个轮播图
        var mySwiper = new Swiper ('.swiper-container', {
            loop: true,
            autoplay: 2000,
            autoplayDisableOnInteraction: false,
            pagination: '.swiper-pagination',
            paginationType: 'fraction'
        })

        $('.house-price').html('￥<span>' + data.house.price + '</span>/晚')

        $('.house-info-address').html(data.house.address)

        $('.house-title').html(data.house.title)

        $('.landlord-name').html('房东： <span>' + data.house.user_name + '</span>')

        $('.landlord-pic').html('<img src="' + data.house.user_avatar + '" width="60" height="60">')

        $('.house-type-detail').html('<h3>出租' + data.house.room_count + '</h3><p>房屋面积:' + data.house.acreage + '平米</p><p>房屋户型:' + data.house.unit + '</p>')

        $('.house-capacity').html('<h3>宜住' + data.house.capacity + '人</h3>')

        $('.house-bed').html('<h3>卧床配置</h3><p>' + data.house.beds + '</p>')

        var house_info_style = '<li>收取押金<span>' + data.house.deposit + '</span></li>'
        house_info_style += '<li>最少入住天数<span>' + data.house.min_days + '</span></li>'
        house_info_style += '<li>最多入住天数<span>' + data.house.max_days + '</span></li>'
        $('.house-info-style').html(house_info_style)

        var house_facility_list = ''
        for(var i=0; i<data.facility_list.length; i++){
            house_facility_list += '<li><span class="' + data.facility_list[i].css + '"></span>' + data.facility_list[i].name + '</li>'
        }
        $('.house-facility-list').html(house_facility_list)

        $('.book-house').attr('href', '/house/booking/?id=' + data.house.id)

        //判断是否显示预订按钮
        if(data.booking==1){
            $(".book-house").show();
        }else{
            $(".book-house").hide();
        }
    });
});