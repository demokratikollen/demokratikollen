demokratikollen.graphics.PickerCross = function() {

  var utils = demokratikollen.utils;

  var margin = { top: 0, left: 0, bottom: 0, right: 0 },
    cssClass = 'picker-cross',
    onMouseMove = function () {};

  function chart(selection) {
    selection.each(function() { // not using data of selection, only the selected object

      var container = d3.select(this),
        pickerId = demokratikollen.utils.uniqueId(cssClass),
        verticalLineId = pickerId + '-vertical',
        horizontalLineId = pickerId + '-horizontal',
        width = this.getBoundingClientRect().width - margin.left - margin.right,
        height = this.getBoundingClientRect().height - margin.top - margin.bottom;

      var cross = container
        .append('g')
        .classed(cssClass, true);

      function mark(x, y) {
          var verticalLine = cross.selectAll('.vertical')
            .data([x]);

          verticalLine.enter()
            .append("line")
            .style("pointer-events", "none")
            .classed('vertical', true);
            
          verticalLine.attr("x1", x)
            .attr("x2", x)
            .attr("y1", margin.bottom)
            .attr("y2", margin.bottom + height);


          var horizontalLine = cross.selectAll('.horizontal')
            .data([y]);

          horizontalLine.enter()
            .append("line")
            .style("pointer-events", "none")
            .classed('horizontal', true);
            
          horizontalLine.attr("x1", margin.left)
            .attr("x2", margin.left + width)
            .attr("y1", y)
            .attr("y2", y);
      }


      function onMouseOut() {
        mark(0, 0);
      }
/*
      function onClick() {
        var eventData = d3.mouse(this),
          x = eventData[0],
          y = eventData[1];
          config.click(x, y);
      }
*/
      container.on("mousemove." + pickerId, function () {
        var eventData = d3.mouse(this),
          x = eventData[0],
          y = eventData[1];
          mark(x, y);
          onMouseMove(x, y);
      });
      container.on("mouseout." + pickerId, onMouseOut);
      //container.on("mouseup." + pickerId, onClick);



/*

      

      })();


      var config = {
        xMin: 0,
        xMax: width,
        yMin: 0,
        yMax: height,
        hover: mark,
        leave: function () {
          mark(xScale(new Date()));
        },
        click: mark
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
      interactiveArea.on("mouseup.interactive", onClick);

      data.selection = {t: new Date(), texts: ["", "", ""]};

      draw();
*/
    } );
  }

  chart.margin = function(value) {
    if (!arguments.length) return magin;
    magin = value;
    return chart;
  }

  chart.cssClass = function(value) {
    if (!arguments.length) return cssClass;
    cssClass = value;
    return chart;
  }

  chart.onMouseMove = function(value) {
    if (!arguments.length) return onMouseMove;
    onMouseMove = value;
    return chart;
  }

  return chart;
};