// Websocket logic, talks to server.py /pay
// Initiate is called in the <head> of index.html with the payload provided
// by the flask request. The data can not be passed straight from flask to this js
// Hence we {{ load }} it in the index head and call this function.
function initiate(payment_data) {
    namespace = '/';
    var socket = io(namespace);

    // Echo initated message for debugging.
    socket.on('connect', function() {
        socket.emit('initialise', {'data': 'Initialising payment.'});
    });

    // Recieving payment status from flask
    socket.on('payresponse', function(msg, cb) {
        console.log(msg.response);
        // Display payment status
        $('#status').text(msg.status).html();
        // Display payment address
        $('#address').text(msg.address).html();
        // Display payment amount
        $('#amount').text(msg.amount).html();
        // Display payment time left
        $('#timer').text(Math.round(msg.time_left)).html();

        // Run additional logic that manipulates element visibility depending
        // on the contents and status of the payment.
        conditionalPageLogic(msg)

        // If close? I forget..
        if (cb)
            cb();
    });

    // Initiate the payment websocket
    socket.emit('make_payment', payment_data);
    return false
}

// Run additional logic that manipulates element visibility depending
// on the contents and status of the payment when giving a response to the webpage.
function conditionalPageLogic(msg) {
    // Display QR code
    if (msg.address != null) {
        document.getElementById('qrImage').style.display = "block";
        document.getElementById('qrClick').href = "/static/qr_codes/" + msg.uuid + ".png";
        document.getElementById('qrImage').src = "/static/qr_codes/" + msg.uuid + ".png";
    }
    // Hide timer until ready.
    if (msg.time_left == 0) {
        document.getElementById('timerContainer').style.visibility = "hidden";
    }
}

// Payment timer, can't go below zero, update every second
intervalTimer = setInterval(function () {
    var currentTime = document.getElementById('timer').innerHTML;
    if (currentTime <= 0) {
        currentTime = 1;
    }
    document.getElementById('timer').innerHTML = Math.round(currentTime - 1);
}, 1000)

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
