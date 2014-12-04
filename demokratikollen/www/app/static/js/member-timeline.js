function AppointmentsTimeline(config) {
  function chart(selection) {
    selection.each(function(data) {
      var svg = d3.select(this)
      
      var line = d3.svg.line()

      numAppointments = data.length
      ordering = function(a, b) {
        endDiff = a.end - b.end;
        if (endDiff) {
          return endDiff;
        } else {
          return a.start - b.start
        }
      }
      data.sort(ordering)

            var width = 700,
          height = numAppointments * 24;

      var x = d3.scale.time()
          .nice()

      var y = d3.scale.ordinal()
          .domain(d3.range(yticklabels.length))
          .rangePoints([height, 0]);

      var yAxis = d3.svg.axis()
          .scale(y)
          .tickFormat(function(d, i) { return yticklabels[d]; })
          .orient("left");

      var line = d3.svg.line()
          .x(function(d,i) { return x(d[1]); })
          .y(function(d,i) { return y(d[0]); })
          .defined(function(d,i) { return !isNaN(d[1]); });

      var paths = svg.selectAll( "path" )
        .data(parties);

      paths.enter().append("path");

      paths
        .classed({"line":true})
        .style("stroke", function(d){return partyColors[d.abbr];})
        .attr("d", function(d){return line(d.data);});


      var marker_groups = svg.selectAll(".marker-group")
        .data(parties);

      marker_groups.enter().append("g");

      marker_groups
        .classed({"marker-group":true});

      var markers = marker_groups.selectAll("circle")
        .data(function(d){return d.data.filter(function(x){return !isNaN(x[1]);})});

      markers.enter().append("circle");

      markers
        .classed({"marker":true})
        .attr("cx", line.x())
        .attr("cy", line.y())
        .attr('r', 4)
        .style('stroke', function(d){return partyColors[this.parentNode.__data__.abbr];});

      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis);

    });
  }
  return chart;
}
