/*global demokratikollen, d3, prop */

demokratikollen.graphics.PartyHistory = function () {

  var width = 400,
    height = 350,
    svgMargin = {top: 20, left: 50, right: 20, bottom: 20},
    timeUnit = d3.time.year,
    xTickLabelWidth = 100,
    markerSize = 4,
    cssClass = "party-history";

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

      var xDomain = [d3.min(data.terms, prop('start')), d3.max(data.terms, prop('end'))],
        yDomain = [0, d3.max(data.terms.concat(data.polls), prop('value'))];

      var xScale = d3.time.scale()
        .domain(xDomain)
        .range([0, plotAreaWidth])
        .nice(timeUnit);

      var yScale = d3.scale.linear()
        .domain(yDomain)
        .range([plotAreaHeight, 0])
        .nice();


      //Clipping path with rectangles representing terms.
      var termsClipId = demokratikollen.utils.uniqueId("terms");
      var termsClipPath = plotArea.append("clipPath").attr("id", termsClipId);

      var pollPath = d3.svg.line()
        .x(function (d) { return xScale(d.time); })
        .y(function (d) { return yScale(d.value); });

      function draw() {
        termsClipPath.selectAll("rect.term")
          .data(data.terms)
          .enter()
          .append("rect")
          .classed("term", true)
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
          .attr("clip-path", 'url(#' + termsClipId + ')')
          .attr("y", 0)
          .attr("x", function (d) { return xScale(d.start); })
          .attr("width", function (d) { return xScale(d.end) - xScale(d.start); })
          .attr("height", plotAreaHeight)
          .classed("even", function (d, i) { return i % 2 === 0; })
          .classed("odd", function (d, i) { return i % 2 !== 0; });
        /*jslint unparam: false*/

        partyLeaderRects.classed("selected", prop("selected"));

        var termLines = plotArea.selectAll("line.term")
          .data(data.terms);

        termLines.enter()
          .append("line")
          .classed("term", true)
          .attr("x1", function (d) { return xScale(d.start); })
          .attr("x2", function (d) { return xScale(d.end); })
          .attr("y1", function (d) { return yScale(d.value); })
          .attr("y2", function (d) { return yScale(d.value); });

        termLines.classed("selected", prop("selected"));

        plotArea.selectAll("path.poll")
          .data([data.polls])
          .enter()
          .append("path")
          .classed("poll", true)
          .attr("d", pollPath);

        var pollMarkers = plotArea.selectAll("circle.poll")
          .data(data.polls);

        pollMarkers.enter()
          .append("circle")
          .classed("poll", true)
          .attr("cx", function (d) { return xScale(d.time); })
          .attr("cy", function (d) { return yScale(d.value); })
          .attr('r', markerSize);

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
        .tickFormat(yScale.tickFormat(",.1%"))
        .orient("left");

      svg.append("g")
        .classed("axis x", true)
        .attr("transform", "translate(0," + plotAreaHeight + ")")
        .call(xAxis);

      svg.append("g")
        .classed("axis y", true)
        .call(yAxis);

      var select = (function () {
        var items = ['partyLeader', 'term', 'poll'],
          currentSelection = null;

        var itemFinders = {
          partyLeader: function (t) {
            return data.partyLeaders.filter(function (d) { return d.start <= t && t <= d.end; })[0];
          },
          term: function (t) {
            return data.terms.filter(function (d) { return d.start <= t && t <= d.end; })[0];
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
              return ('Partiledare ' + yearMonthFormat(d.start) + ' – ' + yearMonthFormat(d.end) +
                ': ' + d.name);
            }
            return 'Partiledare: okänd';

          },
          term: function (d) {
            if (d) {
              return ('Mandat ' + yearFormat(d.start) + ' – ' + yearFormat(d.end) +
                  ': ' + percentFormat(d.value));
            }
            return 'Mandat: okänt';
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

        function updateSelection(t) {
          var changed = false,
            oldSelection = currentSelection;

          data.selection = {t: t};

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

      select(new Date());

      /*jslint unparam: true*/
      var picker = demokratikollen.graphics.PickerCross()
        .onMouseMove(function (x, y) { select(xScale.invert(x)); })
        .onMouseOut(function (x, y) { select(new Date()); });
      /*jslint unparam: false*/

      var interactiveArea = plotArea.append("g");
      interactiveArea.append("rect")
        .attr("width", width)
        .attr("height", height)
        .style("fill", 'transparent');

      picker(interactiveArea);

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

  return chart;
};