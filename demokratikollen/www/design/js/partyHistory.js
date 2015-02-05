/*global demokratikollen, d3, prop */

demokratikollen.graphics.PartyHistory = function () {

  var width = 400,
    height = 350,
    svgMargin = {top: 20, left: 50, right: 20, bottom: 20},
    timeUnit = d3.time.year,
    xTickLabelWidth = 100,
    markerSize = 4,
    cssClass = "party-history",
    baseColor = "#555";

  function unique(arr) {
    return arr.reduce(function (collected, current) {
      if (collected.indexOf(current) < 0) { collected.push(current); }
      return collected;
    }, []);
  }

  function chart(selection) {
    selection.each(function (data) {

      var container = d3.select(this)
        .html("")
        .append('div')
        .classed(cssClass, true)
        .style("width", width)
        .style("height", height);

      var info = container.append("div")
        .classed("info", true)
        .style("margin-left", (svgMargin.left + 10) + 'px');


      var plotAreaWidth = width - svgMargin.left - svgMargin.right,
        plotAreaHeight = height - svgMargin.top - svgMargin.bottom;

      var svg = container.append("svg")
        .classed(cssClass, true)
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + svgMargin.left + "," + svgMargin.top + ")");

      var plotClipId = demokratikollen.utils.uniqueId("plot-area");
      svg.append('clipPath')
        .attr("id", plotClipId)
        .append('rect')
        .attr("width", plotAreaWidth)
        .attr("height", plotAreaHeight)
        .style("fill", "transparent");

      var plotArea = svg.append('g')
        .attr('clip-path', 'url(#' + plotClipId + ')');

      var xDomain = [d3.min(data.elections, prop('start')), new Date()], //d3.max(data.elections, prop('end'))],
        yDomain = [0, d3.max(data.elections.concat(data.polls), prop('value'))];

      var xScale = d3.time.scale()
        .domain(xDomain)
        .range([0, plotAreaWidth])
        .nice(timeUnit);

      var yScale = d3.scale.linear()
        .domain(yDomain)
        .range([plotAreaHeight, 0])
        .nice();


      //Clipping path with rectangles representing elections.
      var electionsClipId = demokratikollen.utils.uniqueId("elections");
      var electionsClipPath = plotArea.append("clipPath").attr("id", electionsClipId);

      var pollPath = d3.svg.line()
        .x(function (d) { return xScale(d.time); })
        .y(function (d) { return yScale(d.value); });

      function draw() {
        electionsClipPath.selectAll("rect.election")
          .data(data.elections)
          .enter()
          .append("rect")
          .classed("election", true)
          .attr("y", function (d) { return yScale(d.value); })
          .attr("x", function (d) { return xScale(d.start); })
          .attr("width", function (d) { return xScale(d.end) - xScale(d.start); })
          .attr("height", function (d) { return yScale(0) - yScale(d.value); });


        var partyLeaderRects = plotArea.selectAll("rect.party-leader")
          .data(data.partyLeaders);

        /*jslint unparam: true*/
        partyLeaderRects.enter()
          .append("rect")
          .classed("party-leader", true)
          .attr("clip-path", 'url(#' + electionsClipId + ')')
          .attr("y", 0)
          .attr("x", function (d) { return xScale(d.start); })
          .attr("width", function (d) { return xScale(d.end) - xScale(d.start); })
          .attr("height", plotAreaHeight)
          .style("fill-opacity", function (d, i) { return i % 2 !== 0 ? 0.25 : 0.35; });
        /*jslint unparam: false*/

        partyLeaderRects.classed("selected", prop("selected"))
          .style("fill", function (d) { return d.selected ? baseColor : baseColor.darker(2); });

        var electionLines = plotArea.selectAll("line.election")
          .data(data.elections);

        electionLines.enter()
          .append("line")
          .classed("election", true)
          .attr("x1", function (d) { return xScale(d.start); })
          .attr("x2", function (d) { return xScale(d.end); })
          .attr("y1", function (d) { return yScale(d.value); })
          .attr("y2", function (d) { return yScale(d.value); });

        electionLines.classed("selected", prop("selected"))
          .style("stroke", function (d) { return d.selected ? baseColor.darker(0.5) : baseColor.darker(1); });

        var pollColor = baseColor.darker(2);
        plotArea.selectAll("path.poll")
          .data([data.polls])
          .enter()
          .append("path")
          .classed("poll", true)
          .attr("d", pollPath)
          .style("stroke", pollColor)
          .style("fill", "none");

        var pollMarkers = plotArea.selectAll("circle.poll")
          .data(data.polls);

        pollMarkers.enter()
          .append("circle")
          .classed("poll", true)
          .attr("cx", function (d) { return xScale(d.time); })
          .attr("cy", function (d) { return yScale(d.value); })
          .attr('r', markerSize)
          .style("fill", pollColor)
          .style("stroke", pollColor);

        pollMarkers
          .classed("selected", prop('selected'));

        if (data.texts) {
          var paragraphs = info.selectAll("p").data(data.texts);
          paragraphs.enter().append("p");
          paragraphs.html(function (d) { return d; });
        }
      }

      // These two lines limit the number of time tick values and only keeps those that are
      // at timeUnit level or above (e.g. does not show months if timeUnit is year)
      var xTickValues = xScale.ticks(Math.floor(plotAreaWidth / xTickLabelWidth));
      xTickValues = unique(xTickValues.map(timeUnit.floor));

      var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .tickValues(xTickValues);

      var yAxis = d3.svg.axis()
        .scale(yScale)
        .tickFormat(d3.format(",.1%"))
        .orient("left");

      svg.append("g")
        .classed("axis x", true)
        .attr("transform", "translate(0," + plotAreaHeight + ")")
        .call(xAxis);

      svg.append("g")
        .classed("axis y", true)
        .call(yAxis);

      var select = (function () {
        var items = ['partyLeader', 'election', 'poll'],
          currentSelection = null;

        var itemFinders = {
          partyLeader: function (t) {
            return data.partyLeaders.filter(function (d) { return d.start <= t && t <= d.end; })[0];
          },
          election: function (t) {
            return data.elections.filter(function (d) { return d.start <= t && t <= d.end; })[0];
          },
          poll: function (t) {
            return data.polls.filter(function (d) { return d.time <= t; }).reverse()[0];
          }
        };
        itemFinders = items.map(function (item) { return itemFinders[item]; });

        var yearFormat = d3.time.format("%Y"),
          yearMonthFormat = d3.time.format("%Y-%m"),
          percentFormat = d3.format(",.1%");
        var textGenerators = {
          partyLeader: function (d) {
            if (d) {
              return ('Partiledare: ' + d.name + ' (' + yearMonthFormat(d.start) + ' – ' + yearMonthFormat(d.end) + ')');
            }
            return 'Partiledare: okänd';

          },
          election: function (d) {
            if (d) {
              return ('Valresultat ' + yearFormat(d.start) +
                  ': ' + percentFormat(d.value));
            }
            return 'Valresultat: okänt';
          },
          poll: function (d) {
            if (d) {
              return 'Opinion ' + yearMonthFormat(d.time) + ': ' + percentFormat(d.value);
            }
            return 'Opinion: okänd';
          }
        };
        textGenerators = items.map(function (item) { return textGenerators[item]; });

        function trySetSelected(value) {
          return function (d) { if (d) { d.selected = value; } };
        }

        function drawVerticalPicker(t) {
          var verticalLine = svg.selectAll('.vertical-picker')
            .data([xScale(t)]);

          verticalLine.enter()
            .append("line")
            .style("pointer-events", "none")
            .classed('vertical-picker', true);

          verticalLine.attr("x1", function (d) { return d; })
            .attr("x2", function (d) { return d; })
            .attr("y1", 0)
            .attr("y2", plotAreaHeight);
        }

        function updateSelection(t) {
          drawVerticalPicker(t);

          var changed = false,
            oldSelection = currentSelection;

          currentSelection = itemFinders.map(function (finder) { return finder(t); });

          if (oldSelection) {
            oldSelection.forEach(trySetSelected(false));
          } else {
            oldSelection = currentSelection.map(function () { return null; });
          }
          currentSelection.forEach(trySetSelected(true));
          d3.zip(currentSelection, oldSelection).forEach(function (pair) {
            var curr = pair[0], old = pair[1];
            changed = changed || (curr !== old);
          });
          if (changed) {
            data.texts = d3.zip(currentSelection, textGenerators).map(function (pair) {
              var curr = pair[0], tg = pair[1];
              return tg(curr);
            });
            draw();
          }
        }
        return updateSelection;
      }());

      var interactiveArea = svg.append("rect")
          .attr("width", plotAreaWidth)
          .attr("height", plotAreaHeight)
          .style("fill", 'transparent');

      var pickerId = demokratikollen.utils.uniqueId(cssClass);

      interactiveArea.on("mousemove." + pickerId, function () {
        var x = d3.mouse(this)[0];
        select(xScale.invert(x));
      });

      interactiveArea.on("mouseout." + pickerId, function () {
        select(new Date());
      });

      select(new Date());

    });
  }

  chart.timeUnit = function (value) {
    if (!arguments.length) { return timeUnit; }
    timeUnit = value;
    return chart;
  };

  chart.xTickLabelWidth = function (value) {
    if (!arguments.length) { return xTickLabelWidth; }
    xTickLabelWidth = value;
    return chart;
  };

  chart.width = function (value) {
    if (!arguments.length) { return width; }
    width = value;
    return chart;
  };

  chart.height = function (value) {
    if (!arguments.length) { return height; }
    height = value;
    return chart;
  };

  chart.svgMargin = function (value) {
    if (!arguments.length) { return svgMargin; }
    svgMargin = value;
    return chart;
  };

  chart.cssClass = function (value) {
    if (!arguments.length) { return cssClass; }
    cssClass = value;
    return chart;
  };

  chart.baseColor = function (value) {
    if (!arguments.length) { return baseColor; }
    baseColor = value;
    return chart;
  };

  return chart;
};