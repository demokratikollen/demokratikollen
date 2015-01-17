demokratikollen.graphics.dateMemberCollectionFigure = {};
demokratikollen.graphics.dateMemberCollectionFigure.Setup = function(figureDiv, dateSliderDiv, x_size, y_size, callbackObject) { //create the svg for the figure.
  $(figureDiv).append("<svg id='member_collection' viewBox='0 0 940 470' preserveAspectRatio='xMinYMin meet'>");

  // Setup the slider.
  var date = new Date();
  var s_today = date.getTime();

  var date_slider = $(dateSliderDiv).slider({
    value: s_today,
    min: callbackObject.minDate,
    max: s_today,
    step: callbackObject.dateTick,
    change: function(event, ui) {
      var self = callbackObject;
      self.UpdateFromDateSlider(self);
    }
  });

  date_slider.slider("pips", {
    rest: 'label',
    step: 8,
    formatLabel: function(value) {
      date = new Date();
      date.setTime(value);
      return date.toISOString().slice(0, 4);
    }

  });

  date_slider.slider("float", {
    formatLabel: function(value) {
      date = new Date();
      date.setTime(value);
      return date.toISOString().slice(0, 4);
    }
  });

  //Add the tooltip div.
  var tooltip = d3.select("body").append("div")
    .attr("class", "member-node-tooltip")
    .style("opacity",0);

  tooltip.append("img");
  tooltip.append("p");

  return d3.select("svg#member_collection");
}

demokratikollen.graphics.dateMemberCollectionFigure.DrawMemberNodes = function(data) {
  var canvas = d3.select('svg#member_collection');

  var anchors = canvas.selectAll('a.member_node').data(data, function(d, i) {
    return d.member_id
  });

  //remove elements
  anchors.exit().remove();

  var new_anchors = anchors.enter()
    .append("a")
    .attr("xlink:href", function(d) { return "/" + d.url_name; } )
    .attr("transform", function(d) {
      return "translate(" + d.x + "," + (-d.r * 4) + ")"
    });

  new_anchors.append("circle")
    .style("fill", function(d) {
      return demokratikollen.utils.getPartyColor(d.party).toString()
    })
    .attr("r", function(d) { return d.r; });

  new_anchors.on("mouseover", function (d) {
    d3.select("div.member-node-tooltip").style("opacity", 1);
    d3.select("div.member-node-tooltip p").text(d.name);
    d3.select("div.member-node-tooltip img").attr("src", '');
  });

  new_anchors.on("mousemove", function(d) {
    var tooltipOffsetY = 20;
    var div = d3.select("div.member-node-tooltip").style("top", (d3.event.pageY + tooltipOffsetY)+"px").style("left",(d3.event.pageX)+"px");
    d3.select("div.member-node-tooltip img").attr("src", d.image_url);

  });

  new_anchors.on("mouseout", function(d) {
    d3.select("div.member-node-tooltip").style("opacity", 0);
  })

  //Sort the nodes.
  anchors.sort(function(a, b) {
    if (a.y > b.y)
      return -1;
    else return 1;
  });

  anchors.attr('class', 'member_node');

  //update the position and animate.
  anchors.transition().duration(1000)
    .attr("transform", function(d) {
      x = d.x;
      y = d.y;
      return "translate(" + x + "," + y + ")";
    });

}

parliamentChairs = {
  Setup: function() {
    this.canvas = demokratikollen.graphics.dateMemberCollectionFigure.Setup("div#parliament_svg_div", "div#parliament_date_slider div.date_slider", 940, 470, this);
    this.UpdateFromDateSlider(this);
  },
  UpdateFromDateSlider: function(self) {
    var date_seconds = $("div#parliament_date_slider div.date_slider").slider("value");
    var date = new Date();
    date.setTime(date_seconds);

    self.date_string = date.toISOString().slice(0, 10);

    self.FetchData();
  },
  FetchData: function() {
    var self = this;
    d3.json(this.dataUrl + "?date=" + this.date_string,
      function(error, data) {
        self.ParseData(data.data);
      });
  },
  ParseData: function(data) {

    this.CalculatePartySupport(data);

    this.GeneratePositions(data);
    demokratikollen.graphics.dateMemberCollectionFigure.DrawMemberNodes(data);

    var partyAngles = this.GetPartyAngles(data);
    this.DrawPartySymbols(partyAngles);

  },
  CalculatePartySupport: function(data) {
    var n_members = data.length;
    var parties = {};
    for (key in demokratikollen.utils.parties._) {
      var party_nodes = data.filter(function(d) {
        return d.party.toLowerCase() == key
      });
      if (party_nodes.length > 0)
        parties[key] = party_nodes.length;
    }
    this.partySupport = parties;
  },
  DrawPartySymbols: function(partyAngles) {
    var self = this;
    var x0 = this.max_width / 2;
    var y0 = this.max_height;
    var radius = this.max_width / 2 - 50;

    var decorations = this.canvas.selectAll("g.decoration").data(partyAngles, function(data) {
      return data.party
    });

    decorations.exit().remove();

    var new_decorations = decorations.enter()
      .append("g")
      .attr('class', 'decoration');

    new_decorations.append("text")
      .text(function(d) {
        return self.partySupport[d.party]
      })
      .attr("class", "party_support")
      .attr("text-anchor", "middle")
      .attr("y", 35)
      .attr("font-size", "32px");

    new_decorations.append("text")
      .attr("class", "party_abbr")
      .text(function(d) {
        return d.party.toUpperCase();
      })
      .attr("text-anchor", "middle")
      .attr("font-size", "45px");

    decorations.selectAll("text.party_support")
      .text(function(d) {
        return self.partySupport[d.party]
      })
      .style('visibility', function(d) {
        return self.partySupport[d.party] < 12 ? 'hidden' : 'visible'
      });

    decorations.selectAll("text.party_abbr")
      .style('visibility', function(d) {
        return self.partySupport[d.party] < 12 ? 'hidden' : 'visible'
      });


    decorations.transition(1000).attr("transform", function(d) {
      var y = y0 - radius * Math.sin(d.angle);
      var x = x0 + radius * Math.cos(d.angle);
      return "translate(" + x + "," + y + "),rotate(" + (-d.angle + Math.PI / 2) * 180 / Math.PI + ")";
    });

  },
  GetPartyAngles: function(data) {

    var x0 = this.max_width / 2;
    var y0 = this.max_height;

    var parties = [];
    for (key in demokratikollen.utils.parties._) {
      var party_nodes = data.filter(function(d) {
        return d.party.toLowerCase() == key
      });
      if (party_nodes.length > 0 && key != '-') {
        var angle = party_nodes.reduce(
          function(p, c) {
            var x = c.x - x0;
            var y = y0 - c.y;
            var a = Math.atan(y / x);
            if (x < 0)
              a += Math.PI;
            return p + a;
          },
          0)/party_nodes.length;

        parties.push({
          party: key,
          angle: angle
        });
      }
    }
    return parties

  },
  GeneratePositions: function(data) {

    var nr = 10;
    var nrm = nr - 1;
    var R = this.chairs_inner_radius;
    var p = 5;
    var k = (nrm * nrm + nrm) / 2;

    var nc = data.length;

    var x0 = this.max_width / 2;
    var y0 = this.max_height;

    //calculate the radius of the circles for fitting the number of circles into the figure.
    var rc = (Math.PI * nr * R + p * (Math.PI * k - (nc - 1))) / (2 * nc - 2 * Math.PI * k);

    var circleData = [];

    //Calculate the radiuses for each row
    var rows = [];
    for (var i = 0; i < nr; i++) {
      var r = R + i * (p + 2 * rc);
      var n = Math.round(Math.PI * r / (p + 2 * rc));
      rows.push({
        "r": r,
        "n": n
      });
    }

    var sum_n = 0;
    for (var i = 0; i < rows.length; i++) {
      sum_n += rows[i].n;
    }

    if (sum_n > nc)
      rows[nr - 1].n--;
    if (sum_n < nc)
      rows[nr - 1].n++;

    //calculate positions for each circle. indexing should be per column, not row. Modify incoming data.
    var current_circle_index = [];
    for (var i = 0; i < nr; i++)
      current_circle_index.push(0);
    for (var i = 0; i < nc; i++) {
      //check the angle of the current circle for each row.
      var angles = [];
      var min_angle_row = 0;
      var min_angle = 100;
      for (var j = 0; j < nr; j++) {
        //correct the angle from number of dots per row. (the above calculation is not perfect.)
        angles.push(Math.PI * (current_circle_index[j] / (rows[j].n - 1)));
        if (angles[j] < min_angle) {
          min_angle_row = j;
          min_angle = angles[j];
        }
      }

      //calculate the x and y position of the lowest angle row.
      var x = -rows[min_angle_row].r * Math.cos(min_angle);
      var y = -rows[min_angle_row].r * Math.sin(min_angle);

      //update the current_circle_index
      current_circle_index[min_angle_row] ++;

      //add the position to the data.
      data[i].x = x0 + x;
      data[i].y = y0 + y;
      data[i].r = rc;
    }
  },
  canvas: null,
  partySupport: null,
  dataUrl: '/data/parliament/parliament.json',
  date_string: null,
  minDate: 512761189000,
  dateTick: 31536000000,
  chairs_inner_radius: 150,
  max_width: 940,
  max_height: 470 - 15
};