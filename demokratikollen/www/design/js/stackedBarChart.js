/*
Upright stacked bar chart.

data: object x-labels "labels" and bar-data "bars"."
"bars" is a list, each element is a list of objects describing pieces.
{
  labels: ["X-label 1", "X-label 2"],
  bars:
      [
        [
          {
            title: "bar 1 piece 1",
            value: 7,
            color: d3.rgb("#888")
          },
          {
            title: "bar 1 piece 2",
            value: 9,
            color: d3.rgb("#888")
          }
        ],
        [
          {
            title: "bar 2 piece 1",
            value: 1,
            color: d3.rgb("#888")
          },
          {
            title: "bar 2 piece 2",
            value: 2,
            color: d3.rgb("#888")
          }
        ]
      ]
}
*/
demokratikollen.graphics.stackedBarChart = function() {
  var width = 400, height = 200;
  var title = "";
  var margin = { top: 25, right: 10, bottom: 60, left: 10 };
  var barWidth = 0.6;
  var maxAbsoluteBandWidth = 50;

  var onBarActivated = null;

  var currentlyActive = null;


  function chart(selection) {
    selection.each(function(data){
      data.bars.forEach(function(bar,bar_idx){
        bar.total = d3.sum(bar, prop("value"));
        bar.rectData = [];
        bar.forEach(function(p,i,a){
          var rect = {};
          if (i == 0) {
            rect.y0 = 0;
          } else {
            rect.y0 = bar.rectData[i-1].y1;
          }
          rect.y1 = rect.y0 + p.value;
          rect.x = bar_idx;
          rect.color = p.color;
          rect.title = p.title;
          bar.rectData.push(rect);
        });
      });

      var parent = d3.select(this);
      var top = parent.selectAll("g").data([0]);
      top.enter()
        .append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var w = Math.min(
            width,
            maxAbsoluteBandWidth * data.labels.length
            ) - margin.left - margin.right;
      var h = height - margin.top - margin.bottom;

      var absoluteBarWidth = barWidth * w/data.labels.length;

      var xScale = d3.scale.ordinal()
          .domain(d3.range(data.labels.length))
          .rangeBands([0,w]);

      var xAxis = d3.svg.axis()
          .scale(xScale)
          .tickFormat(function(d) { return data.labels[d]; })
          .orient("bottom");

      var xAxisElement = top.selectAll(".x-axis").data([0]);
      xAxisElement.enter().append("g").attr("class", "axis x-axis");

      xAxisElement
        .attr("transform", "translate(0," + h + ")")
        .call(xAxis)
        .selectAll("text")
          .style("text-anchor", "end")
          .attr("dx", "-.8em")
          .attr("dy", ".15em")
          .attr("transform","rotate(-75)");


      var titleElement = top.selectAll(".title-text").data([0]);
      titleElement.enter().append("text").attr("class", "title-text");
      titleElement
        .text(title)
        .style("text-anchor","middle")
        .attr("x", w/2)
        .attr("y", -margin.top)
        .attr("dy", "1.5em");

      var maxValue = d3.max(data.bars, prop("total"));
      var yScale = d3.scale.linear()
          .domain([0, maxValue])
          .range([h,0]);

      var barGroups = top.selectAll(".bar-group").data(data.bars);
      barGroups.enter()
        .append("g").attr("class", "bar-group")
          .append("text").attr("class","bar-text");

      barGroups.exit().remove();

      var barRects = barGroups.selectAll(".bar-rect")
        .data(prop("rectData"),function(d){return d.title;});

      barRects.enter().append("rect").attr("class","bar-rect");

      barRects
        .attr("x", function(d){return xScale(d.x)+0.5*(xScale(1)-absoluteBarWidth);})
        .attr("y", function(d){return yScale(d.y1);})
        .attr("height", function(d,i){return yScale(d.y0)-yScale(d.y1);})
        .attr("width", absoluteBarWidth)
        .style("fill", prop("color"));

      barRects.exit()
        .style("fill-opacity",1e-5)
        .remove();

      var barTexts = barGroups.select(".bar-text");
      barTexts
        .text(prop("total"))
        .style("text-anchor","middle")
        .attr("x", function(d,i){return xScale(i)+0.5*(xScale(1));})
        .attr("y", function(d){return yScale(d.total)})
        .attr("dy","-0.1em");


      var clickRects = top.selectAll(".click-rect").data(data.bars);

      function activateBar(i) {
        var d = data.bars[i];
        if (currentlyActive != null) {
          d3.select(clickRects[0][currentlyActive]).style("fill-opacity","");
        }
        d3.select(clickRects[0][i]).style("fill-opacity",0.3);
        if (onBarActivated) onBarActivated(d,i);
        currentlyActive = i;
      };
      function deActivateBar(i) {
        var d = data.bars[i];
        if (currentlyActive != null) {
          d3.select(clickRects[0][currentlyActive]).style("fill-opacity","");
        }
        currentlyActive = null;
      };

      clickRects.enter().append("rect").attr("class", "click-rect");

      clickRects
        .attr("x", function(d,i){return xScale(i);})
        .attr("y", yScale(maxValue))
        .attr("width", xScale(1))
        .attr("height",h+margin.bottom)
        .on("mouseover",function(d,i){
          if (currentlyActive == i) return;
          d3.select(this).style("fill-opacity",0.2);
        })
        .on("mouseout",function(d,i){
          if (currentlyActive == i) return;
          d3.select(this).style("fill-opacity","");
        })
        .on("click",function(d,i){
          if (currentlyActive == i) return;
          deActivateBar(currentlyActive);
          activateBar(i);
        });

      // reactivate selection when updating data
      if (currentlyActive != null) activateBar(currentlyActive);
    });
  };

 chart.onBarActivated = function(_) {
    if (!arguments.length) return onBarActivated;
    else onBarActivated = _;
    return chart;
 }
 chart.width = function(_) {
    if (!arguments.length) return width;
    else width = +_;
    return chart;
 }
 chart.height = function(_) {
    if (!arguments.length) return height;
    else height = +_;
    return chart;
 }
 chart.bottomMargin = function(_) {
    if (!arguments.length) return margin.bottom;
    else margin.bottom = +_;
    return chart;
 }
 chart.maxAbsoluteBandWidth = function(_) {
    if (!arguments.length) return maxAbsoluteBandWidth;
    else maxAbsoluteBandWidth = +_;
    return chart;
 }
 chart.currentlyActive = function(_) {
    if (!arguments.length) return currentlyActive;
    else currentlyActive = _;
    return chart;
 }
 chart.title = function(_) {
    if (!arguments.length) return title;
    else title = _;
    return chart;
 }

 return chart;
};
