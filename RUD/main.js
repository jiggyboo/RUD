$(document).ready(function(){           

    document.getElementById("search").onclick = function() {
        var sre = document.getElementById("sresult");
        if (sre.style.display === "none") {
            sre.style.display = "block";
        }
    }

    document.getElementById("linkd").onclick = function() {
        var red = $("#sub").val();
        var typ = $("#type").val();
        var tim = $("#time").val();
        var link = document.getElementById("linkd");
        if (typ == "top") {
            link.href = "https://www.reddit.com/r/"+red+"/"+typ+"/"+"?t="+tim;
        }
        else {
            link.href = "https://www.reddit.com/r/"+red+"/"+typ;
        }
    }

    document.getElementById("adds").onclick = function() {
        var red = $("#sub").val();
        var typ = $("#type").val();
        var tim = $("#time").val();
        var num = $("#nump").val();
        $('#url-tab').append(
            '<div class="w3-card w3-container w3-gray w3-border" style="margin:5px" name="ubody">' +
                '<header class="w3-dark-gray">'+
                    '<input type="checkbox" name="download" checked="checked" class="w3-check w3_black w3-margin-right">'+
                    red+
                '</header>'+
                '<body class="w3-gray">'+
                    '<div class="w3-half" style="padding:2px">'+
                        typ +" "+ num +" "+ tim +
                    '</div>'+
                    '<button class="w3-button w3-dark-grey" style="padding:0px; margin:auto" id="downe">Download</button>'+
                '</body>'+
            '</div>');
    }

    document.getElementById("download").onclick = function() {
        var red = $("#sub").val();
        var typ = $("#type").val();
        var tim = $("#time").val();
        var num = $("#nump").val();
        var dData = {'sub':red,'num':num,'tim':tim};
        $.get('http://localhost:5000/list', dData)
            .done((data) => {
                var urlList = [];
                urlList = JSON.parse(data['urls']);
                download_sub(data['sub'],urlList);
            })
            .fail((error) => console.error(error))
            .always(() => console.log('Download Done'));
    }

    document.getElementById("down").onclick = function() {
        var red = $("#sub").val();
        var typ = $("#type").val();
        var tim = $("#time").val();
        var num = $("#nump").val();
        if (typ == 'top') {
            var dData = {'sub':red,'typ':typ,'tim':tim,'num':num};
        }
        else {
            var dData = {'sub':red,'typ':typ,'num':num};
        }
        $.get('http://localhost:5000/down', dData)
            .done((data) => {
                var urlList = [];
                urlList = data;
                console.log(data);
                download_sub(red,urlList);
            })
            .fail((error) => console.error(error))
            .aways(() => console.log('Download Tried'));
    }

    document.getElementById('select').onclick = function() {
        if (document.getElementById('select').checked == true) {
            selAll()
        }
        else {
            desAll()
        }
    }

    document.getElementById('ping').onclick = function() {
        $.ajax({
            method: "GET",
            dataType: "text",
            url: "http://localhost:5000/ping",
            success: function(msg) {
                console.log(msg);
                $('#url-tab').append(
                    '<div class="w3-card w3-container w3-gray w3-border" style="margin:5px" name="ubody">' +
                    '<header class="w3-dark-gray">'+
                        '<input type="checkbox" name="download" checked="checked" class="w3-check w3_black">'+
                        msg+
                    '</header>'+
                    '</div>'
                )
            }
        });
    }

    document.getElementById('url').onclick = function() {
        $.get('http://localhost:5000/url')
            .done((data) => {
                $('#url-tab').append(
                    '<div class="w3-card w3-container w3-gray w3-border" style="margin:5px" name="ubody">' +
                    '<header class="w3-dark-gray">'+
                        '<input type="checkbox" name="download" checked="checked" class="w3-check w3_black w3-margin-right">'+
                        data['url']+
                    '</header>'+
                    '<body class="w3-gray">'+
                        '<div class="w3-half" style="padding:2px">'+
                        data['download']+
                        '</div>'+
                        '<button class="w3-button w3-dark-grey" style="padding:0px; margin:auto" id="downe">Download</button>'+
                    '</body>'+
                    '</div>'
                )
            })
            .fail((error) => console.error(error))
            .always(() => console.log('Done'));
    }

    function attping(msg) {
        var pong = msg;
        $('#url-tab').append(
            '<div class="w3-card w3-container w3-gray w3-border" style="margin:5px" name="ubody">' +
            '<header class="w3-dark-gray">'+
                '<input type="checkbox" name="download" checked="checked" class="w3-check w3_black w3-margin-right">'+
                'Subreddit Title'+
            '</header>'+
            '<body class="w3-gray">'+
                '<div class="w3-half" style="padding:2px">'+
                    'Type NumPos Timeline'+
                '</div>'+
                '<button class="w3-button w3-dark-grey" style="padding:0px; margin:auto" id="downe">Download</button>'+
            '</body>'+
            '</div>'
        )   
    }

    function selAll() {
        var checkboxes = document.getElementsByName("download");
        for (var checkbox of checkboxes) {
            checkbox.checked = true;
        }
    }

    function desAll() {
        var checkboxes = document.getElementsByName("download");
        for (var checkbox of checkboxes) {
            checkbox.checked = false;
        }
    }

    document.getElementById("del").onclick = function() {
        var checkboxes = document.getElementsByName("download");
        for (var checkbox of checkboxes) {
            if (checkbox.checked == true){
                checkbox.parentElement.parentElement.remove();
            }
        }
    }
});
