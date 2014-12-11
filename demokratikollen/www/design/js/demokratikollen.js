demokratikollen = {};
demokratikollen.utils = {};
var utils = demokratikollen.utils;

utils.parties = d3.map([
  { key: "v", color: "#af0000", order: 0 },
  { key: "fi", color: "#d9308e", order: 1 },
  { key: "pp", color: "#572b85", order: 2 },
  { key: "s", color: "#ee2020", order: 3 },
  { key: "mp", color: "#83cf39", order: 4 },
  { key: "sd", color: "#dddd00", order: 5 },
  { key: "nyd", color: "#dddd00", order: 6 },
  { key: "-", color: "#bbbbbb" , order: 7},
  { key: "c", color: "#009933", order: 8 },
  { key: "m", color: "#1b49dd", order: 9 },
  { key: "fp", color: "#6bb7ec", order: 10 },
  { key: "kd", color: "#231977", order: 11 }
  ],
  function(d) { return d.key; });