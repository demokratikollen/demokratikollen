parties = {
  mapChart: function(regions) {
    var width = 130,
        height = 2.53846153846*width;

    var projection = d3.geo.conicEqualArea()
        .parallels([50,70])
        .center([16.6358,62.1792])

    var path = d3.geo.path();

    function prop(name) {
      return function(d) { return d[name]; };
    }

    var regMap = d3.map(regions.features, prop("id"))

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
        var colorScale = d3.scale.linear().domain([0,max_votes]).range([startColor, endColor]);

        var tooltip = d3.select("body")
            .append("div")
            .attr('class', 'election-tooltip')
            .style("opacity", 0);

        var tooltipText = tooltip.append("div");

        // var tooltipFigure = tooltip.append("figure")
        var tooltipFigure = d3.select("#municipality-timeseries")
          .style("display","block")
          .style("padding-top","5px");

        // Setup tooltip events
        regs.on("mouseover", function(d){
              tooltipText.html("<strong>"+regMap.get(d.id).properties.name+":</strong> "
                              +"<span style='color:"+colorScale(0.5*max_votes)+"'>" + Math.round(100*d.votes) + "</span> %");
              d3.json("/data/elections/timeseries/"+"m"+"/"+d.id+".json",function(error,mTsJson){
                tooltipFigure.datum(mTsJson.d).call(parties.timeSeriesChart());
              });
              tooltip.transition()
                .duration(100)
                .style("opacity",0.9);
            })
            .on("mousemove", function(d){
              tooltip.style("top", (event.pageY-40)+"px").style("left",(event.pageX)+"px");
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
    var margin = {top: 5, right: 5, bottom: 3, left: 5},
        width = 80 - margin.left - margin.right,
        height = 40 - margin.top - margin.bottom;

    var x = d3.time.scale()
      .range([0, width]);

    var y = d3.scale.linear()
      .range([height, 0]);

    var line = d3.svg.line()
      .x(function(d) { return x(d.year); })
      .y(function(d) { return y(d.votes); });

    function chart(selection) {
      selection.each(function(data,i) {
        var svg = d3.select(this)
          .selectAll("svg")
          .data([data]);

        svg.enter().append("svg");
        svg = svg.selectAll("g")
          .data([data]);

        x.domain(d3.extent(data, function(d) { return d.year; }));
        y.domain(d3.extent(data, function(d) { return d.votes; }));

        svg.enter()
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        
        svg.attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          
         
        svg = svg.append("path")
            .datum(data)
            .attr("class", "line")
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

    return chart;

  },
  setup: function(divId,data,color) {
    d3.json('/data/municipalities.topojson', function (error,json) {
      var municipalities = topojson.feature(json, json.objects.municipalities);
      var mapChart = parties.mapChart(municipalities).width(150).color(color);
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