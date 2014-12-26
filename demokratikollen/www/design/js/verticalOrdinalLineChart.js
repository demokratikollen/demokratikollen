/*

data:
{
  labels: ["label 1", "label 2", "label 3"],
  series: [
   {
    title: "series 1",
    color: d3.rgb("#f00"),
    values: [0.5,0.8, 1.0]
   },
   {
    title: "series 2",
    color: d3.rgb("#ff0"),
    values: [-0.5,0.0, 0.2]
   }
  ]
}


*/
demokratikollen.graphics.verticalOrdinalLineChart = function() {
  var margin = { top: 25, right: 20, bottom: 25, left: 60 };
  var width = 400, height = 200;
  var onLineActivated = null;
  var markerSize = 8;

  function chart(selection) {
    selection.each(function(data){

      data.series.forEach(function(s){
        s.markerData = s.values.map(function(v,i){
            return {x: v, y: i, color: s.color};
        }).filter(function(d){return d.x != null;});

      });

      var parent = d3.select(this);
      var top = parent.selectAll("g").data([0]);
      top.enter()
        .append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var w = width - margin.left - margin.right;
      var h = height - margin.top - margin.bottom;

      var yScale = d3.scale.ordinal()
          .domain(d3.range(data.labels.length))
          .rangePoints([h,0]);

      var xScale = d3.scale.linear()
          .domain([-1.1,1.1])
          .range([0,w]);

      var yAxis = d3.svg.axis()
        .scale(yScale)
        .tickFormat(function(d, i) { return data.labels[d]; })
        .orient("left");

      var lineGenerator = d3.svg.line()
          .x(function(d,i) { return xScale(d); })
          .y(function(d,i) { return yScale(i); })
          .defined(function(d,i) { return d != null; });

      var yAxisElement = top.selectAll(".y-axis").data([0]);
      yAxisElement.enter().append("g").attr("class","axis y-axis");
      yAxisElement.call(yAxis);

      yAxisElement.exit().remove();

      var seriesGroups = top.selectAll(".series-group")
        .data(data.series, prop("title"));

      seriesGroups.enter().append("g").attr("class","series-group");

      seriesGroups.exit()
        .style("opacity",1e-5)
        .remove();

      var paths = seriesGroups.selectAll(".line-path")
        .data(function(d){return [d];});

      paths.enter().append("path").attr("class","line-path");

      paths
        .style("stroke", prop("color"))
        .attr("d", function(d){return lineGenerator(d.values);});

      paths.exit()
        .style("opacity", 1e-5)
        .remove();

      var markers = seriesGroups.selectAll(".line-marker")
        .data(function(d){return d.markerData;});

      markers.enter().append("circle").attr("class","line-marker");

      markers
        .attr("cy", compose(yScale,prop("y")))
        .attr("cx", compose(xScale,prop("x")))
        .attr("r", markerSize*0.5)
        .style("stroke", prop("color"));
    
      markers.exit()
        .style("opacity",1e-5)
        .remove();



    });// selection.each
  };

 chart.onLineActivated = function(_) {
    if (!arguments.length) return onLineActivated;
    else onLineActivated = _;
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
 chart.title = function(_) {
    if (!arguments.length) return title;
    else title = _;
    return chart;
 } 

 return chart;
};
