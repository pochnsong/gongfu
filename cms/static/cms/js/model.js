/**
 * Created by song on 15-7-29.
 */

var GET = (function(){
    var url = window.document.location.href.toString();
    var u = url.split("?");
    if(typeof(u[1]) == "string"){
        u = u[1].split("&");
        var _get = {};
        for(var i in u){
            var j = u[i].split("=");
            _get[j[0]] = j[1];
        }
        return _get;
    } else {
        return {};
    }
})();

$('.form-group input').each(function(){
    var $this = $(this);
    var $list = ["file", "checkbox"];
    for(var i in $list){
        if($this.attr("type")==$list[i]){
            if($this.attr("type")=="file"){
                $this.css('display', 'inline-block');
            }
            return
        }
    }
    $this.addClass('form-control')

});

$('.form-group textarea').addClass('form-control');
$('.form-group select').each(function(){
    var $this=$(this);
    $(this).addClass('form-control');
    if($(this).attr("multiple")=="multiple"){
        $(this).hide();
        var select_id = $(this).attr("id");
        var $list = '<div data-select="'+select_id+'">';
        $this.find("option").each(function(){
            if($(this).attr("selected")=="selected"){
                $list += '<div class="select-item btn btn-default active">'+$(this).text()+"</div>";
            }else{
                $list += '<div class="select-item btn btn-default">'+$(this).text()+"</div>";
            }
        });
        $list+="<div>";
        $(this).parent().append($list);

        // 添加事件

        $(".select-item").click(function(){
            var $parent = $(this).parent();
            var select_id = "#"+$parent.data('select');
            var $option = $(select_id).find(":contains("+$(this).html()+")");
            $(this).toggleClass("active");
            if($(this).hasClass("active")){
                $option.attr("selected", "selected");
            }else{
                $option.removeAttr("selected");
            }
        });

    }
});

// 初始化 WYSIWIG
var WYSIWIG=GET['WYSIWIG']?GET['WYSIWIG'].replace(/%23/g, "#"):"textarea";
if(GET['model']=='WebsiteModel'){
    WYSIWIG = null;
}

$(document).ready(function(){
    if(WYSIWIG) {
        tinyMCE.init({
            selector: WYSIWIG,
            plugins: [
                "advlist autolink lists link image charmap print preview hr anchor pagebreak",
                "searchreplace wordcount visualblocks visualchars code fullscreen",
                "insertdatetime media nonbreaking save table contextmenu directionality",
                "emoticons template paste textcolor colorpicker textpattern imagetools image64"
            ],

            toolbar1: "insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image",
            toolbar2: "print preview media | forecolor backcolor emoticons| image64",
            image_advtab: true,
            paste_data_images: true,
            height: 600,
            language: 'zh_CN'
        });
    }

    $(".form_datetime").datetimepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        minView: 2,
        language: 'zh-CN',
        pickerPosition: 'top-right'
    });
});