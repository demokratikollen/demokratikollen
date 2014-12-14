demokratikollen = {};
demokratikollen.utils = {};
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

utils.parties.forEach(function(key, party) { utils.colors.set(key, { key: party.key, color: party.color}); });
                      
data = utils.colors
var labels = data.keys();
var height = labels.length * 30;
var width = 200;

xScale = d3.scale.linear()
    .domain([0, 1])
    .range([0, width]);
yScale = d3.scale.ordinal()
    .domain(labels)
    .rangePoints([0, height], 1);

d3.select("#parties")
    .append("svg")
    .attr("height", height+40)
    .selectAll("parties")
    .data(data.values())
    .enter()
    .append("rect")
    .classed("party", true)
    .style("fill", function(d) { return d.color; })
    .attr("width", width)
    .attr("height", 20)
    .attr("transform", function(d) { return "translate(0," + yScale(d.key) + ")"; } );

chart = positionPicker()
    .xScale(xScale)
    .yScale(yScale)
    .vertical(false);
chart(d3.select("#parties svg"));


function positionPicker() {
  var xScale = null,
      yScale = null,
      xMin = 0,
      xMax = 0,
      yMin = 0,
      yMax = 0,
      horizontal = true,
      vertical = true;
    
  function chart(selection) {
      selection.each(function(data) {
          
          svg = d3.select(this);
          var horzLine = null,
              vertLine = null;
          
          if (xScale) {
              var extent = d3.extent(xScale.range());
              if (!xMin) { xMin = extent[0]; }
              if (!xMax) { xMax = extent[1]; }
          }
          if (yScale) {
              var extent = d3.extent(yScale.range());
              if (!yMin) { yMin = extent[0]; }
              if (!yMax) { yMax = extent[1]; }
          }
          if (vertical) {
              vertLine = svg.append("line")
                  .classed("vertLine", true)
                  .attr("x1", xMin)
                  .attr("x2", xMin)
                  .attr("y1", yMin)
                  .attr("y2", yMax);
          }
          if (horizontal) {
              horzLine = svg.append("line")
                  .classed("horzLine", true)
                  .attr("x1", xMin)
                  .attr("x2", xMax)
                  .attr("y1", yMin)
                  .attr("y2", yMin);
          }
              
          
          hide();
         
          function hide() {
              ([vertLine, horzLine]).forEach(
                  function (line) { 
                      if (line) { line.style("display", "none"); }
                  });
          }
          
          function drawAndShow() {
              if (vertLine) {
                  vertLine
                      .attr("x1", x).attr("x2", x)
                      .style("display", "inline");
              }
              if (horzLine) {
                  horzLine
                      .attr("y1", y).attr("y2", y)
                      .style("display", "inline");
              }
          }
          
          var mouseMove = function() {
              var pos = d3.mouse(this);
              x = pos[0];
              y = pos[1];
              
              if (xMin <= x && x <= xMax && yMin <= y && y <= yMax) {
                  drawAndShow();
              } else {
                  hide();
              }
          }
          
          svg.on("mousemove", mouseMove);
          svg.on("mouseout", hide);
          
      });
  }
                     
  chart.xScale = function(value) {
    if (!arguments.length) return xScale;
    xScale = value;
    return chart;
  };
                         
  chart.yScale = function(value) {
    if (!arguments.length) return yScale;
    yScale = value;
    return chart;
  };
    
  chart.yMin = function(value) {
    if (!arguments.length) return yMin;
    yMin = value;
    return chart;
  };

  chart.yMax = function(value) {
    if (!arguments.length) return yMax;
    yMax = value;
    return chart;
  };

  chart.xMin = function(value) {
    if (!arguments.length) return xMin;
    xMin = value;
    return chart;
  };

  chart.xMax = function(value) {
    if (!arguments.length) return xMax;
    xMax = value;
    return chart;
  };

  chart.horizontal = function(value) {
    if (!arguments.length) return horizontal;
    horizontal = value;
    return chart;
  };

  chart.vertical = function(value) {
    if (!arguments.length) return vertical;
    vertical = value;
    return chart;
  };


  return chart;
}
