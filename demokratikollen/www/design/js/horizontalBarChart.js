/*
Horizontal bar chart.

data is a list, each element is an objects describing the bar.
[
  {
    title: "bar 1",
    value: 7,
    color: d3.rgb("#element")
  },
  {
    title: "bar 2",
    value: 9,
    color: d3.rgb("#888")
  }
]
*/
demokratikollen.graphics.horizontalBarChart = function() {
  var title = "";
  var margin = { top: 40, right: 50, bottom: 0, left: 0 };
  var barWidth = 0.4;
  var width = 400, height = 200;
  var maxAbsoluteBandWidth = 40;
  var onBarActivated = null;
  var formatter = function(d){return d.value;};

  function chart(selection) {
    selection.each(function(data){

      var parent = d3.select(this);
      var top = parent.selectAll("g").data([0]);
      top.enter()
        .append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var w = width - margin.left - margin.right;
      var h = Math.min(height, maxAbsoluteBandWidth*data.length) - margin.top - margin.bottom;

      var absoluteBarWidth = barWidth * h/data.length;

      var yScale = d3.scale.ordinal()
          .domain(d3.range(data.length))
          .rangeBands([h,0]);

      var maxValue = d3.max(data, prop("value"));
      var xScale = d3.scale.linear()
          .domain([0, maxValue])
          .range([0,w]);

      var titleElement = top.selectAll(".title-text").data([0]);
      titleElement.enter().append("text").attr("class", "title-text");
      titleElement
        .text(title)
        .style("text-anchor","middle")
        .attr("x", w/2)
        .attr("y", -margin.top)
        .attr("dy", "1.5em");


      var barRects = top.selectAll(".bar-rect")
        .data(data, prop("title"));

      barRects.enter().append("rect").attr("class","bar-rect");

      barRects
        .attr("y",function(d,i){return yScale(i)+0.5*h/data.length;})
        .attr("x",0)
        .attr("width", function(d,i){return xScale(d.value);})
        .attr("height", absoluteBarWidth)
        .style("fill", prop("color"));

      barRects.exit()
        .style("fill-opacity",1e-5)
        .remove();

      barTexts = top.selectAll(".bar-text")
        .data(data, prop("title"));

      barTexts.enter().append("text").attr("class","bar-text");

      barTexts
        .text(formatter)
        .style("text-anchor","start")
        .style("alignment-baseline","middle")
        .attr("x", function(d,i){return xScale(d.value);})
        .attr("dx", "0.4em")
        .attr("dy","0.1em")
        .attr("y", function(d,i){return yScale(i)+0.5*h/data.length+0.5*absoluteBarWidth;});

      barTexts.exit().remove();

      barTitles = top.selectAll(".bar-title")
        .data(data, prop("title"));

      barTitles.enter().append("text").attr("class","bar-title");

      barTitles
        .text(function(d){return d.title;})
        .attr("x", 0)
        .attr("dy","-0.2em")
        .attr("y", function(d,i){return yScale(i)+0.5*h/data.length;});

      barTitles.exit().remove();

    });// selection.each
  };

 chart.onBarActivated = function(_) {
    if (!arguments.length) return onBarActivated;
    else onBarActivated = _;
    return chart;
 }
 chart.width = function(_) {
    if (!arguments.length) return width;
    else width = _;
    return chart;
 }
 chart.height = function(_) {
    if (!arguments.length) return height;
    else height = _;
    return chart;
 }
 chart.topMargin = function(_) {
    if (!arguments.length) return margin.top;
    else margin.top = _;
    return chart;
 }
 chart.maxAbsoluteBandWidth = function(_) {
    if (!arguments.length) return maxAbsoluteBandWidth;
    else maxAbsoluteBandWidth = _;
    return chart;
 }
 chart.title = function(_) {
    if (!arguments.length) return title;
    else title = _;
    return chart;
 }
 chart.formatter = function(_) {
    if (!arguments.length) return formatter;
    else formatter = _;
    return chart;
 }

 return chart;
};


