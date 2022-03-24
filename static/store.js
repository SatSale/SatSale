function clearSearch() {
    var search = document.getElementById('search');
    search.value = "";

    $("table tr").each(function(index) {
        if (index !== 0) {
            $row = $(this);
            $row.show();
        }
    }
    );
    return;
}

function load_items(items) {
    itemList = items;
    var result = "<table id='itemtable'>";
    var result = result + "<tr><th>Item</th><th>Price</th><th>Quantity</th></tr>";

    var i = 0;
    for (const item of itemList) {
        itemName = item[0];
        itemPrice = item[1];
        itemImage = item[2];
        button = create_value_buttons(i);

        if (itemImage != null) {
            image = "<img src='" + itemImage + "' height=80px></br>";
            itemName = image + itemName;
        }
        result = result + "<tr><td>" + itemName + "</td><td>$" + itemPrice + "</td><td>" + button + "</td></tr>\n";

        i++;
    }
    result = result + "</table>";

    var storeTable = document.getElementById('storetablediv');
    storeTable.innerHTML = result;

    return;
}

function update_receipt(){
    itemList = items;
    var receiptresult = "<table id='itemtable'>";
    var receiptresult = receiptresult + "<tr><th>Item</th><th>Price</th><th>Total</th></tr>";

    var i = 0;
    var total = 0;
    for (const item of itemList) {
        itemName = item[0];
        itemPrice = item[1];
        itemImage = item[2];

        var quantityElement = document.getElementById("itemQuantity" + i);
        if ((quantityElement != null) && (quantityElement.value > 0)) {
            var quantity = quantityElement.value;
            receiptresult = receiptresult + "<tr><td>" + quantity + "x " + itemName + "</td><td>$" + itemPrice + "</td><td>$" + itemPrice*quantity + "</td></tr>\n";
            total += quantity*itemPrice;
        }

        i++;
    }

    document.getElementById("hiddenbaskettotal").value = total;
    // receiptresult = receiptresult + "<tr><td>" + "</td><td>" + "</td><td><b>$" + total + "</b></td></tr>\n"
    receiptresult = receiptresult + "</table>";

    document.getElementById("receipttablediv").innerHTML = receiptresult;
    //var receiptTable = document.getElementById('receipttablediv');
    //receiptTable = receiptresult;

    // From calc.js
    resetCalculator(zero=false);

    return;
}


function increaseValue(itemID) {
  var value = parseInt(document.getElementById("itemQuantity" + itemID).value, 10);
  value = isNaN(value) ? 0 : value;
  value++;
  document.getElementById("itemQuantity" + itemID).value = value;
  updateInvoice();
}

function decreaseValue(itemID) {
  var value = parseInt(document.getElementById("itemQuantity" + itemID).value, 10);
  value = isNaN(value) ? 0 : value;
  value < 1 ? value = 1 : '';
  value--;
  document.getElementById("itemQuantity" + itemID).value = value;
  updateInvoice();
}

function getPriceEstimation() {
    $.getJSON("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", function(data){
        $("#BTCPrice").text(data["bitcoin"]["usd"].toFixed(2));
    }).fail(function( dat, textStatus, error ) {
        var err = textStatus + ", " + error;
        alert(err);
    });
}

function create_value_buttons(itemIndex) {
    var buttonStart = "<div class='value-button' id='decrease' onclick='decreaseValue(" + itemIndex + ");updateInvoice();' value='Decrease Value'>-</div> \
    <input type='number' class='number' id='itemQuantity" + itemIndex + "' placeholder='0' onChange='updateInvoice()'/>\
    <div class='value-button' id='increase' onclick='increaseValue(" + itemIndex + ");updateInvoice();' value='Increase Value'>+</div>";
    return buttonStart;
}

function clearQuantities() {
    var i;
    for (i = 0; i < num_items; i++) {
        document.getElementById("itemQuantity" + i).value = 0;
    }
    return;
}

function showHideCalc() {
  var x = document.getElementById("calculator-div");
  if (x.style.display === "none") {
    x.style.display = "";
  } else {
    x.style.display = "none";
  }
}

function getAmountBTC(invoice_total) {
    var price = document.getElementById("BTCPrice").innerHTML;
    var amount_bitcoin = invoice_total / price;
    amount_bitcoin = amount_bitcoin.toFixed(8);
    console.log(invoice_total, amount_bitcoin, price);
    return amount_bitcoin;
}

function updateTotals(invoice_total, amount_bitcoin) {
    console.log(invoice_total, amount_bitcoin);
    if (Number.isNaN(parseFloat(amount_bitcoin))) {
        invoice_total = 0;
        amount_bitcoin = 0;
    }

    document.getElementById("invoicetotal").innerHTML = Number.parseFloat(invoice_total).toFixed(2);
    document.getElementById("sats_amount").innerHTML = Math.round(amount_bitcoin * 10**8);
    document.getElementById("btc_amount").innerHTML = Number.parseFloat(amount_bitcoin).toFixed(8);
    document.getElementById("amount").value = invoice_total;
    return;
}

function updateInvoice() {
    var i;
    var invoice_total = 0;
    for (i = 0; i < num_items; i++) {
        invoice_total = invoice_total + document.getElementById("itemQuantity" + i).value * items[i][1];
    }
    var amount_bitcoin = getAmountBTC(invoice_total);
    updateTotals(invoice_total, amount_bitcoin);
    update_receipt();
    return;
}

function main(items) {
    num_items = items.length;
    getPriceEstimation();
    load_items(items);
}
