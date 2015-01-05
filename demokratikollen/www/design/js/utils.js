(function(utils){

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

utils.getPartyColor = function(abbr) {
  return d3.rgb(demokratikollen.utils.colors.get(abbr.toLowerCase())["color"]);
};

utils.pageState = function(obj) {
  var delim = "-"
  var state = {};
  var orderedKeys = [];
  for (var key in obj) {
    if (obj.hasOwnProperty(key)) {
      state[key] = obj[key];
      orderedKeys.push(key);
    }
  }
  orderedKeys.sort();
  
  // try to read incoming state from URL
  if (location.hash.length > 1) {
    var values = location.hash.substr(1).split(delim);
    if (values.length == orderedKeys.length) {
      values.forEach(function(value,i){
        if (value == "") value = null;
        var tryInt = parseInt(value, 10);
        if (!isNaN(tryInt)) value = tryInt;

        state[orderedKeys[i]] = value;
      });
    } else {
      console.log("Warning: given pageStatus hash not compatible with state specification.");
    }
  } 

  return function(obj) {

    if (obj.length) {
      var key = obj;
      if (state.hasOwnProperty(key)) return state[key];
    }

    for (var key in obj) {
      if (obj.hasOwnProperty(key) && state.hasOwnProperty(key)) {
        state[key] = obj[key];
      }
    }
    var newHash = orderedKeys.map(function(key){return state[key];}).join(delim);
    location.hash = '#'+newHash; 
  };
};




})(demokratikollen.utils);

