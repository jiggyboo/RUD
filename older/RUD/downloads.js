"use strict";

var urls_to_download = [];
var image_names_to_download = [];
var currently_downloading_url_index = 0;
var zip;
var galleryname_to_download = 'hitomi';

function user_lang() {
        var userLang = navigator.language || navigator.userLanguage;
        return userLang.toLowerCase();
}

function is_english() {
        var userLang = user_lang();
        return /^en/.test(userLang);
}

function is_british() {
        var userLang = user_lang();
        return /^en-gb/.test(userLang);
}

function is_japanese() {
        var userLang = user_lang();
        return /^ja/.test(userLang);
}

function is_korean() {
        var userLang = user_lang();
        return /^ko/.test(userLang);
}

function is_russian() {
        var userLang = user_lang();
        return /^ru/.test(userLang);
}

function download_gallery(galleryname) {
        $("#dl-button").hide();
        var progressbar = $( "#progressbar" );
        progressbar.show();
        progressbar.progressbar({
                value: false
        });
        
        urls_to_download = [];
        image_names_to_download = [];
        $.each(galleryinfo['files'], function(i, image) {
                var url = url_from_url_from_hash(galleryid, image);
                urls_to_download.push(url);
                image_names_to_download.push(image.name);
        });
        zip = new JSZip();
        currently_downloading_url_index = 0;
        if (galleryname) {
                galleryname_to_download = galleryname;
        }
        download_next_image();
}

var throttle_interval_ms = 1000;
var last_throttle_time_ms = 0;
function throttle(fn) {
        var epoch_ms = (new Date).getTime();
        var time_to_sleep_ms = Math.max(0, (last_throttle_time_ms + throttle_interval_ms) - epoch_ms);
        last_throttle_time_ms = epoch_ms + time_to_sleep_ms;
        setTimeout(fn, time_to_sleep_ms);
}

function download_next_image() {
        throttle(function() {
                ajax_download_blob(urls_to_download[currently_downloading_url_index]).then(image_downloaded);
        });
}

function image_downloaded(imgData) {
        var progressbar = $( "#progressbar" );
        progressbar.progressbar( "value", (currently_downloading_url_index+1)/urls_to_download.length*100);
        zip.file(image_names_to_download[currently_downloading_url_index], imgData, {base64: true});
        
        if (++currently_downloading_url_index >= urls_to_download.length) {
                zip.generateAsync({type:"blob"}).then(function(content) {
                        saveAs(content, galleryname_to_download+".zip");
                });
                progressbar.hide();
                $("#dl-button").show();
        } else {
                download_next_image();
        }
}

function ajax_download_blob(url) {
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
                                xhr.open('GET', url);
                                xhr.responseType = 'arraybuffer';
                                xhr.send();    
                        });
                }).then(resolve).catch(console.error);
        });
}
