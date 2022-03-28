$(document).ready(function(){
    const urls = [];
    temp = [];
    temp2 = [];
    const res = {recent:[],recentN:[],popular:[],popularN:[],todays:[],todaysN:[]};
    var modal = $(".modal");
    var rcd = $("#rcd");
    var sub = $("#sub");
    var time = $("#time");
    var stype = $("#type");
    var modsr = $("#modsr");
    var modpr = $("#modpr");
    var urltab = $("#urls");

    // Search Bar Functions //
    rcd.on("change", function(){
        let x = rcd.val();
        if (x == "Reddit") {
            sub.attr('placeholder', 'Subreddit');
            time.attr('disabled',  false);
            stype.attr('disabled',  false);
        }
        else if (x == "CD") {
            sub.attr('placeholder', 'Cyberdrop');
            time.attr('disabled',  true);
            stype.attr('disabled',  true);
        }
    });

    stype.on("change",function(){
        let x = type.val();
        if (x == "hot" || x == "new") {
            time.attr('disabled', true);
        }
        else {
            time.attr('disabled', false);
        }
    });

    // Search Modal //
    $("#search").on("click", function() { 

        if (sub.val().trim()=="") {
            return alert("Please enter a Subreddit name or Cyberdrop URL.\n입력창에 레딧게시판 이름 또는 CyberDrop URL을 입력하세요.");
        }
        else {
            modal.css("display","block");
        }

        let roc = rcd.val();

        // Searching For Reddit //
        if (roc == 'Reddit') {
            let red = sub.val();
            let typ = stype.val();
            let tim = time.val();
            let dData = {};
            if (typ == 'top') {
                dData = {'sub':red,'typ':typ,'tim':tim};
            }
            else {
                dData = {'sub':red,'typ':typ,'tim':''};
            }
            $.get('https://rud4u.xyz/api/search', dData)
                .done((data) => {
                    console.log(data);
                    temp = JSON.parse(data['tf']);
                    temp2 = JSON.parse(data['result']);
                    let id = JSON.parse(data['result'])['id'];
                    console.log(id);
                    modsr.append(
                        '<div class="modurlt" style="margin:5px" name="ubody">' +
                        '<button class="modadd">Add</button>' +
                        '<div class="murltitm">'+red+'</div>'+'<div class="murltitm">'+typ+'</div>'+'<div class="murltitm">'+tim+'</div>' +
                        '<div style="display:none;">' + id + '</div>' +
                        '</div>'
                    );
                    for (var pc of JSON.parse(data['tf'])) {
                        console.log(pc);
                        if (pc['id'] != id) {
                            modpr.append(
                                '<div class="modurlt" style="margin:5px" name="ubody">' +
                                '<button class="modadd">Add</button>' +
                                '<div class="murltitm">'+red+'</div>'+'<div class="murltitm">'+pc['type']+'</div>'+'<div class="murltitm">'+pc['time']+'</div>' +
                                '<div style="display:none;">' + pc['id'] + '</div>' +
                                '</div>'
                            );
                        }
                    }
                    if (modpr.children().length == 0) {
                        modpr.append(
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
            var url = sub.val();
            $.get('https://rud4u.xyz/api/cd', {'url':url})
            .done((data) => {
                console.log(data);
                //URL Search
                if (url.includes('https')) {  
                    temp = JSON.parse(data['recent']);
                    let id = 0;
                    if (data['result'] == "Page No Longer Available") {
                        alert("Page No Longer Available!")
                        modsr.append(
                            '<div class="modurltna" style="margin:5px" name="ubody">' +
                            '<div class="murltitm">'+'</div>'+'<div class="murltitm">N/A</div>'+'<div class="murltitm"></div>' +
                            '<div style="display:none;"></div>' +
                            '</div>'
                        )
                    }
                    else {
                        temp2 = JSON.parse(data['result']);
                        id = temp2['id'];
                        var title = temp2['title'];

                        modsr.append(
                            '<div class="modurlt" style="margin:5px" name="ubody">' +
                            '<button class="modadd">Add</button>' +
                            '<div class="murltitmcd">CyberDrop</div><div class="murltitmcdt">'+title+'</div><div class="murltitm"></div>' +
                            '<div style="display:none;">' + id + '</div>' +
                            '</div>'
                        )
                    }

                    for (let pc of temp) {
                        if (pc['id'] != id) {
                            modpr.append(
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
                    var ids = [];
                    if (data['result'] == "QUERY NOT FOUND") {
                        modsr.append(
                            '<div class="modurltna" style="margin:5px" name="ubody">' +
                            '<div class="murltitm">'+'</div>'+'<div class="murltitm">N/A</div>'+'<div class="murltitm"></div>' +
                            '<div style="display:none;"></div>' +
                            '</div>'
                        )
                    }
                    else {
                        temp2 = JSON.parse(data['result']);
                        for (let pc of temp2) {
                            modsr.append(
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
                        modpr.append(
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
    });

    $('.close:nth-child(1)').on("click", function(){
        modal.css("display","none");
        $('#modsr').empty();
        $('#modpr').empty();
    })

    $('.modal').on("click", function(e){
        if (e.target.closest('.modal_content')==null) {
            modal.css("display","none");
            $('#modsr').empty();
            $('#modpr').empty();
        }
        // Adding from Search
        if (e.target.className == 'modadd') {
            console.log("inside if");
            // CyberDrop //
            if (e.target.parentElement.children[1].innerText == 'CyberDrop') {
                console.log("inside if2");
                let type = String(e.target.parentElement.parentElement.id);
                console.log(type);
                let uoq = $("#sub").val();
                // URL based Search //
                if (uoq.includes('http')) {
                    if (type == "modsr") {
                        let title = e.target.parentElement.children[2].innerText;
                        let id = e.target.parentElement.children[4].innerText;
                        let cd = e.target.parentElement.children[1].innerText;
                        // Find Duplicates in List
                        for (let url of urls) {
                            if (url['subinfo'][2]==id && url['subinfo'].length == 3) {
                                return alert("Already in list");
                            }
                        }
                        let cdinfo = [title, cd, id];
                        let urlList = temp2['urls'];
                        let urlData = {'subinfo':cdinfo, 'urllist':urlList};
                        console.log(urlData);
                        urls.push(urlData);
                        updateLen();
                        urltab.append(
                            '<div class="urlt" style="margin:5px" name="ubody">' +
                            '<input type="checkbox" name="download" checked="checked" class="check">'+
                            '<div class="urltitm">CyberDrop</div>'+'<div class="urltitm">'+title+'</div>'+'<div class="urltitm"></div>' +
                            '<div style="display:none;">' + id + '</div>' +
                            '</div>'
                        )
                    }
                    else {
                        let title = e.target.parentElement.children[2].innerText;
                        let id = e.target.parentElement.children[4].innerText;
                        let cd = e.target.parentElement.children[1].innerText;
                        // Find Duplicates in List
                        for (let url of urls) {
                            console.log("checking for duplicates");
                            if (url['subinfo'][2]==id && url['subinfo'].length == 3) {
                                return alert("Already in list");
                            }
                        }
                        for (let pc of temp) {
                            console.log(pc['id']);
                            if (id == pc['id']) {
                                let cdinfo = [title, cd, id];
                                let urlList = pc['urls'];
                                let urlData = {'subinfo':cdinfo, 'urllist':urlList};
                                console.log(urlData);
                                urls.push(urlData);
                                updateLen();
                                urltab.append(
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
                    console.log(type);
                    if (type == "modsr") {
                        let title = e.target.parentElement.children[2].innerText;
                        let id = e.target.parentElement.children[4].innerText;
                        let cd = e.target.parentElement.children[1].innerText;
                        // Find Duplicates in List
                        for (let url of urls) {
                            if (url['subinfo'][2]==id && url['subinfo'].length == 3) {
                                return alert("Already in list");
                            }
                        }
                        for (let pc of temp2) {
                            if (id == pc['id']) {
                                let cdinfo = [title, cd, id];
                                let urlList = pc['urls'];
                                let urlData = {'subinfo':cdinfo, 'urllist':urlList};
                                console.log(urlData);
                                urls.push(urlData);
                                updateLen();
                                urltab.append(
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
                        console.log("in modpr");
                        let title = e.target.parentElement.children[2].innerText;
                        let id = e.target.parentElement.children[4].innerText;
                        let cd = e.target.parentElement.children[1].innerText;
                        console.log(temp);
                        // Find Duplicates in List
                        for (let url of urls) {
                            if (url['subinfo'][2]==id && url['subinfo'].length == 3) {
                                return alert("Already in list");
                            }
                        }
                        for (let pc of temp) {
                            if (id == pc['id']) {
                                console.log("inside final if");
                                let cdinfo = [title, cd, id];
                                let urlList = pc['urls'];
                                let urlData = {'subinfo':cdinfo, 'urllist':urlList};
                                console.log(urlData);
                                urls.push(urlData);
                                updateLen();
                                urltab.append(
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
                console.log(e.target.parentElement.parentElement)
                let type = String(e.target.parentElement.parentElement.id);
                var id = e.target.parentElement.children[4].innerText;
                var sub = e.target.parentElement.children[1].innerText;
                var typ = e.target.parentElement.children[2].innerText;
                var tim = e.target.parentElement.children[3].innerText;
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
                    urltab.append(
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
            
                            urltab.append(
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

    $("#del").on("click", del);

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

    $('#downUrl').on("click", downUrl);

    function downUrl() {
        if (urls.length == 0) {
            console.log("list empty");
            return alert("Your list is empty!\nPlease add some items to download.\n다운로드할 자료가 없습니다.");
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

    document.body.addEventListener('click', e => {
        // Adding from Recent/Popular
        if (e.target.className == 'postadd') {
            let id = String(e.target.parentElement.id);
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

            urltab.append(
                '<div class="urlt" style="margin:5px" name="ubody">' +
                '<input type="checkbox" name="download" checked="checked" class="check">'+
                '<div class="urltitm">'+sub+'</div>'+'<div class="urltitm">'+typ+'</div>'+'<div class="urltitm">'+tim+'</div>' +
                '<div style="display:none;">' + id + '</div>' +
                '</div>'
            )
        }
    })

    document.getElementById('hidepanelY').onclick = function() {
        document.getElementById('hidepanel').style.display = "";
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
        urltab.append(
            '<div class="urlt" style="margin:5px" name="ubody">' +
            '<input type="checkbox" name="download" checked="checked" class="check">'+
            '<div class="urltitm">'+red+'</div>'+'<div class="urltitm">'+typ+'</div>'+'<div class="urltitm">'+tim+'</div>' +
            '<div style="display:none;">' + id + '</div>' +
            '</div>'
        )
    }

    function addUrlCD(title, id) {
        urltab.append(
            '<div class="urlt" style="margin:5px" name="ubody">' +
            '<input type="checkbox" name="download" checked="checked" class="check">'+
            '<div class="urltitm">CyberDrop</div><div class="urltitm">'+title+'</div><div class="urltitm"></div>' +
            '<div style="display:none;">' + id + '</div>' +
            '</div>'
        )
    }

    $('#head').on("click",function() {
        let width = window.innerWidth;
        if (width < 768) {
            $('.transform').toggleClass('transform-active');
            $('.urltabbtns').toggleClass('urltabbtns-active');
            $('.urltab-small').toggleClass('urltab-small-active');
        }
        else {
            console.log("not mobile");
        }
    });

    dcnt();

});