// Websocket logic, talks to server.py pay
$(document).ready(function() {
    namespace = '/pay';
    var socket = io(namespace);

    socket.on('connect', function() {
        socket.emit('initialise', {'data': 'Initialising payment.'});
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

// Additional steps to take when giving a response to the webpage
// Update qr code, and hide timer
function conditionalPageLogic(msg) {
    if (msg.address != null) {
        document.getElementById('logo').classList.add("qr");
        // document.getElementById('logo').src = "static/qr_codes/" + msg.uuid + ".png";
        document.getElementById('logo').style.display = "none";
        document.getElementById('qrImage').style.display = "block";
        document.getElementById('qrClick').href = "/static/qr_codes/" + msg.uuid + ".png";
        document.getElementById('qrImage').src = "/static/qr_codes/" + msg.uuid + ".png";
    }

    if (msg.time_left == 0) {
        document.getElementById('timerContainer').style.visibility = "hidden";
    }
}

// Hide payment form and show payment details when payment is initiated
function hideAmountShowPayment() {
    if (document.getElementById('pay_data').value > 0) {
        document.getElementById('paymentDetails').style.display = "block";
        document.getElementById('paymentForm').style.display = "none";
    }
}

// Copy text functions
function copyText(text) {
  navigator.clipboard.writeText(text);
}

function copyTextFromElement(elementID) {
  let element = document.getElementById(elementID); //select the element
  let elementText = element.textContent; //get the text content from the element
  copyText(elementText); //use the copyText function below
  alert("Copied address:" + elementText)
}

// Payment timer, can't go below zero, update every second
intervalTimer = setInterval(function () {
    var currentTime = document.getElementById('timer').innerHTML;
    if (currentTime <= 0) {
        currentTime = 1;
    }
    document.getElementById('timer').innerHTML = Math.round(currentTime - 1);
}, 1000)
