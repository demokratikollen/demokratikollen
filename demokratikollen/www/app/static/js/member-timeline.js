function AppointmentsTimeline(config) {
  ROLE_CLASSES = d3.map();
  ROLE_CLASSES.set("Ordförande", "chair");
  ROLE_CLASSES.set("Suppleant", "substitute");

  function prepData(data) {
    data.forEach(
      function(element, index, array) {
        element.start = new Date(element.start);
        element.end = new Date(element.end);
      });
      
    ordering = function(a, b) {
      //Sort by end date descending, then start date descending
      endDiff = b.end - a.end;
      if (endDiff) {
        return endDiff;
      } else {
        return b.start - a.start
      }
    }
    data.sort(ordering);

    data.minDate = d3.min(data, function (d) { return d.start; });
    data.maxDate = d3.max(data, function (d) { return d.end; });
  }

  function chart(selection) {
    selection.each(function(data) {
      prepData(data);

      var svg = d3.select(this);
      
      numAppointments = data.length;

      var height = numAppointments * config.lineHeight;
      svg.attr("viewBox", "0 0 940 " + height);

      var x = d3.time.scale()
        .domain([data.minDate, data.maxDate])
        .range([config.labelWidth, config.width])
        .nice(d3.time.year);

      var y = d3.scale.ordinal()
        .domain(d3.range(numAppointments))
        .rangePoints([0, height], 1);

      var yAxis = d3.svg.axis()
        .scale(y)
        .tickFormat(function(d, i) { return data[i].name; })
        .orient("right");

      var line = d3.svg.line()
        .x(function(d) { return x(d[0]); })
        .y(function(d) { return y(d[1]); });

      data.forEach(function (el, i, arr) {
        lineData = [[el.start, i], [el.end, i]];
        path = svg.append("path")
          .attr("class", "line appointment")
          .attr("d", line(lineData));
        ROLE_CLASSES.forEach(function(role, css) {
          if (el.role == role) { path.classed(css, true); }
        });
      });

      svg.append("g")
          .call(yAxis);

    });
  }
  return chart;
}
