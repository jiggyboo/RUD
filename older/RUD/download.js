var urls_to_download = [];
var current_index = 0;
var zip;
var subname_dl = 'sub';
var purl = 'ec2-3-35-138-18.ap-northeast-2.compute.amazonaws.com/api/cors/';

function download_sub(subname, urlList) {
    urls_to_download = urlList;
    zip = new JSZip();
    current_index = 0;
    if (subname) {
        subname_dl = subname;
    }
    download_next_image();
}

var throttle_interval = 1000;
var last_throttle_time = 0;
function throttle(fn) {
    var epoch = (new Date).getTime();
    var time_to_sleep = Math.max(0, (last_throttle_time + throttle_interval) - epoch);
    last_throttle_time = epoch + time_to_sleep;
    setTimeout(fn, time_to_sleep);
}

//1
function download_next_image() {
    throttle(function() {
        ajax_download_blob(urls_to_download[current_index]).then(image_downloaded);
    });
}


//3
function image_downloaded(imgData) {
    zip.file(current_index, imgData, {base64: true});

    if (++current_index >= urls_to_download.length){
        zip.generateAsync({type:"blob"}).then(function(content) {
            saveAs(content, subname_dl+".zip");
        }); 
    }
    else {
        download_next_image();
    }
}

function retry(fn, retries, err) {
    retries = typeof retries !== 'undefined' ? retries : 3;
    err = typeof err !== 'undefined' ? err : null;
    
    if (!retries) {
            return Promise.reject(err);
    }
    return fn().catch(function(err) {
            //console.warn(`retry ${3 - retries}, err ${err}`);
            return retry(fn, (retries - 1), err);
    });
}


//2
function ajax_download_blob(url){
    return new Promise((resolve, reject) => {
        retry(() => {
            return new Promise((resolve, reject) => {
                var xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function() {
                    if (this.readyState === 4) {
                        if (this.status === 200) {
                            resolve(this.response);
                        } else {
                            reject(new Error(`ajax_download_blob(${url}) failed, xhr.status: ${xhr.status}`));
                        }
                    }
                };
                xhr.open('GET', purl+url);
                console.log(url);
                xhr.responseType = 'arraybuffer';
                xhr.send();
            });
        }).then(resolve).catch(console.error);
    })
}

