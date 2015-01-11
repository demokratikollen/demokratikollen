demokratikollen.graphics.PartyHistory = function() {

  var width = 400,
    height = 350,
    svgMargin = {top: 20, left: 50, right: 20, bottom: 20},
    timeUnit = d3.time.year,
    xTickLabelWidth = 100,
    markerSize = 4,
    cssClass = "party-history";

  function unique(arr) {
    return arr.reduce(function(collected, current) {
      if (collected.indexOf(current) < 0) collected.push(current);
      return collected;
    }, []);
  }

  function chart(selection) {
    selection.each(function(data) {
      var utils = demokratikollen.utils;

      var container = d3.select(this)
        .append('div')
        .classed(cssClass, true)
        .style("width", width)
        .style("height", height);

      var info = container.append("div")
        .classed("info", true);

      var legend = container.append("div")
        .classed("legend", true);

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
      plotArea.append("clipPath")
        .attr("id", termsClipId)
        .selectAll("rect.term")
        .data(data.terms)
        .enter()
        .append("rect")
        .classed("term", true)
        .attr("y", function (d) { return yScale(d.value); })
        .attr("x", function (d) { return xScale(d.start); })
        .attr("width", function (d) { return xScale(d.end) - xScale(d.start); })
        .attr("height", function (d) { return yScale(0) - yScale(d.value); });

      plotArea.selectAll("rect.party-leader")
        .data(data.partyLeaders)
        .enter()
        .append("rect")
        .classed("party-leader", true)
        .attr("clip-path", 'url(#' + termsClipId + ')')        
        .attr("y", 0)
        .attr("x", function (d) { return xScale(d.start); })
        .attr("width", function (d) { return xScale(d.end) - xScale(d.start); })
        .attr("height", plotAreaHeight)
        .classed("even", function (d, i) { return i % 2 == 0; })
        .classed("odd", function (d, i) { return i % 2 != 0; });


      plotArea.append("g")
        .selectAll("line.term")
        .data(data.terms)
        .enter()
        .append("line")
        .classed("term", true)
        .attr("x1", function (d) { return xScale(d.start); })
        .attr("x2", function (d) { return xScale(d.end); })
        .attr("y1", function (d) { return yScale(d.value); })
        .attr("y2", function (d) { return yScale(d.value); });


      pollPath = d3.svg.line()
        .x(function (d) { return xScale(d.time); })
        .y(function (d) { return yScale(d.value); });

      plotArea.append("path")
        .classed("poll", true)
        .attr("d", pollPath(data.polls));

      plotArea.selectAll("circle.poll")
        .data(data.polls)
        .enter()
        .append("circle")
        .classed("poll", true)
        .attr("cx", function(d) { return xScale(d.time); })
        .attr("cy", function(d) { return yScale(d.value); })
        .attr('r', markerSize);



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




  // Interactivity part
    /*
      function makeVerticalLine(cssClass, x, y) {
        cssClasses = ["interactive"].concat(cssClass)
        selector = "." + cssClasses.join(".");
        s = svg.selectAll(selector)
            .data([0])
          
          s.enter()
            .append("line")
            .classed(cssClasses.join(" "), true)
            .style("pointer-events", "none");
            
          s.attr("x1", x)
            .attr("x2", x)
            .attr("y1", 0)
            .attr("y2", height);
      }

      function findPartyLeader(t) {
        result = partyLeaderData.filter(function (d) { return d.start <= t && t <= d.end; })[0];
        return "Partiledare: " + (result ? result.name : "okänd");
      }

      function findElectionDatum(t) {
        result = electionData.filter(function (d) { return d.start <= t && t <= d.end; })[0];
        return "Antal mandat: " + (result ? result.value : "okänt");
      }

      function findPollDatum(t) {
        result = pollData.filter(function (d) { return d.time <= t; });
        result = result[result.length - 1]
        return "Senaste opinionsundersökning: " + (result ? (result.value * 100 + "% (" + result.time + ")") : "okänt");
      }

      var config = {
        xMin: 0,
        xMax: width,
        yMin: 0,
        yMax: height,
        hover: function (x, y) {
          makeVerticalLine("hover", x, y);
        },
        leave: function () {
          s = svg.selectAll(".interactive.hover")
            .remove();
        },
        click: function (x, y) {
          makeVerticalLine("fixed", x, y);
          t = timeScale.invert(x);

          infoParagraphs
            .data([findPartyLeader(t), findElectionDatum(t), findPollDatum(t)])
            .html(function (d) { return d; });
        }
      };


      interactiveArea = svg.append("rect")
        .classed("interactive", true)
        .attr("width", width)
        .attr("height", height)
        .style("fill", "transparent");

      function onMouseMove() {
        var eventData = d3.mouse(this),
          x = eventData[0],
          y = eventData[1];
          config.hover(x, y);
      }

      function onMouseOut() {
          config.leave();
      }

      function onClick() {
        var eventData = d3.mouse(this),
          x = eventData[0],
          y = eventData[1];
          config.click(x, y);
      }

      interactiveArea.on("mousemove.interactive", onMouseMove);
      interactiveArea.on("mouseout.interactive", onMouseOut);
      interactiveArea.on("mouseup.interactive", onClick);*/
    } );
  }

  chart.timeUnit = function(value) {
    if (!arguments.length) return timeUnit;
    timeUnit = value;
    return chart;
  };

  chart.xTickLabelWidth = function(value) {
    if (!arguments.length) return xTickLabelWidth;
    xTickLabelWidth = value;
    return chart;
  };

  chart.width = function(value) {
    if (!arguments.length) return width;
    width = value;
    return chart;
  }

  chart.height = function(value) {
    if (!arguments.length) return height;
    height = value;
    return chart;
  }

  chart.svgMargin = function(value) {
    if (!arguments.length) return svgMargin;
    svgMargin = value;
    return chart;
  }

  chart.cssClass = function(value) {
    if (!arguments.length) return cssClass;
    cssClass = value;
    return chart;
  }

  return chart;
};