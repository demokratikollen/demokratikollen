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
