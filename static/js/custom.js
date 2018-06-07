$(function() {
    $('#cluster-button').click(function() {
        var form_data = new FormData($('#cluster-form')[0]);
        $.ajax({
            type: 'POST',
            url: '/upload',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function(data) {
                console.log('Success!');
                console.log(data);
                $("#image-1").attr("src",'static/uploads/'+data);
            },
        });
    });
});

function clusterImage(){
    // var form_data = new FormData($('#cluster-form')[0]);
    var cluster = document.getElementById("num-cluster").value;
    var form_data = new FormData($('#cluster-master')[0]);
    console.log(cluster)
    $.ajax({
        type: 'POST',
        url: '/cluster-lib',
        data: form_data,
        // dataType: 'json',
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
            // console.log('Success!');
            console.log(data);
            $("#image-final").attr("src",'static/result/'+data);
            $("#image-final").attr("style",'width:350px; height:350px;');
        },
    });
}

function uploadImage(num){
    var form_data = new FormData($('#upload-file-'+num)[0]);
    $.ajax({
        type: 'POST',
        url: '/upload',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
            console.log('Success!');
            console.log(data);
            $("#image-"+num).attr("src",'static/uploads/'+data);
        },
    });
}