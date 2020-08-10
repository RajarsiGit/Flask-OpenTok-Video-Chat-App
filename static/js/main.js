function handleError(error) {
    if (error) {
      alert(error.message);
    }
}
function initializeSession(api_key, session_id, token, name) {
    var session = OT.initSession(api_key, session_id);
    session.on('streamCreated', function(event) {
        subscribeToStreams(event.streams);
    });
    function subscribeToStreams(streams){
        if(streams.length > 6) {
            window.alert("Room Full!")
            return 0;
        }
        for(var i = 0; i < streams.length; i++) {
            var stream = streams[i];
            session.subscribe(stream, 'subscriber', {
                insertMode: 'append',
                width: '100%',
            height: '100%'
            }, handleError);
        }
    }
    var publisher = OT.initPublisher('publisher', {
        insertMode: 'append',
        width: '100%',
        height: '100%',
        name: name
    }, handleError);
    session.connect(token, function(error) {
        if (error) {
            handleError(error);
        }
        else {
            session.publish(publisher, handleError);
        }
    });
}
function copyContent() {
    var copyText = document.getElementById("link");
    copyText.select();
    copyText.setSelectionRange(0, 99999)
    document.execCommand("copy");
  }