/*------------------------------------------------------------------
* Project: INTERIOR-PROJECT
* File:    animation.js  — Scroll-reveal & entrance animations
-------------------------------------------------------------------*/
(function ($) {
  "use strict";

  $(document).ready(function () {

    /* Intersection Observer for fade-in on scroll */
    if ('IntersectionObserver' in window) {
      const targets = document.querySelectorAll(
        '.service-box, .portfolio-box, .process-box, .why-us-box, .blog-box, .about-us-inner'
      );

      const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15 });

      targets.forEach(function (el) { observer.observe(el); });
    }

    /* Animated counter for stats */
    function animateCounters() {
      $('.about-right .h2').each(function () {
        var $el = $(this);
        var target = parseInt($el.text(), 10);
        if (isNaN(target)) return;
        $({ count: 0 }).animate({ count: target }, {
          duration: 1800,
          easing: 'swing',
          step: function () {
            $el.text(Math.ceil(this.count) + '+');
          },
          complete: function () {
            $el.text(target + '+');
          }
        });
      });
    }

    /* Trigger counter when about section enters viewport */
    if ('IntersectionObserver' in window) {
      var counterDone = false;
      var aboutEl = document.querySelector('.about-us');
      if (aboutEl) {
        var counterObserver = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting && !counterDone) {
              counterDone = true;
              animateCounters();
            }
          });
        }, { threshold: 0.3 });
        counterObserver.observe(aboutEl);
      }
    }

  });

})(jQuery);
