/* When the user scrolls down, hide the navbar. When the user scrolls up, show the navbar */

window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    document.getElementsByClassName("navbar").style.top = "0";
  } else {
    document.getElementsByClassName("navbar").style.top = "-50px";
  }
}