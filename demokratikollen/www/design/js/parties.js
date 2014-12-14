parties = {
  mapChart: function(regions) {
    var width = 130,
        height = 2.53846153846*width,
        color = "steelblue";

    var projection = d3.geo.conicEqualArea()
        .parallels([50,70])
        .center([16.6358,62.1792]);

    var path = d3.geo.path();

    function prop(name) {
      return function(d) { return d[name]; };
    }

    var regMap = d3.map(regions.features, prop("id"));

    function chart(selection) {
      selection.each(function(data, i) {
        var max_votes = data.max_municipality;
        var svg = d3.select(this).selectAll("svg").data([data.municipalities]);

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
            .data(data.municipalities, prop("id"));

        var startColor = d3.rgb('#eee'),
            endColor = d3.rgb(color);
        var colorScale = d3.scale.linear()
            .domain([0,max_votes])
            .range([startColor, endColor]);

        var tooltip = d3.select("body")
            .append("div")
            .attr('class', 'election-tooltip')
            .style("opacity", 0);

        var tooltipText = tooltip.append("div");

        var tooltipFigure = tooltip.append("figure")
        // var tooltipFigure = d3.select("#municipality-timeseries")
          .style("display","block")
          .style("padding-top","5px");

        // Setup tooltip events
        regs.on("mouseover", function(d){
              pColor = colorScale(0.5*max_votes);
              tooltipText.html("<strong>"+regMap.get(d.id).properties.name+":</strong> "
                              +"<span style='color:"+pColor+"'>" + d3.format('.1f')(100*d.votes) + "</span> % "+parties.year);
              d3.json("/data/elections/timeseries/"+parties.party+"/"+d.id+".json",function(error,mTsJson){
                timeSeriesChart = parties.timeSeriesChart()
                  .lineColor(pColor);
                tooltipFigure.datum(mTsJson.d).call(timeSeriesChart);
              });
              tooltip.transition()
                .duration(100)
                .style("opacity",0.8);
            })
            .on("mousemove", function(d){
              tooltip.style("top", (event.pageY-110)+"px").style("left",(event.pageX+3)+"px");
            })
            .on("mouseout", function(d){
              tooltip.transition()
                .duration(100)
                .style("opacity",0);;
            });

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

    chart.color = function(_) {
      if (!arguments.length) return color;
      color = _;
      return chart;
    };

    return chart;
  },
  timeSeriesChart: function() {
    var margin = {top: 7, right: 12, bottom: 17, left: 25},
        width = 170 - margin.left - margin.right,
        height = 60 - margin.top - margin.bottom
        lineColor = "steelblue";

    var x = d3.scale.linear()
      .range([0, width]);

    var y = d3.scale.linear()
      .range([height, 0]);

    var line = d3.svg.line()
      .x(function(d) { return x(d.year); })
      .y(function(d) { return y(d.votes); });

    var xAxis = d3.svg.axis()
        .scale(x)
        .tickFormat(d3.format(".0f"))
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .tickFormat(function(d) {
          if(d>=0.1) {
            return d3.format(".0f")(100*d);
          } else {
            return d3.format(".1f")(100*d).replace('.',',');
          }
        })
        .orient("left");

    function chart(selection) {
      selection.each(function(data,i) {
        data.forEach(function(d) {
          d.year = parseInt(d.year);
          d.votes = +d.votes;
        });
        console.log(data);
        var svg = d3.select(this)
          .selectAll("svg")
          .data([data]);

        svg.enter().append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom);
        svg = svg.selectAll("g")
          .data([data]);

        var years = d3.extent(data, function(d) { return d.year; });
        x.domain(years);

        years.splice(1,0,d3.median(data,function(d) { return d.year; }));
        xAxis.tickValues(years);

        var votes = d3.extent(data, function(d) { return d.votes; });
        yAxis.tickValues(votes);
        y.domain(votes);

        var gEnter = svg.enter()
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        gEnter.append("path")
            .attr("class", "line")
            .style("fill", "none")
            .style("stroke",lineColor)
            .style("stroke-width", "1.5px");

        gEnter.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")");

        gEnter.append("g")
            .attr("class", "y axis")
            .append("text")
            .attr("class","label");

        svg.selectAll("g.y.axis")
            .call(yAxis)
          .selectAll("text.label")
            // .attr("transform", "rotate(-90)")
            .attr("x", 1)
            // .attr("y", height/2)
            .attr("dx", ".71em")
            .style("text-anchor", "start")
            .style("alignment-baseline","middle")
            .text("%");

        svg.selectAll("g.x.axis")
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

    chart.lineColor = function(_) {
      if (!arguments.length) return lineColor;
      lineColor = _;
      return chart;
    };

    return chart;

  },
  setup: function(divId,data,party,year) {
    parties.party = party;
    parties.year = year;
    d3.json('/data/municipalities.topojson', function (error,json) {
      var municipalities = topojson.feature(json, json.objects.municipalities);
      var mapChart = parties.mapChart(municipalities)
            .width(150)
            .color(utils.parties.get(party).color);
      var chartDiv = d3.select(divId);

      // Create and call update function
      parties.updateMap = function(d) {
        chartDiv.datum(d)
                .call(mapChart)
      }

      parties.updateMap(data);
    });
  }
};