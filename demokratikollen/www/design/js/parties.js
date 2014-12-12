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

    function chart(selection) {
      selection.each(function(data, i) {
        var max_votes = data.max_votes;
        var svg = d3.select(this).selectAll("svg").data([data.d]);

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
            .data(data.d, prop("id"));

        var color = d3.scale.linear().domain([0,max_votes]).range(['white', 'green']);

        regs.transition()
            .duration(200)
            .attr("fill",function(d) {
              return color(d.votes);
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

    return chart;
  },
  setup: function(divId,data) {
    d3.json('/data/municipalities.topojson', function (error,json) {
      var municipalities = topojson.feature(json, json.objects.municipalities);
      var mapChart = parties.mapChart(municipalities).width(150);
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