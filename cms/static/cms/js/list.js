/**
 * Created by song on 16-4-21.
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

$(document).ready(function(){
    $('#list-search').submit(function(e){
        e.preventDefault();
        var field = $('#id_search_field').val();
        var value = $('#id_search_value').val();
        var search_by_value = $('#id_search_by_group').val();
        var para = "";
        var search = false;
        var search_by = false;

        for( var i in GET){
            if(i=="search"){
                if(value) {
                    para += 'search=' + field + ',' + value + '&';
                }
                search = true;
                continue
            }
            if(i=="search_by_group"){
                if(search_by_value) {
                    para += 'search_by_group=true&';
                    search_by = true;
                }
                continue
            }

            para += i+'='+GET[i]+'&';
        }
        para=para.substring(0,para.length-1);

        if(!search && value){
            para += '&search='+field+','+value
        }

        if(!search_by && search_by_value){
            para += '&search_by_group=true'
        }

        var url = window.document.location.href.toString();
        var u = url.split("?");

        console.log(u[0]);
        window.document.location.href = u[0]+'?'+para;
    })

});