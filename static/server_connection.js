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
