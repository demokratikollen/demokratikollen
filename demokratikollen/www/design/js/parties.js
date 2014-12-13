parties = {
  mapChart: function(regions) {
    var width = 130,
        height = 2.53846153846*width;

    var projection = d3.geo.conicEqualArea()
        .parallels([50,70])
        .center([16.6358,62.1792])

    var path = d3.geo.path();

    var featureNames = {};

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
            .attr('class', 'tooltip')
            .style("opacity", 0);

        // Setup tooltip events
        regs.on("mouseover", function(d){
              return tooltip.html("<strong>"+regMap.get(d.id).properties.name+":</strong> "
                              +"<span style='color:"+colorScale(0.5*max_votes)+"'>" + Math.round(100*d.votes) + "</span> %")
                            .transition()
                            .duration(100)
                            .style("opacity",0.9);
            })
            .on("mousemove", function(d){
              return tooltip.style("top", (event.pageY-40)+"px").style("left",(event.pageX)+"px");
            })
            .on("mouseout", function(d){
              return tooltip.transition()
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