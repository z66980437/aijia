function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    //查询地区、设施信息
    $.get('/house/area_facility/',function (data) {
        //地区
        var area_html = ''
        for(var i=0; i<data.area.length; i++){
            area_html += '<option value="' + data.area[i].id + '">' + data.area[i].name + '</option>'
        }
        $('#area-id').html(area_html);
        //设施
        var facility_html_list = ''
        for(var i=0; i<data.facility.length; i++){
            var facility_html = '<li><div class="checkbox"><label><input type="checkbox" name="facility"'
            facility_html += ' value="' + data.facility[i].id + '">' + data.facility[i].name
            facility_html += '</label></div></li>'

            facility_html_list += facility_html
        }
        $('.house-facility-list').html(facility_html_list);
    });

    //为房屋表单绑定提交事件
    $('#form-house-info').submit(function (e) {
        e.preventDefault();
        $('.error-msg text-center').hide();
        $(this).ajaxSubmit({
            url: '/house/new_house/',
            type: 'POST',
            dataType: 'json',
            success: function (data) {
                if (data.code == '200') {
                    $('#form-house-info').hide();
                    // 完成之后展示图片上传表单
                    $('#form-house-image').show();
                    // 信息上传成功之后，将图片上传表单中id为house-id的input框的value改为我们房屋的id，这样在图片上传跟的时候就可以知道是上床的那个房屋的图片了
                    $('#house-id').val(data.house_id);
                } else {
                    $('.error-msg text-center').show().find('span').html(ret_map[data.code]);
                }
            }
        });
        return false;
    });


})