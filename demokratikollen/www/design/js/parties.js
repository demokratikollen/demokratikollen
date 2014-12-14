demokratikollen.graphics.mapChart = function(regions) {
  var width = 130,
      height = 2.53846153846*width,
      color = "steelblue";

  var tooltipTextHtml,
      tooltipFigureDataUrl,
      tooltipChart = demokratikollen.graphics.timeSeriesChart();

  var projection = d3.geo.conicEqualArea()
      .parallels([50,70])
      .center([16.6358,62.1792]);

  var path = d3.geo.path();

  var startColor = d3.rgb('#eee'),
      endColor = d3.rgb(color);

  var colorScale = d3.scale.linear()
      .domain([0,1])
      .range([startColor, endColor]);

  function prop(name) {
    return function(d) { return d[name]; };
  }

  function chart(selection) {
    selection.each(function(data, i) {
      var svg = d3.select(this).selectAll("svg").data([data]);

      // Update projection and path
      projection.scale(10*width)
          .translate([width / 2, height / 2]);
      path.projection(projection);
      var transform = 'rotate(10,'+width/2+','+height/2+')';

      // If it doesn't exist, create the map
      var gMain = svg.enter().append("svg").append("g");
      var sel = gMain.attr("class","map-collection")
          .attr('transform',transform)
          .selectAll(".map-region")
          .data(regions.features, prop("id"))
          .enter()
          .append("path")
          .attr("class","map-region")
          .attr("d", path);

      var regs = svg.attr("width", width)
          .attr("height", height)
          .selectAll(".map-region")
          .data(data, prop("id"));

      var cScaleDomain = colorScale.domain();
      var cScaleAvg = cScaleDomain.reduce(function(a,b) { return a+b; })/cScaleDomain.length;
      var emphColor = colorScale(cScaleAvg);

      // Setup tooltip events
      if(tooltipTextHtml) {
        var tooltipOffsetY = 40;
        var ttHeight;
        var tooltip = d3.select("body")
            .append("div")
            .attr('class', 'election-tooltip')
            .style("opacity", 0);

        var tooltipText = tooltip.append("div");

        if(tooltipFigureDataUrl) {
          if(tooltipChart.margin != undefined) {
            tooltipOffsetY += tooltipChart.margin().top + tooltipChart.margin().bottom;
          }
          tooltipOffsetY += tooltipChart.height();
          var tooltipFigure = tooltip.append("figure")
          // var tooltipFigure = d3.select("#municipality-timeseries")
            .style("display","block");

          tooltipOffsetY += 7;
        }

        regs.on("mouseover", function(d){
          tooltipText.html(tooltipTextHtml(d))
            .select("span.votes")
            .style("color",emphColor);

          if(tooltipFigureDataUrl) {
            d3.json(tooltipFigureDataUrl(d),function(error,mTsJson){
              tooltipFigure.datum(mTsJson.d).call(tooltipChart);
              ttHeight  = tooltip.node().getBoundingClientRect().height;
            });
          }

          tooltip.transition()
            .duration(100)
            .style("opacity",0.8);
        })
        .on("mousemove", function(d){
          if(ttHeight == undefined) ttHeight = tooltipOffsetY;
          tooltip.style("top", (event.pageY-ttHeight)+"px").style("left",(event.pageX)+"px");
        })
        .on("mouseout", function(d){
          tooltip.transition()
            .duration(100)
            .style("opacity",0);
        });
      }

      regs.attr("fill",startColor)
          .transition()
          .duration(200)
          .attr("fill",function(d) {
            return colorScale(d.votes);
          });

      regs.exit()
          .transition()
          .duration(200)
          .attr("fill","black");
    });
  }

  chart.projection = function(_) {
    if (!arguments.length) return projection;
    projection = _;
    return chart;
  };

  chart.tooltipTextHtml = function(_) {
    if (!arguments.length) return tooltipTextHtml;
    tooltipTextHtml = _;
    return chart;
  };

  chart.tooltipFigureDataUrl = function(_) {
    if (!arguments.length) return tooltipFigureDataUrl;
    tooltipFigureDataUrl = _;
    return chart;
  };

  chart.tooltipChart = function(_) {
    if (!arguments.length) return tooltipChart;
    tooltipChart = _;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    height = 2.53846153846*_;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    width = _/2.53846153846;
    return chart;
  };

  chart.colorScale = function(_) {
    if (!arguments.length) return colorScale;
    colorScale = _;
    return chart;
  };

  return chart;
}

demokratikollen.graphics.timeSeriesChart = function() {
  var margin = {top: 7, right: 12, bottom: 17, left: 25},
      width = 170 - margin.left - margin.right,
      height = 60 - margin.top - margin.bottom,
      lineColor = "steelblue";

  var xScale = d3.scale.linear()
    .range([0, width]);

  var yScale = d3.scale.linear()
    .range([height, 0]);

  var line = d3.svg.line()
    .x(function(d) { return xScale(d.x); })
    .y(function(d) { return yScale(d.y); });

  var xAxis = d3.svg.axis()
      .scale(xScale)
      .orient("bottom");

  var yAxis = d3.svg.axis()
      .scale(yScale)
      .orient("left");

  function chart(selection) {
    selection.each(function(data,i) {
      var svg = d3.select(this)
        .selectAll("svg")
        .data([data]);

      svg.enter().append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);
      svg = svg.selectAll("g")
        .data([data]);

      var gEnter = svg.enter()
          .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      gEnter.append("path")
          .attr("class", "line")
          .style("fill", "none")
          .style("stroke",lineColor)
          .style("stroke-width", "1.5px");

      gEnter.append("g")
          .attr("class", "x axis");

      gEnter.append("g")
          .attr("class", "y axis")
          .append("text")
          .attr("class","label");

      svg.selectAll("g.y.axis")
          .call(yAxis)
        .selectAll("text.label")
          .attr("x", 1)
          .attr("dx", ".71em")
          .style("text-anchor", "start")
          .style("alignment-baseline","middle")
          .text("%");

      svg.selectAll("g.x.axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);
       
      svg.selectAll("path.line")
          .data([data])
          .attr("d", line);

    });
  }

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin = _;
    return chart;
  };

  chart.line = function(_) {
    if (!arguments.length) return line;
    line = _;
    return chart;
  };  

  chart.xAxis = function(_) {
    if (!arguments.length) return xAxis;
    xAxis = _;
    return chart;
  }; 

  chart.yAxis = function(_) {
    if (!arguments.length) return yAxis;
    yAxis = _;
    return chart;
  }; 

  chart.xScale = function(_) {
    if (!arguments.length) return xScale;
    xScale = _;
    return chart;
  }; 

  chart.yScale = function(_) {
    if (!arguments.length) return yScale;
    yScale = _;
    return chart;
  }; 

  chart.lineColor = function(_) {
    if (!arguments.length) return lineColor;
    lineColor = _;
    return chart;
  };

  return chart;
}



parties = {
  tooltipFigure: function() {
    var margin = {top: 12, right: 12, bottom: 17, left: 25},
        width = 170 - margin.left - margin.right,
        height = 60 - margin.top - margin.bottom

    var timeSeriesChart = demokratikollen.graphics.timeSeriesChart()
      .lineColor(parties.pColorMild)
      .width(width)
      .height(height)
      .margin(margin);

    var xScale = timeSeriesChart.xScale().range([0, width]),
        yScale = timeSeriesChart.yScale().range([height, 0]),
        xAxis = timeSeriesChart.xAxis(),
        yAxis = timeSeriesChart.yAxis();

    var line = d3.svg.line()
      .x(function(d) { return xScale(d.year); })
      .y(function(d) { return yScale(d.votes); });

    timeSeriesChart.line(line);

    function chart(selection) {
      selection.each(function(data,i) {
        data.forEach(function(d) {
          d.year = parseInt(d.year);
          d.votes = +d.votes;
        });

        var years = d3.extent(data, function(d) { return d.year; });
        xScale.domain(years);

        var votes = d3.extent(data, function(d) { return d.votes; });
        yScale.domain(votes);

        years.splice(1,0,d3.median(data,function(d) { return d.year; }));
        xAxis.tickValues(years);
        yAxis.tickValues(votes);

        yAxis.tickFormat(function(d) {
            if(d>=0.1) {
              return d3.format(".0f")(100*d);
            } else {
              return d3.format(".1f")(100*d).replace('.',',');
            }
          });

        xAxis.tickFormat(d3.format(".0f"));
      });

      timeSeriesChart(selection);
    }

    chart.width = function(_) {
      if (!arguments.length) return width;
      width = _;
      return chart;
    };

    chart.height = function(_) {
      if (!arguments.length) return height;
      height = _;
      return chart;
    };

    chart.margin = function(_) {
      if (!arguments.length) return margin;
      margin = _;
      return chart;
    };
    
    return chart;
  },
  setup: function(divId,data,party,year) {
    parties.party = party;
    parties.year = year;
    parties.pColor = utils.parties.get(party).color;
    parties.pColorMild = d3.interpolateRgb(d3.rgb('#eee'), parties.pColor)(0.5);

    var startColor = d3.rgb('#eee'),
        endColor = d3.rgb(parties.pColor);

    var maxVotes = data.max_municipality;

    var colorScale = d3.scale.linear()
      .domain([0,maxVotes])
      .range([startColor, endColor]);

    d3.json('/data/municipalities.topojson', function (error,json) {
      var municipalities = topojson.feature(json, json.objects.municipalities);
      var regMap = d3.map(municipalities.features, function(d) { return d.id; });
      var mapChart = demokratikollen.graphics.mapChart(municipalities)
            .width(150)
            .tooltipTextHtml(function(d) {
              return "<strong>"+regMap.get(d.id).properties.name+":</strong> "
                            +"<span class='votes'>" + d3.format('.1f')(100*d.votes) + "</span> % "+year;
            })
            .tooltipFigureDataUrl(function(d) { return "/data/elections/timeseries/"+party+"/"+d.id+".json"; })
            .tooltipChart(parties.tooltipFigure())
            .colorScale(colorScale);

      var chartDiv = d3.select(divId);

      // Create and call update function
      parties.updateMap = function(d) {
        chartDiv.datum(d.municipalities)
                .call(mapChart)
      }

      parties.updateMap(data);
    });
  }
};