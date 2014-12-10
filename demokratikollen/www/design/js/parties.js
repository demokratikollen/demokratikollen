parties = {
  mapChart: function(regions) {
    var width = 130,
        height = 2.53846153846*width;

    var transform = 'rotate(10,'+width/2+','+height/2+')';

    var projection = d3.geo.conicEqualArea()
        .parallels([50,70])
        .center([16.6358,62.1792])        

    var path = d3.geo.path();

    function idProp(d) {
      return d.id;
    }

    function chart(selection) {
      console.log(regions);
      selection.each(function(data, i) {
        var svg = d3.select(this).selectAll("svg").data([data]);

        console.log(svg);

        // Update projection and path
        projection.scale(10*width)
            .translate([width / 2, height / 2]);
        path.projection(projection);

        // Otherwise, create the skeletal chart.
        var gMain = svg.enter().append("svg").append("g");
        var sel = gMain.attr("class","map-collection")
            .attr('transform',transform)
            .selectAll(".map-region")
            .data(regions.features, idProp)
            .enter()
            .append("path")
            .attr("class","map-region")
            .attr("d", path);

        console.log(sel);

        svg.attr("width", width)
            .attr("height", height)
            .selectAll(".map-region")
            .data(data, idProp)
            .attr("fill",function(d) { return d.color });
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
      return chart;
    };

    chart.height = function(_) {
      if (!arguments.length) return height;
      height = _;
      return chart;
    };

    return chart;
  },
  setup: function(divId,data) {
    d3.json('/data/municipalities.topojson', function (error,json) {
      var municipalities = topojson.feature(json, json.objects.municipalities);
      var mapChart = parties.mapChart(municipalities);
      d3.select(divId)
        .datum(data)
        .call(mapChart);
    });
  }
};