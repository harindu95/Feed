console.error("My Script !!!!!!!!!");

function loadScript(url, callback) {
    // adding the script element to the head as suggested before
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;

    // then bind the event to the callback function 
    // there are several events for cross browser compatibility
    script.onreadystatechange = callback;
    // script.onload = callback;

    // fire the loading
    head.appendChild(script);
}

source = 'qrc:///qtwebchannel/qwebchannel.js';
var script = document.createElement('script');
script.type = 'text/javascript';
script.src = source;
async function execute() {
    // const lib = await fetch(source);
    // eval(lib);      
    document.addEventListener("DOMContentLoaded", function (event) {

        document.head.appendChild(script);
        script.onload = function (){
            console.error("Script Loaded!")
            channel = new QWebChannel(qt.webChannelTransport, function (channel) {
                var sharedObject = channel.objects.shared;
                shared.addText(document.body.innerText)
            });
        };
       
        console.error('Document content')
        // console.error(document.body.innerText);

    });
}


document.body.innerText;
