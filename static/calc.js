/* MIT LICENSE */
/* https://freshman.tech/calculator/ */

const calculator = {
  displayValue: '0',
  firstOperand: null,
  waitingForSecondOperand: false,
  operator: null,
};

function overwriteInvoiceWithCalc(invoice_total_sats) {
    var amount_bitcoin = invoice_total_sats / 10**8;
    var amount_USD = amount_bitcoin*1/getAmountBTC(1);
    // From store.js
    updateTotals(amount_USD, amount_bitcoin);
    return;
}


function inputDigit(digit) {
  const { displayValue, waitingForSecondOperand } = calculator;

  if (waitingForSecondOperand === true) {
    calculator.displayValue = digit;
    calculator.waitingForSecondOperand = false;
  } else {
    calculator.displayValue = displayValue === '0' ? digit : displayValue + digit;
  }
}

function inputDecimal(dot) {
  if (calculator.waitingForSecondOperand === true) {
  	calculator.displayValue = "0."
    calculator.waitingForSecondOperand = false;
    return
  }

  if (!calculator.displayValue.includes(dot)) {
    calculator.displayValue += dot;
  }
}

function minusFivePercent() {
    const { firstOperand, displayValue, operator } = calculator
    const inputValue = parseFloat(displayValue);
    var result = 0.95*inputValue;

    calculator.displayValue = `${parseFloat(result.toFixed(7))}`;
    overwriteInvoiceWithCalc(calculator.displayValue);
    return;
}

function handleOperator(nextOperator) {
  const { firstOperand, displayValue, operator } = calculator
  const inputValue = parseFloat(displayValue);

  if (operator && calculator.waitingForSecondOperand)  {
    calculator.operator = nextOperator;
    return;
  }


  if (firstOperand == null && !isNaN(inputValue)) {
    calculator.firstOperand = inputValue;
  } else if (operator) {
    const result = calculate(firstOperand, inputValue, operator);

    calculator.displayValue = `${parseFloat(result.toFixed(7))}`;
    calculator.firstOperand = result;
    overwriteInvoiceWithCalc(calculator.displayValue);
  }

  calculator.waitingForSecondOperand = true;
  calculator.operator = nextOperator;
}

function calculate(firstOperand, secondOperand, operator) {
  if (operator === '+') {
    return firstOperand + secondOperand;
  } else if (operator === '-') {
    return firstOperand - secondOperand;
  } else if (operator === '*') {
    return firstOperand * secondOperand;
  } else if (operator === '/') {
    return firstOperand / secondOperand;
  }

  return secondOperand;
}

function resetCalculator(zero=true) {
  var hidden_total = document.getElementById('hiddenbaskettotal').value;
  var amount_bitcoin = getAmountBTC(hidden_total);

  if (zero) {
      calculator.displayValue = Math.round(amount_bitcoin * 10**8);
  }
  else {
      calculator.displayValue = document.getElementById('sats_amount').innerHTML;
      // document.getElementById('hiddenbaskettotal').value;
  }


  updateTotals(hidden_total, amount_bitcoin);
  updateDisplay();


  calculator.firstOperand = null;
  calculator.waitingForSecondOperand = false;
  calculator.operator = null;
}

function updateDisplay() {
  const display = document.querySelector('.calculator-screen');
  display.value = calculator.displayValue;
}

updateDisplay();

const keys = document.querySelector('.calculator-keys');
keys.addEventListener('click', event => {
  const { target } = event;
  const { value } = target;
  if (!target.matches('button')) {
    return;
  }

  switch (value) {
    case '+':
    case '-':
    case '*':
    case '/':
    case '=':
      handleOperator(value);
      break;
    case '.':
      inputDecimal(value);
      break;
    case 'all-clear':
      resetCalculator();
      break;
    case 'm5':
      minusFivePercent();
    default:
      if (Number.isInteger(parseFloat(value))) {
        inputDigit(value);
      }
  }

  updateDisplay();
});
