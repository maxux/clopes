var socket;

function connect() {
    socket = new WebSocket("ws://10.241.0.106:2010/");

    socket.onopen = function() {
        console.log("websocket open");
        $('#disconnected').hide();
    }

    socket.onmessage = function(msg) {
        json = JSON.parse(msg.data);
        console.log(json);

        if(json['type'] == 'update') {
            $("#outside").empty();
            $("#queue").empty();

            var outside = json['payload']['outside'];

            for(var c in outside)
                $("#outside").append($("<li>").append($("<span>").html(outside[c])));

            var queue = json['payload']['queue'];

            for(var c in queue)
                $("#queue").append($("<li>").append($("<span>").html(queue[c])));

            if(outside.length == 0)
                $("#outside-free").show();
            else
                $("#outside-free").hide();

            if(queue.length == 0)
                $("#queue-empty").show();
            else
                $("#queue-empty").hide();

            $("#outside-body").removeClass("okay");
            $("#outside-body").removeClass("warning");
            $("#outside-body").removeClass("full");

            if(outside.length > 2) {
                $("#outside-body").addClass("full");

            } else if(outside.length > 1) {
                $("#outside-body").addClass("warning");

            } else {
                $("#outside-body").addClass("okay");
            }
        }
    }

    socket.onclose = function() {
        $('#disconnected').show();
        setTimeout(connect, 2000);
    }
}


$(document).ready(function() {
    connect();
});
