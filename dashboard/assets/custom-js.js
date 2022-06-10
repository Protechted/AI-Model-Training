/*$(document).ready(function () {



});*/

window.addEventListener("DOMContentLoaded", function () {
    let timeleft = 4;
    let intervalid;

    function toggleFunction() {
        const messagefield = document.getElementById("message");
        messagefield.textContent = "Countdown started " + timeleft + " seconds remaining";

        intervalid = window.setInterval( function() {
            if (timeleft === 0){
                document.getElementById('starttraining').click();
                timeleft = 4;
                clearInterval(intervalid);
            }
            messagefield.textContent = "Countdown started " + timeleft + " seconds remaining";
            timeleft --;
        }, 1000);

  }
setTimeout(function() {
console.log("Callback Funktion wird aufgerufen");
    const toggleButton = document.getElementById("starttimer");

  toggleButton.addEventListener("click", toggleFunction);

}, 800);
});