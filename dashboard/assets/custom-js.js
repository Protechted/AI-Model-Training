/*$(document).ready(function () {



});*/

window.addEventListener("DOMContentLoaded", function () {

    function toggleFunction() {
    alert("test");
  }
setTimeout(function() {
console.log("Callback Funktion wird aufgerufen");
    const toggleButton = document.getElementById("starttimer");

  toggleButton.addEventListener("click", toggleFunction);

}, 3000);
});