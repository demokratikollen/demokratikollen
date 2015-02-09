/*global demokratikollen, d3, window */

demokratikollen.graphics.AppointmentsTimeline = function () {

  var rowHeight = 40,
    lineOffsetY = 10,
    margin = { top: 20, right: 20, bottom: 5, left: 10 },
    rowLabelsMarginLeft = 10,
    timeUnit = d3.time.year,
    tickLabelWidth = 100,
    tipHtml = null,
    markerSize = 4,
    cssClass = "timeline",
    hoverLinesWidth = rowHeight - 15;

  function getMinDate(blocks) {
    return d3.min(blocks, function (block) { return block.startDate; });
  }

  function getMaxDate(blocks) {
    return d3.max(blocks, function (block) { return block.endDate; });
  }

  function ordering(rowA, rowB) {
    // rowA and rowB are arrays of data entries
    var maxDates = [getMaxDate(rowA.values), getMaxDate(rowB.values)];
    if (maxDates[0] !== maxDates[1]) {
      return maxDates[1] - maxDates[0];
    }
    return getMinDate(rowB.values) - getMinDate(rowA.values);

  }

  function unique(arr) {
    return arr.reduce(function (collected, current) {
      if (collected.indexOf(current) < 0) {
        collected.push(current);
      }
      return collected;
    }, []);
  }

  function chart(selection) {
    selection.each(function (data) {

      var dataByRowLabel = d3.nest()
        .key(function (d) { return d.rowLabel; })
        .entries(data);
      dataByRowLabel.sort(ordering);


      var rowLabels = dataByRowLabel.map(function (d) { return d.key; }),
        minDate = getMinDate(data),
        maxDate = getMaxDate(data);

      var width = demokratikollen.utils.getInnerWidth(d3.select(this)) - margin.left - margin.right,
        height = rowLabels.length * rowHeight;

      var container = d3.select(this);
      var svg = container
        .append("svg")
        .classed(cssClass, true)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var x = d3.time.scale()
        .domain([minDate, maxDate])
        .range([0, width])
        .nice(timeUnit);

      var y = d3.scale.ordinal()
        .domain(rowLabels)
        .rangePoints([0, height], 1);

      var tickValues = x.ticks(Math.floor(width / tickLabelWidth));
      tickValues = unique(tickValues.map(timeUnit.floor));

      var xAxis = d3.svg.axis()
        .scale(x)
        .orient("top")
        .tickSize(-height, 0)
        .tickValues(tickValues);

      xAxis = svg.append("g")
        .classed("axis x", true)
        .call(xAxis);

      svg.append("g")
        .classed("rowLabels", true)
        .selectAll("rowLabels")
        .data(rowLabels)
        .enter()
        .append("text")
        .text(function (d) { return d; })
        .attr("transform", function (d) { return "translate(" + rowLabelsMarginLeft + "," + y(d) + ")"; });

      var line = d3.svg.line()
        .x(function (d) { return x(d[0]); })
        .y(function (d) { return y(d[1]); });

      var linesSelection = svg.append("g")
        .attr("transform", "translate(0," + lineOffsetY + ")")
        .classed("lines", true)
        .selectAll("lines")
        .data(data)
        .enter();

      linesSelection.append("path")
        .attr("d", function (d) {
          return line([[d.startDate, d.rowLabel], [d.endDate, d.rowLabel]]);
        })
        .attr("class", function (d) { return d.cssClass || ""; });

      linesSelection.append("circle")
        .attr("cx", function (d) { return x(d.startDate); })
        .attr("cy", function (d) { return y(d.rowLabel); })
        .attr('r', markerSize);

      linesSelection.append("circle")
        .attr("cx", function (d) { return x(d.endDate); })
        .attr("cy", function (d) { return y(d.rowLabel); })
        .attr('r', markerSize);


      if (tipHtml) {
        var tooltip = d3.select("body")
          .append("div")
          .classed(cssClass + " tooltip", true)
          .style("display", "none")
          .style("position", "absolute")
          .style("max-width", width + "px");

        var setPosTooltip = function (x, y) {
          tooltip.style("left", x + "px")
            .style("top", y + "px");
        };

        var hideTooltip = function () {
          tooltip.style("display", "none");
        };

        var showTooltip = function (d) {
          tooltip.style("display", "block");
          tooltip.html(tipHtml(d));
          setPosTooltip(0, 0);

          var mouseEvent = d3.mouse(d3.select("body")[0][0]),
            anchorX = mouseEvent[0],
            anchorY = mouseEvent[1],
            tooltipBCR = tooltip[0][0].getBoundingClientRect(),
            tooltipWidth = tooltipBCR.right - tooltipBCR.left,
            plotAreaBCR = container[0][0].getBoundingClientRect(),
            edge = {
              left: window.pageXOffset + plotAreaBCR.left + margin.left,
              right: window.pageXOffset + plotAreaBCR.left + margin.left + width
            };

          if (anchorX + tooltipWidth / 2 > edge.right) {
            anchorX = edge.right - tooltipWidth / 2;
          } else if (anchorX - tooltipWidth / 2 < edge.left) {
            anchorX = edge.left + tooltipWidth / 2;
          }

          setPosTooltip(anchorX - tooltipWidth / 2, anchorY + rowHeight / 2);
        };



        linesSelection.append("path")
          .style("stroke", "rgba(0,0,0,0)")
          .style("stroke-width", hoverLinesWidth)
          .attr("d", function (d) { return line([[d.startDate, d.rowLabel], [d.endDate, d.rowLabel]]); })
          .on('mouseover', showTooltip)
          .on('mouseout', function (d) { hideTooltip(); });
      }
    });
  }

  chart.tipHtml = function (value) {
    if (!arguments.length) {
      return tipHtml;
    }
    tipHtml = value;
    return chart;
  };

  chart.timeUnit = function (value) {
    if (!arguments.length) {
      return timeUnit;
    }
    timeUnit = value;
    return chart;
  };

  chart.tickLabelWidth = function (value) {
    if (!arguments.length) {
      return tickLabelWidth;
    }
    tickLabelWidth = value;
    return chart;
  };

  return chart;
};