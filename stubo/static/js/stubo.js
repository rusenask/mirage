
function show_alert(message, alerttype) {
    $('#alert_placeholder').append('<div id="alertdiv" class="alert ' +  alerttype + '"><a class="close" data-dismiss="alert">×</a><span>'+message+'</span></div>')
    // automatically close info messages after 3 secs, leave warnings & errors for the user to close.
    if (alerttype === "alert-info") {
        setTimeout(function() { 
          $("#alertdiv").remove();
        }, 3000);
    }
}

function changeAllHosts(from, to) {
    return(window.location.href.replace("all_hosts="+from, "all_hosts="+to));
}

function beautify(text, btn_id, text_id) {
    $(btn_id).on('click', function (e) {
        $(this).toggleClass("active");
        if ($(this).hasClass("active")) { 
            var pretty_text;
            try {
               JSON.parse(text);
               pretty_text = vkbeautify.json(text);   
            }
            catch(err) {
                pretty_text = vkbeautify.xml(text); 
            } 
            $(text_id).text(pretty_text);         
        } else {
            $(text_id).text(text); 
        }
    });    
}     

$(document).ready(function() {

    var urlParams;
    (window.onpopstate = function () {
        var match,
            pl     = /\+/g,  // Regex for replacing addition symbol with a space
            search = /([^&=]+)=?([^&]*)/g,
            decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
            query  = window.location.search.substring(1);
    
        urlParams = {};
        while (match = search.exec(query))
           urlParams[decode(match[1])] = decode(match[2]);
    })();

    var all_hosts_set = ($.cookie("stubo.all-hosts") === 'true');
    $('input#all_hosts').prop("checked", all_hosts_set);
    $("li#manage a").prop("href", "/manage?all_hosts="+all_hosts_set);  
    $("li#tracker a").prop("href", "/tracker?all_hosts="+all_hosts_set); 
    $("input#tracker-filter-all-hosts").prop("value", all_hosts_set);  

    var d = new Date();
    d.setDate(d.getDate() + 7);

    // navbar 'show all hosts' checkbox
    $('#all_hosts').click(function () {
        var thisCheck = $(this);
        var allHosts = thisCheck.is (':checked');
        show_alert("all hosts set to " + allHosts, "alert-info");
        $.cookie("stubo.all-hosts", allHosts, {expires: d});   
        $("li#manage a").prop("href", "/manage?all_hosts="+allHosts); 
        $("li#tracker a").prop("href", "/tracker?all_hosts="+allHosts); 
        $("input#tracker-filter-all-hosts").prop("value", allHosts);   
        window.location.href = changeAllHosts(urlParams["all_hosts"], ""+allHosts);     
    });
     $('#all_hosts_label').click(function () {                                                  
     $('#all_hosts').click()
     });                                                                                 

 
    $("#latency").change(function () {
    if (document.getElementById("latency").value == ""){
        document.getElementById("latency").value = "0";
        window.alert("Please enter a number greater than 0!");
    }
    else if (isNaN(document.getElementById("latency").value)){
        document.getElementById("latency").value = "0";
        window.alert("Please enter a number greater than 0!");
    }

  });



});
