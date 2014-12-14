var utils = demokratikollen.utils;

utils.parties = d3.map([
  { key: "v", color: "#af0000" },
  { key: "fi", color: "#d9308e" },
  { key: "pp", color: "#572b85" },
  { key: "s", color: "#ee2020" },
  { key: "mp", color: "#83cf39" },
  { key: "sd", color: "#dddd00" },
  { key: "nyd", color: "#dddd00" },
  { key: "-", color: "#bbbbbb" },
  { key: "c", color: "#009933" },
  { key: "m", color: "#1b49dd" },
  { key: "fp", color: "#6bb7ec" },
  { key: "kd", color: "#231977" }
  ],
  function(d) { return d.key; });

utils.colors = d3.map([
  { key: "green", color: "#4cd42f" },
  { key: "yellow", color: "#ebeb2b" },
  { key: "red", color: "#cb1310"}
  ],
  function(d) { return d.key; });

// Copy party colors to colors
utils.parties.forEach(
  function(key, party) { utils.colors.set(key, { key: party.key, color: party.color}); });