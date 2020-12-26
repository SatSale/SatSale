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
        $('#timer').text(Math.round(msg.time_left)).html();

        conditionalPageLogic(msg)

        if (cb)
            cb();
    });

    $('form#pay').submit(function(event) {
        socket.emit('payment', {'amount': $('#pay_data').val(), 'label' : null});
        return false;
    });
});

function conditionalPageLogic(msg) {
    if (msg.address != null) {
        document.getElementById('logo').classList.add("qr");
        document.getElementById('logo').src = "static/qr_codes/" + msg.uuid + ".png";
        document.getElementById('qrClick').href = "/static/qr_codes/" + msg.uuid + ".png"
    }

    if (msg.time_left == 0) {
        document.getElementById('timerContainer').style.visibility = "hidden";
    }
}

function hideAmountShowPayment() {
    if (document.getElementById('pay_data').value > 0) {
        document.getElementById('paymentDetails').style.display = "block";
        document.getElementById('paymentForm').style.display = "none";
    }
}

function copyText(text) {
  navigator.clipboard.writeText(text);
}

function copyTextFromElement(elementID) {
  let element = document.getElementById(elementID); //select the element
  let elementText = element.textContent; //get the text content from the element
  copyText(elementText); //use the copyText function below
  alert("Copied address:" + elementText)
}


intervalTimer = setInterval(function () {
    var currentTime = document.getElementById('timer').innerHTML;
    if (currentTime <= 0) {
        currentTime = 1;
    }
    document.getElementById('timer').innerHTML = Math.round(currentTime - 1);
}, 1000)
