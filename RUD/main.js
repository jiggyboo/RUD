$(document).ready(function(){
    const urls = [];
    const res = {recent:[],recentN:[],popular:[],popularN:[],todays:[],todaysN:[]};

    document.getElementById("search").onclick = function() {
        var sre = document.getElementById("sresult");
        if (sre.style.display === "none") {
            sre.style.display = "flex";
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

    // document.getElementById("adds").onclick = function() {
    //     var red = $("#sub").val();
    //     var typ = $("#type").val();
    //     var tim = $("#time").val();
    //     $('#url-tab').append(
    //         '<div class="w3-card w3-container w3-gray w3-border" style="margin:5px" name="ubody">' +
    //             '<header class="w3-dark-gray">'+
    //                 '<input type="checkbox" name="download" checked="checked" class="w3-check w3_black w3-margin-right">'+
    //                 red+
    //             '</header>'+
    //             '<body class="w3-gray">'+
    //                 '<div class="w3-half" style="padding:2px">'+
    //                     typ +" "+ tim +
    //                 '</div>'+
    //                 '<button class="w3-button w3-dark-grey" style="padding:0px; margin:auto" id="downe">Download</button>'+
    //             '</body>'+
    //         '</div>');
    // }

    document.getElementById("down").onclick = function() {
        var red = $("#sub").val();
        var typ = $("#type").val();
        var tim = $("#time").val();
        var date = $("#date").val();
        if (typ == 'top') {
            var dData = {'sub':red,'typ':typ,'tim':tim,'date':date};
        }
        else {
            var dData = {'sub':red,'typ':typ,'tim':'','date':date};
        }
        $.get('http://ec2-3-35-138-18.ap-northeast-2.compute.amazonaws.com/api/search', dData)
            .done((data) => {
                var urlList = [];
                urlList = data;
                console.log(data);
                var subinfo = [red, typ, tim];
                var urlData = {'subinfo':subinfo, 'urllist':urlList};
                urls.push(urlData);
                $('#url-tab').append(
                    '<div class="w3-card w3-container w3-gray w3-border" style="margin:5px" name="ubody">' +
                    '<header class="w3-dark-gray">'+
                        '<input type="checkbox" name="download" checked="checked" class="w3-check w3_black">'+
                        red+' '+typ+' '+tim+
                    '</header>'+
                    '</div>'
                )
            })
            .fail((error) => console.error(error))
            .always(() => console.log('Download Tried'));
    }

    document.getElementById('downUrl').onclick = function() {
        var blob = new Blob([JSON.stringify(urls)],{type:"text/plain;charset=utf-8"});
        console.log(urls);
        saveAs(blob, "urls.txt");
    }

    document.getElementById('select').onclick = function() {
        if (document.getElementById('select').checked == true) {
            selAll()
        }
        else {
            desAll()
        }
    }

    // document.getElementById('dcnt').onclick = function() {
    //     $.get('http://ec2-3-35-138-18.ap-northeast-2.compute.amazonaws.com/api/dcnt')
    //         .done((data) => {
    //             var dCnt = data;
    //             for (var i = 0; i < 8; i++) {
    //                 document.getElementById('psfw'+(i+1)).innerHTML = dCnt['pops'][i]['sub'];
    //                 document.getElementById('pnsfw'+(i+1)).innerHTML = dCnt['popsN'][i]['sub'];
    //                 document.getElementById('rsfw'+(i+1)).innerHTML = dCnt['recent'][i]['sub'];
    //                 document.getElementById('rnsfw'+(i+1)).innerHTML = dCnt['recentN'][i]['sub'];
                    

    //             }            
    //     })
    // }

    document.getElementById('hidepanelY').onclick = function() {
        document.getElementById('hidepanel').style.display = "none";
    }

    document.getElementById('hidepanelN').onclick = function() {
        document.getElementById('hidepanel').style.backgroundColor = "#20163a";
        document.getElementById('hidepanelY').hidden = true;
        document.getElementById('hidepanelN').hidden = true;
        document.getElementById('hptext').hidden = true;
    }

    // document.getElementById('ping').onclick = function() {
    //     $.ajax({
    //         method: "GET",
    //         dataType: "text",
    //         url: "http://ec2-3-35-138-18.ap-northeast-2.compute.amazonaws.com/api/ping",
    //         success: function(msg) {
    //             console.log(msg);
    //             $('#url-tab').append(
    //                 '<div class="w3-card w3-container w3-gray w3-border" style="margin:5px" name="ubody">' +
    //                 '<header class="w3-dark-gray">'+
    //                     '<input type="checkbox" name="download" checked="checked" class="w3-check w3_black">'+
    //                     msg+
    //                 '</header>'+
    //                 '</div>'
    //             )
    //         }
    //     });
    // }

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

    function chLength(x) {
        if (x.matches) {
            document.getElementById("home").innerText = "RUD";
        }
    }

    function chLength2(x) {
        if (x.matches) {
            document.getElementById("home").innerText = "Reddit URL Downloader";
        }
    }
    var x = window.matchMedia("(max-width: 768px)");
    chLength(x);
    x.addEventListener("change", chLength);

    var y = window.matchMedia("(min-width: 768px)");
    chLength2(y);
    y.addEventListener("change", chLength2);
});

