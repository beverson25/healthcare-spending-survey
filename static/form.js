// Enables an amount box only when its checkbox is ticked.
document.querySelectorAll('input[type="checkbox"][data-target]').forEach(function (box) {
  var amount = document.getElementById(box.dataset.target);
  function sync() {
    amount.disabled = !box.checked;
    if (box.checked) { amount.focus(); } else { amount.value = ''; }
  }
  box.addEventListener('change', sync);
});
