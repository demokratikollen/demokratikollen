function AppointmentsTimeline(config) {
  ROLE_CLASSES = d3.map();
  ROLE_CLASSES.set("Ordförande", "chair");
  ROLE_CLASSES.set("Suppleant", "substitute");

  function getMinDate(appointments) { 
    return d3.min(appointments, function (a) { return a.start; });
  }

  function getMaxDate(appointments) { 
    return d3.max(appointments, function (a) { return a.end; });
  }

  function prepData(data) {
    // Transform date strings to Date objects
    data.forEach(
      function(element, index, array) {
        element.start = new Date(element.start);
        element.end = new Date(element.end);
      });
  }

  function orderedNames(appointments) {
    // Make a nested list by appointment name, with overall 
    // start and end dates for the appointments in each group
    datesByName = d3.nest()
      .key(function(a) { return a.name; })
      .rollup(function(a) {
        return { minDate: getMinDate(a), maxDate: getMaxDate(a) };
      })
      .entries(appointments)
      
    ordering = function(a, b) {
      //Sort by end date descending, then start date descending
      endDiff = b.values.maxDate - a.values.maxDate;
      if (endDiff) {
        return endDiff;
      } else {
        return b.values.minDate - a.values.minDate
      }
    }
    datesByName.sort(ordering);

    return datesByName.map(function(d) { return d.key; });
  }

  function chart(selection) {
    selection.each(function(data) {
      prepData(data);

      var svg = d3.select(this);
      
      numAppointments = data.length;

      var height = (
        config.marginTop +
        numAppointments * config.lineHeight + 
        config.marginBottom);

      svg.attr("viewBox", "0 0 940 " + height);

      var x = d3.time.scale()
        .domain([getMinDate(data), getMaxDate(data)])
        .range([config.labelWidth, config.width])
        .nice(d3.time.year);

      var y = d3.scale.ordinal()
        .domain(orderedNames(data))
        .rangePoints([config.marginTop, height-config.marginBottom], 1);

      var yAxis = d3.svg.axis()
        .scale(y)
        .orient("right");

      var xAxis = d3.svg.axis()
        .scale(x)
        .orient("top");

      var line = d3.svg.line()
        .x(function(d) { return x(d[0]); })
        .y(function(d) { return y(d[1]); });

      data.forEach(function (el, i, arr) {
        lineData = [[el.start, el.name], [el.end, el.name]];
        path = svg.append("path")
          .attr("class", "line appointment")
          .attr("d", line(lineData));
        ROLE_CLASSES.forEach(function(role, css) {
          if (el.role == role) { path.classed(css, true); }
        });
      });

      svg.append("g")
        .classed("axis x", true)
        .call(xAxis);
      
      svg.append("g")
        .classed("axis y", true)
        .call(yAxis);

      console.log(this.width)

    });
  }
  return chart;
}