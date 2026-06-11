// Minimal stand-in for the original slick fade slideshow.
(function () {
  var slides = document.querySelectorAll('.slideshow .StartContentGrid');
  if (!slides.length) return;
  var i = 0;
  slides[0].classList.add('slick-current');
  setInterval(function () {
    slides[i].classList.remove('slick-current');
    i = (i + 1) % slides.length;
    slides[i].classList.add('slick-current');
  }, 3000);
})();
