parties = {
  setup: function() {
    d3.json('/data/municipalities.topojson', function (error,data) {
      if (error) return console.error(error);
      // console.log(data);

      var municipalities = topojson.feature(data, data.objects.municipalities);
      // var projection = d3.geo.mercator();
      var width = 130,
          height = 330;

       var svg = d3.select("#election-map")
            .attr('width',width)
            .attr('height',height);

      var projection = d3.geo.conicEqualArea()
          .parallels([50,70])
          .scale(1300)
          .center([16.6358,62.1792])
          .translate([width / 2, height / 2]);
      var path = d3.geo.path()
          .projection(projection);

      svg.append("rect")
          .attr("width", "100%")
          .attr("height", "100%")
          .attr("fill", "pink");

      svg.append("g")
          .attr('transform','rotate(10,'+width/2+','+height/2+')')
        .selectAll(".municipality")
          .data(municipalities.features)
        .enter()
          .append("path")
          .attr("class","municipality")
          .attr("d", path)
          .attr("fill", function(d){
            var num = parseInt(d.id),
                col = d3.hsl(num/2584*360,1,0.5);
            return col.rgb();
          });

      var point = projection([14.6358,63.1792]);
      svg.append("circle")
          .attr("cx",point[0])
          .attr("cy",point[1])
          .attr("r",3)
          .attr("fill", "blue");
    });
  }
};