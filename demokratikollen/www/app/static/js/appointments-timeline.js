function AppointmentsTimeline() {

  var lineHeight = 30,
    labelLength = 20,
    lineOffsetY = 10,
    margin = { top: 40, right: 0, bottom: 40, left: 0 }
    timeUnit = null;

  function getMinDate(blocks) { 
    return d3.min(blocks, function (block) { return block.start; });
  }

  function getMaxDate(blocks) { 
    return d3.max(blocks, function (block) { return block.end; });
  }

  function chart(selection) {
    selection.each(function(data) {

      labels = d3.set(data.map(function(d) { return d.name; })).values()

      d3.select(this).classed("chart", true);

      var width = this.getBoundingClientRect().width - margin.left - margin.right,
          height = data.length * lineHeight;

      var svg = d3.select(this)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var x = d3.time.scale()
        .domain([getMinDate(data), getMaxDate(data)])
        .range([0, width])
        .nice();

      var y = d3.scale.ordinal()
        .domain(labels)
        .rangePoints([0, height], 1);

      svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .classed("background", true);

      var xAxis = d3.svg.axis()
        .scale(x)
        .orient("top")
        .tickSize(-height, 5)
        .ticks(2 + Math.floor(width/50));

      xax = svg.append("g")
        .classed("axis x", true)
        .call(xAxis);

      xax.selectAll("text")
        .style("text-anchor", "start");
      xax.select("g.tick:last-of-type text").remove()

      svg.append("g")
        .classed("labels", true)
        .selectAll("labels")
        .data(labels)
        .enter()
        .append("text")
        .text(function(d) { return d; })
        .attr("transform", function(d) { return "translate(0," + y(d) + ")"; });

      var line = d3.svg.line()
        .x(function(d) { return x(d[0]); })
        .y(function(d) { return y(d[1]); })
      
      svg.append("g")
        .classed("lines", true)
        .selectAll("lines")
        .data(data)
        .enter()
        .append("path")
        .attr("d", function(d) { return line([[d.start, d.name], [d.end, d.name]]); })
        .attr("transform", function(d) { return "translate(0," + lineOffsetY + ")"; });

    });
  }
  return chart;
}