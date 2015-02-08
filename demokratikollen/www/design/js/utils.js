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

utils.getInnerWidth = function (selection) {
  var cs = window.getComputedStyle(selection.node());
  return parseInt(cs.width) - parseInt(cs.paddingLeft) - parseInt(cs.paddingRight);
}

utils.sv_SE = {
  "decimal": ",",
    "thousands": " ",
    "grouping": [3],
    "currency": ["", " kr"],
    "dateTime": "%A %e %B %Y %X",
    "date": "%Y-%m%-%d",
    "time": "%H:%M:%S",
    "periods": ["AM", "PM"],
    "days": ["söndag", "måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag"],
    "shortDays": ["sön", "mån", "tis", "ons", "tor", "fre", "lö"],
    "months": ["januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"],
    "shortMonths": ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
}

utils.locale = d3.locale(utils.sv_SE);

utils.pageState = function(obj) {

  var state = {};
  var urlNames = {};
  var keys = {};
  for (var key in obj) {
    if (obj.hasOwnProperty(key)) {
      state[key] = obj[key].defaultValue;
      urlNames[key] = obj[key].urlName;
      keys[obj[key].urlName] = key;
    }
  }
  
  // try to read incoming state from URL
  if (location.hash.length > 1) {
    var queryStringParts = location.hash.substr(1).split("&");
    queryStringParts.forEach(function(part,i){
      var keyValuePair = part.split("=");
      var urlName = keyValuePair[0];
      if (!keys.hasOwnProperty(urlName)) {
        console.warn("Undefined urlName in pageState: ", urlName);
        return;
      }
      var value = decodeURIComponent(keyValuePair[1]);
      if (value == "") value = null;
      var tryInt = parseInt(value, 10);
      if (!isNaN(tryInt)) value = tryInt;

      state[keys[urlName]] = value;
    });
  } 

  return function(obj) {

    if (obj.length) {
      var key = obj;
      if (state.hasOwnProperty(key)) return state[key];
      else return console.warn("Unknown state key: ", obj);
    }

    for (var key in obj) {
      if (obj.hasOwnProperty(key) && state.hasOwnProperty(key)) {
        state[key] = obj[key];
      }
    }

    var parts = [];
    for (var key in state) {
      if (state.hasOwnProperty(key)) {
        parts.push(urlNames[key]+'='+encodeURIComponent(state[key]));
      }
    }

    var newHash = parts.join("&");
    location.hash = '#'+newHash; 
  };
};


utils.uniqueId = (function() {
  var counter = 0;
  return function(prefix) {
    if (!prefix) { prefix = ''; }
    return prefix + '-unique-' + counter;
  }
})();



})(demokratikollen.utils);

