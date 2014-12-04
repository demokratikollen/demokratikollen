function AppointmentsTimeline(config) {
  function chart(selection) {
    selection.each(function(data) {
      console.log(this)

      var line = d3.svg.line()

      numAppointments = data.length

      d3.select(this)
        .attr("height", 2 * config.fontSize * numAppointments)

      d3.select(this)
        .append("g")
        .append("path")
        .attr("d", line(data))
        .attr("style", "fill:none;stroke:#000;")

    });
  }
  return chart;
}
