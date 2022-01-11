$(document).ready(function(){
    const urls = [];
    var temp = [];
    var temp2 = [];
    const res = {recent:[],recentN:[],popular:[],popularN:[],todays:[],todaysN:[]};
    var modal = document.getElementById("modal");
    var span = document.getElementsByClassName("close")[0];

    function redoCD() {
        let x = document.getElementById('rcd').value;
        if (x == "Reddit") {
            document.getElementById('sub').placeholder = "Subreddit";
            document.getElementById('time').disabled = false;
            document.getElementById('type').disabled = false;
        }
        else if (x == "CD") {
            document.getElementById('sub').placeholder = "Cyberdrop";
            document.getElementById('time').disabled = true;
            document.getElementById('type').disabled = true;
        }
    }

    document.getElementById('rcd').onchange = redoCD;

    function redType() {
        let x = $('#type').val();
        if (x == "hot" || x == "new") {
            document.getElementById('time').disabled = true;
        }
        else {
            document.getElementById('time').disabled = false;
        }
    }

    document.getElementById('type').onchange = redType;


    // Search Modal //
    document.getElementById("search").onclick = function() { 

        if ($("#sub").val()=="") {
            alert("Please enter a Subreddit name or Cyberdrop URL");
            console.log($("#sub").val());
        }
        else {
            modal.style.display = "block";
        }

        let roc = $("#rcd").val();

        // Searching For Reddit //
        if (roc == 'Reddit') {
            let red = $("#sub").val();
            let typ = $("#type").val();
            let tim = $("#time").val();
            let dData = {};
            if (typ == 'top') {
                dData = {'sub':red,'typ':typ,'tim':tim};
            }
            else {
                dData = {'sub':red,'typ':typ,'tim':''};
            }
            $.get('https://rud4u.xyz/api/search', dData)
                .done((data) => {
                    temp = JSON.parse(data['tf']);
                    temp2 = JSON.parse(data['result']);
                    console.log(data);
                    let id = JSON.parse(data['result'])['id'];
                    console.log(id);
                    $('#modsr').append(
                        '<div class="modurlt" style="margin:5px" name="ubody">' +
                        '<button class="modadd">Add</button>' +
                        '<div class="murltitm">'+red+'</div>'+'<div class="murltitm">'+typ+'</div>'+'<div class="murltitm">'+tim+'</div>' +
                        '<div style="display:none;">' + id + '</div>' +
                        '</div>'
                    );
                    for (var pc of JSON.parse(data['tf'])) {
                        console.log(pc);
                        if (pc['id'] != id) {
                            $('#modpr').append(
                                '<div class="modurlt" style="margin:5px" name="ubody">' +
                                '<button class="modadd">Add</button>' +
                                '<div class="murltitm">'+red+'</div>'+'<div class="murltitm">'+pc['type']+'</div>'+'<div class="murltitm">'+pc['time']+'</div>' +
                                '<div style="display:none;">' + pc['id'] + '</div>' +
                                '</div>'
                            );
                        }
                    }
                    if ($("#modpr").children().length == 0) {
                        $("#modpr").append(
                            '<div class="modurltna" style="margin:5px" name="ubody">' +
                            '<div class="murltitm">'+'</div>'+'<div class="murltitm">N/A</div>'+'<div class="murltitm"></div>' +
                            '<div style="display:none;"></div>' +
                            '</div>'
                        );
                    }
                })
            .fail((error) => console.error(error))
            .always(() => console.log('Download Tried'));
        }
        // Searching For Cyberdrop //
        else {
            var url = $("#sub").val();
            $.get('https://rud4u.xyz/api/cd', {'url':url})
            .done((data) => {
                console.log(data);
                //URL Search
                if (url.includes('https')) {  
                    temp = JSON.parse(data['recent']);
                    console.log(data);
                    let id = 0;
                    if (data['result'] == "Page No Longer Available") {
                        alert("Page No Longer Available");
                        $('#modsr').append(
                            '<div class="modurlt" style="margin:5px" name="ubody">' +
                            '<div class="murltitmcd">'+'</div>'+'<div class="murltitmcdt">N/A</div>'+'<div class="murltitm"></div>' +
                            '<div style="display:none;"></div>' +
                            '</div>'
                        )
                    }
                    else {
                        temp2 = JSON.parse(data['result']);
                        id = temp2['id'];
                        var title = temp2['title'];

                        $('#modsr').append(
                            '<div class="modurlt" style="margin:5px" name="ubody">' +
                            '<button class="modadd">Add</button>' +
                            '<div class="murltitmcd">CyberDrop</div><div class="murltitmcdt">'+title+'</div><div class="murltitm"></div>' +
                            '<div style="display:none;">' + id + '</div>' +
                            '</div>'
                        )
                    }

                    for (let pc of temp) {
                        if (pc['id'] != id) {
                            $('#modpr').append(
                                '<div class="modurlt" style="margin:5px" name="ubody">' +
                                '<button class="modadd">Add</button>' +
                                '<div class="murltitmcd">CyberDrop</div><div class="murltitmcdt">'+pc['title']+'</div><div class="murltitm"></div>' +
                                '<div style="display:none;">' + pc['id'] + '</div>' +
                                '</div>'
                            );
                        }
                    }
                }
                //Query Search
                else {
                    temp = JSON.parse(data['recent']);
                    console.log(data);
                    if (temp2 == "QUERY NOT FOUND") {
                        alert("Query Not Found");
                        $('#modsr').append(
                            '<div class="modurlt" style="margin:5px" name="ubody">' +
                            '<div class="murltitmcd">'+'</div>'+'<div class="murltitmcdt">N/A</div>'+'<div class="murltitm"></div>' +
                            '<div style="display:none;"></div>' +
                            '</div>'
                        )
                    }
                    else {
                        temp2 = JSON.parse(data['result']);
                        var ids = [];
                        for (let pc of temp2) {
                            $('#modsr').append(
                                '<div class="modurlt" style="margin:5px" name="ubody">' +
                                '<button class="modadd">Add</button>' +
                                '<div class="murltitmcd">CyberDrop</div><div class="murltitmcdt">'+pc['title']+'</div><div class="murltitm"></div>' +
                                '<div style="display:none;">' + pc['id'] + '</div>' +
                                '</div>'
                            );
                            ids.push(pc['id']);
                        }
                    }
                    
                    for (let pc of temp) {
                        let x = 0
                        for (let num of ids) {
                            if (pc['id'] == num) {
                                console.log("same item found");
                                x = 1;
                                break;
                            }
                        }
                        if (x != 0) {
                            continue;
                        }
                        $('#modpr').append(
                            '<div class="modurlt" style="margin:5px" name="ubody">' +
                            '<button class="modadd">Add</button>' +
                            '<div class="murltitmcd">CyberDrop</div><div class="murltitmcdt">'+pc['title']+'</div><div class="murltitm"></div>' +
                            '<div style="display:none;">' + pc['id'] + '</div>' +
                            '</div>'
                        );
                        
                    }
                }
            })
            .fail((error) => alert("Server Error Try Again", error))
            .always(() => console.log('Download Tried'));
        }
    }

    span.onclick = function() {
        modal.style.display = "none";
        $('#modsr').empty();
        $('#modpr').empty();
    }

    window.onclick = function(event) {
        if (event.target == modal) {
          modal.style.display = "none";
          $('#modsr').empty();
          $('#modpr').empty();
        }
    }

    document.getElementById("del").onclick = del;

    function del() {
        var checkboxes = document.getElementsByName("download");
        for (var i = 0; i < 4; i++) {
            for (var checkbox of checkboxes) {
                if (checkbox.checked == true) {
                    var id = checkbox.parentElement.children[4].innerText;
                    for (var url of urls) {
                        if (url['subinfo'][3] == id) {
                            var index = urls.indexOf(url);
                            urls.splice(index, 1);
                            console.log(index);
                        }
                        if (url['subinfo'][2] == id) {
                            var index = urls.indexOf(url);
                            urls.splice(index, 1);
                            console.log(index);
                        }
                    }
                    checkbox.parentElement.remove();
                }
            }
        }
        updateLen();
        console.log(urls);
    }

    function updateLen() {
        document.getElementById("listlen").innerText = urls.length;
    }

    document.getElementById('downUrl').onclick = downUrl;

    function downUrl() {
        if (urls.length == 0) {
            console.log("list empty");
            return alert("Your list is empty!");
        }
        var blob = new Blob([JSON.stringify(urls)],{type:"text/plain;charset=utf-8"});
        console.log(urls);
        saveAs(blob, "urls.txt");
        document.getElementById("urls").textContent = '';
        urls.splice(0, urls.length);
        updateLen();
        console.log(urls);
    }

    function selAll() {
        var checkboxes = document.getElementsByName("download");
        for (let checkbox of checkboxes) {
            checkbox.checked = true;
        }
    }

    function desAll() {
        var checkboxes = document.getElementsByName("download");
        for (let checkbox of checkboxes) {
            checkbox.checked = false;
        }
    }

    document.getElementById('select').onclick = function() {
        if (document.getElementById('select').checked == true) {
            selAll()
        }
        else {
            desAll()
        }
    }

    function dcnt() {
        $.get('https://rud4u.xyz/api/dcnt')
            .done((data) => {
                let dCnt = data;
                res['popular'] = JSON.parse(dCnt['pops']);
                res['popularN'] = JSON.parse(dCnt['popsN']);
                res['recent'] = JSON.parse(dCnt['recent']);
                res['recentN'] = JSON.parse(dCnt['recentN']);
                res['todays'] = JSON.parse(dCnt['todays']);
                res['todaysN'] = JSON.parse(dCnt['todaysN']);

                for (var i = 0; i < 8; i++) {
                    $('#popular'+i).append(
                        '<div class="posttitle">'+res['popular'][i]['sub']+'</div>' +
                        '<div class="postitem">'+res['popular'][i]['type']+'</div>' +
                        '<div class="postitem">'+res['popular'][i]['time']+'</div>' +
                        '<button class="postadd">'+'Add'+'</button>'
                    )
                    $('#popularN'+i).append(
                        '<div class="posttitle">'+res['popularN'][i]['sub']+'</div>' +
                        '<div class="postitem">'+res['popularN'][i]['type']+'</div>' +
                        '<div class="postitem">'+res['popularN'][i]['time']+'</div>' +
                        '<button class="postadd">'+'Add'+'</button>'
                    )
                    $('#todays'+i).append(
                        '<div class="posttitle">'+res['todays'][i]['sub']+'</div>' +
                        '<div class="postitem">'+res['todays'][i]['type']+'</div>' +
                        '<div class="postitem">'+res['todays'][i]['time']+'</div>' +
                        '<button class="postadd">'+'Add'+'</button>'
                    )
                    $('#todaysN'+i).append(
                        '<div class="posttitle">'+res['todaysN'][i]['sub']+'</div>' +
                        '<div class="postitem">'+res['todaysN'][i]['type']+'</div>' +
                        '<div class="postitem">'+res['todaysN'][i]['time']+'</div>' +
                        '<button class="postadd">'+'Add'+'</button>'
                    )
                }
                console.log(res);
            })
    }

    document.body.addEventListener('click', event => {

        // Adding from Recent/Popular
        if (event.target.className == 'postadd') {
            let id = String(event.target.parentElement.id);
            let type = id.slice(0,-1);
            let index = id.slice(-1);
            id = res[type][index]['id'];
            for (let url of urls) {
                if (url['subinfo'][3]==id) {
                    return alert("Already in list");
                }
            }
            let sub = res[type][index]['sub'];
            let typ = res[type][index]['type'];
            let tim = res[type][index]['time'];

            let urllist = res[type][index]['urls'];
            let subinfo = [sub, typ, tim, id];
            let urlData = {'subinfo':subinfo, 'urllist':urllist};
            urls.push(urlData);
            updateLen();
            console.log(urls.length);

            $('#urls').append(
                '<div class="urlt" style="margin:5px" name="ubody">' +
                '<input type="checkbox" name="download" checked="checked" class="check">'+
                '<div class="urltitm">'+sub+'</div>'+'<div class="urltitm">'+typ+'</div>'+'<div class="urltitm">'+tim+'</div>' +
                '<div style="display:none;">' + id + '</div>' +
                '</div>'
            )
        }

        // Adding from Search
        if (event.target.className == 'modadd') {
            // CyberDrop //
            if (event.target.parentElement.children[1].innerText == 'CyberDrop') {
                let type = String(event.target.parentElement.parentElement.id);
                let uoq = $('#sub').val();
                // URL based Search //
                if (uoq.includes('http')) {
                    if (type == "modsr") {
                        let title = event.target.parentElement.children[2].innerText;
                        let id = event.target.parentElement.children[4].innerText;
                        // Find Duplicates in List
                        for (let url of urls) {
                            if (url['subinfo'][2]==id && url['subinfo'].length == 3) {
                                return alert("Already in list");
                            }
                        }
                        let cdinfo = [title, uoq, id];
                        let urlList = temp2['urls'];
                        let urlData = {'subinfo':cdinfo, 'urllist':urlList};
                        console.log(urlData);
                        urls.push(urlData);
                        updateLen();
                        $('#urls').append(
                            '<div class="urlt" style="margin:5px" name="ubody">' +
                            '<input type="checkbox" name="download" checked="checked" class="check">'+
                            '<div class="urltitm">CyberDrop</div>'+'<div class="urltitm">'+title+'</div>'+'<div class="urltitm"></div>' +
                            '<div style="display:none;">' + id + '</div>' +
                            '</div>'
                        )
                    }
                    else {
                        let title = event.target.parentElement.children[2].innerText;
                        let id = event.target.parentElement.children[4].innerText;
                        // Find Duplicates in List
                        for (let url of urls) {
                            if (url['subinfo'][2]==id && url['subinfo'].length == 3) {
                                return alert("Already in list");
                            }
                        }
                        for (let pc of temp) {
                            if (id == pc['id']) {
                                let cdinfo = [title, uoq, id];
                                let urlList = pc['urls'];
                                let urlData = {'subinfo':cdinfo, 'urllist':urlList};
                                console.log(urlData);
                                urls.push(urlData);
                                updateLen();
                                $('#urls').append(
                                    '<div class="urlt" style="margin:5px" name="ubody">' +
                                    '<input type="checkbox" name="download" checked="checked" class="check">'+
                                    '<div class="urltitm">CyberDrop</div>'+'<div class="urltitm">'+title+'</div>'+'<div class="urltitm"></div>' +
                                    '<div style="display:none;">' + id + '</div>' +
                                    '</div>'
                                )
                            }
                        }
                    }
                }
                // Title based Search //
                else {
                    if (type == "modsr") {
                        let title = event.target.parentElement.children[2].innerText;
                        let id = event.target.parentElement.children[4].innerText;
                        // Find Duplicates in List
                        for (let url of urls) {
                            if (url['subinfo'][2]==id && url['subinfo'].length == 3) {
                                return alert("Already in list");
                            }
                        }
                        for (let pc of temp2) {
                            if (id == pc['id']) {
                                let cdinfo = [title, uoq, id];
                                let urlList = pc['urls'];
                                let urlData = {'subinfo':cdinfo, 'urllist':urlList};
                                console.log(urlData);
                                urls.push(urlData);
                                updateLen();
                                $('#urls').append(
                                    '<div class="urlt" style="margin:5px" name="ubody">' +
                                    '<input type="checkbox" name="download" checked="checked" class="check">'+
                                    '<div class="urltitm">CyberDrop</div>'+'<div class="urltitm">'+title+'</div>'+'<div class="urltitm"></div>' +
                                    '<div style="display:none;">' + id + '</div>' +
                                    '</div>'
                                )
                            }
                        }
                    }
                    else {
                        let title = event.target.parentElement.children[2].innerText;
                        let id = event.target.parentElement.children[4].innerText;
                        // Find Duplicates in List
                        for (let url of urls) {
                            if (url['subinfo'][2]==id && url['subinfo'].length == 3) {
                                return alert("Already in list");
                            }
                        }
                        for (let pc of temp) {
                            if (id == pc['id']) {
                                let cdinfo = [title, uoq, id];
                                let urlList = pc['urls'];
                                let urlData = {'subinfo':cdinfo, 'urllist':urlList};
                                console.log(urlData);
                                urls.push(urlData);
                                updateLen();
                                $('#urls').append(
                                    '<div class="urlt" style="margin:5px" name="ubody">' +
                                    '<input type="checkbox" name="download" checked="checked" class="check">'+
                                    '<div class="urltitm">CyberDrop</div>'+'<div class="urltitm">'+title+'</div>'+'<div class="urltitm"></div>' +
                                    '<div style="display:none;">' + id + '</div>' +
                                    '</div>'
                                )
                            }
                        }
                    }
                }
            }
            // Reddit //
            else {
                let type = String(event.target.parentElement.parentElement.id);
                var id = event.target.parentElement.children[4].innerText;
                var sub = event.target.parentElement.children[1].innerText;
                var typ = event.target.parentElement.children[2].innerText;
                var tim = event.target.parentElement.children[3].innerText;
                for (let url of urls) {
                    if (url['subinfo'][3]==id) {
                        return alert("Already in list");
                    }
                }
                if (type == 'modsr') {
                    var urllist = temp2['url'];
                    var subinfo = [sub, typ, tim, id];
                    var urlData = {'subinfo':subinfo, 'urllist':urllist};
                    urls.push(urlData);
                    updateLen();
                    console.log(urls.length);
                    $('#urls').append(
                        '<div class="urlt" style="margin:5px" name="ubody">' +
                        '<input type="checkbox" name="download" checked="checked" class="check">'+
                        '<div class="urltitm">'+sub+'</div>'+'<div class="urltitm">'+typ+'</div>'+'<div class="urltitm">'+tim+'</div>' +
                        '<div style="display:none;">' + id + '</div>' +
                        '</div>'
                    )
                }
                else {
                    for (let url of temp) {
                        if (url['id']==id) {
                            var urllist = url['urls'];
                            var subinfo = [sub, typ, tim, id];
                            var urlData = {'subinfo':subinfo, 'urllist':urllist};
                            urls.push(urlData);
                            updateLen();
                            console.log(urls.length);
            
                            $('#urls').append(
                                '<div class="urlt" style="margin:5px" name="ubody">' +
                                '<input type="checkbox" name="download" checked="checked" class="check">'+
                                '<div class="urltitm">'+sub+'</div>'+'<div class="urltitm">'+typ+'</div>'+'<div class="urltitm">'+tim+'</div>' +
                                '<div style="display:none;">' + id + '</div>' +
                                '</div>'
                            )
                        }
                    }    
                }
            }
                
        }
    })

    document.getElementById('hidepanelY').onclick = function() {
        document.getElementById('hidepanel').style.display = "none";
    }

    document.getElementById('hidepanelN').onclick = function() {
        document.getElementById('hidepanel').style.backgroundColor = "#20163a";
        document.getElementById('hidepanelY').hidden = true;
        document.getElementById('hidepanelN').hidden = true;
        document.getElementById('hptext').hidden = true;
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

    function addUrlRed(red, typ, tim, id) {
        $('#urls').append(
            '<div class="urlt" style="margin:5px" name="ubody">' +
            '<input type="checkbox" name="download" checked="checked" class="check">'+
            '<div class="urltitm">'+red+'</div>'+'<div class="urltitm">'+typ+'</div>'+'<div class="urltitm">'+tim+'</div>' +
            '<div style="display:none;">' + id + '</div>' +
            '</div>'
        )
    }

    function addUrlCD(title, id) {
        $('#urls').append(
            '<div class="urlt" style="margin:5px" name="ubody">' +
            '<input type="checkbox" name="download" checked="checked" class="check">'+
            '<div class="urltitm">CyberDrop</div><div class="urltitm">'+title+'</div><div class="urltitm"></div>' +
            '<div style="display:none;">' + id + '</div>' +
            '</div>'
        )
    }

    document.getElementById('head').onclick = function() {
        let width = window.innerWidth;
        if (width < 768) {
            $('.transform').toggleClass('transform-active');
            $('.urltabbtns').toggleClass('urltabbtns-active');
            $('.urltab-small').toggleClass('urltab-small-active');
        }
        else {
            console.log("not mobile");
        }
    };

    dcnt();

});

