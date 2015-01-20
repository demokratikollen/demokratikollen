demokratikollen = {};
demokratikollen.utils = {};
demokratikollen.graphics = {};

// global utils (aka danger zone)

function prop(p) {
  return function(d) {
    return d[p];
  };
}

function compose(f,g) {
  return function(d) {
    return f(g(d));
  };
}

//google analytics
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-58748015-1', 'auto');
ga('send', 'pageview');