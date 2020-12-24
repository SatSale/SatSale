$(document).ready(function() {
    namespace = '/pay';
    var socket = io(namespace);

    socket.on('connect', function() {
        socket.emit('initialise', {'data': 'initialising payment...'});
    });

    socket.on('payresponse', function(msg, cb) {
        console.log(msg.response);
        $('#status').text(msg.status).html();
        $('#address').text(msg.address).html();
        $('#amount').text(msg.amount).html();
        $('#log').append('<br>' + $('<div/>').text(msg.response).html());
        $('#timer').text(msg.time_left).html();
        if (cb)
            cb();
    });

    $('form#pay').submit(function(event) {
        socket.emit('payment', {'amount': $('#pay_data').val(), 'label' : null});
        return false;
    });
});

intervalTimer = setInterval(function () {
    var currentTime = document.getElementById('timer').innerHTML;
    if (currentTime <= 0) {
        currentTime = 1;
    }
    document.getElementById('timer').innerHTML = Math.round(currentTime - 1);
}, 1000)

function showDiv() {
    if (document.getElementById('pay_data').value > 0) {
        document.getElementById('paymentDetails').style.display = "block";
    }
}

function CopyToClipboard(containerid) {
  if (document.selection) {
    var range = document.body.createTextRange();
    range.moveToElementText(document.getElementById(containerid));
    range.select().createTextRange();
    document.execCommand("copy");
  } else if (window.getSelection) {
    var range = document.createRange();
    range.selectNode(document.getElementById(containerid));
    window.getSelection().addRange(range);
    document.execCommand("copy");
    alert("Copied address!");
  }
}
