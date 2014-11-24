
P = {
  Setup: function() {
    
    // Setup the slider.
    var date = new Date();
    s_today = date.getTime()/1000;

    var date_slider = $( "#date_slider" ).slider({
      value: s_today,
      min: s_today - 3600*24*365*30,
      max: s_today,
      step: 3600*24*365,
      slide: P.UpdateFromSlider,
      change: P.UpdateFromSlider
    });
    date_slider.slider("float", 
      { formatLabel: function(value) {
        date = new Date();
        date.setTime(value*1000);
        return date.toLocaleDateString();
    }});

    //connect the buttons.
    $('#parliament_button').on('click', P.SetupParliament);
    $('#gender_button').on('click', P.SetupGender);

    //Start with the image over the parliament.
    P.SetupParliament();

  },
  SetupGender: function() {
    //remove previous elements if ther exists any
    if(P.page !== 'gender'){

      $('#parliament_svg .decoration').remove();

      var canvas = d3.select('svg#parliament_svg');

      var padding = P.max_width - 4* P.gender_radius;
      var middle_padding = 2/3*padding;
      var outer_padding = (padding - middle_padding)/2;

      var female_g = canvas
                .append('g')
                .attr("id", "female")
                .attr("class", "decoration")
                .attr('transform', "translate(" + (P.gender_radius + outer_padding)
                                                + ","
                                                + (P.gender_radius + 10)
                                                + ")");
      P.female_x0 = (P.gender_radius + outer_padding);
      P.female_y0 = (P.gender_radius + 10);

      var male_g = canvas
                .append('g')
                .attr('id', 'male')
                .attr('class', 'decoration')
                .attr('transform', 'translate(' + (outer_padding + 2*P.gender_radius + middle_padding + P.gender_radius)
                                                + ','
                                                + (P.gender_radius + 50)
                                                + ')');
      P.male_x0 = (outer_padding + 2*P.gender_radius + middle_padding + P.gender_radius);
      P.male_y0 = (P.gender_radius + 50);
    

      var symbol_length = 0.5*P.gender_radius;

      female_g.append("circle").attr("r", P.gender_radius);
      female_g.append('line').attr('x1',0)
                           .attr('x2',0)
                           .attr('y1',P.gender_radius)
                           .attr('y2',P.gender_radius+symbol_length);
      female_g.append('line').attr('x1',-symbol_length/2)
                           .attr('x2',symbol_length/2)
                           .attr('y1',P.gender_radius+symbol_length/2)
                           .attr('y2',P.gender_radius+symbol_length/2);

      var trig45 = 0.70710678118
      male_g.append('circle').attr('r', P.gender_radius);
      male_g.append('line').attr('x1',trig45*P.gender_radius)
                         .attr('x2',trig45*(P.gender_radius+symbol_length))
                         .attr('y1',-trig45*P.gender_radius)
                         .attr('y2',-trig45*(P.gender_radius + symbol_length));

      male_g.append('line').attr('x1',trig45*(P.gender_radius+symbol_length))
                         .attr('x2',trig45*(P.gender_radius+symbol_length)-symbol_length/2)
                         .attr('y1',-trig45*(P.gender_radius+symbol_length))
                         .attr('y2',-trig45*(P.gender_radius+symbol_length));

      male_g.append('line').attr('x1',trig45*(P.gender_radius+symbol_length))
                         .attr('x2',trig45*(P.gender_radius+symbol_length))
                         .attr('y1',-trig45*(P.gender_radius+symbol_length)-P.stroke_width/2)
                         .attr('y2',-trig45*(P.gender_radius+symbol_length)+symbol_length/2);

      P.page = 'gender';
      $('#parliament_mode_switcher button').removeClass( "active");
      $('#gender_button').addClass('active');
      P.UpdateFromSlider();
    }
  },
  SetupParliament: function() {
    //remove previous elements if ther exists any
    if(P.page !== 'parliament'){
      $('#parliament_svg .decoration').remove();
      P.page = 'parliament';
      $('#parliament_mode_switcher button').removeClass( "active");
      $('#parliament_button').addClass('active');
      P.UpdateFromSlider();
    }
  },
  UpdateFromSlider: function() {

    var date_seconds = $("#date_slider").slider("value");
    var date = new Date();
    date.setTime(date_seconds*1000);

    switch(P.page) {
    case 'parliament':
        P.FetchParliamentData(date,'');
        break;
    case 'gender':
        P.FetchGenderData(date,'');
        break;
    }
  },
  FetchGenderData: function(date, party) {

      date = typeof date !== 'undefined' ? date : '';
      dateString = date.toISOString().slice(0,10)
      party = typeof party !== 'undefined' ? party : '';

      d3.json("/data/gender.json?party=" + party + "&date=" + dateString, function(error, root) {

        var data = {'name': 'root', 'children': root.data};

        P.GenerateGenderPositions(data);

        P.DrawMemberNodes(data.children);

        //P.DrawGenderCircles('kvinna', root.statistics.n_females, female_data);
        //P.DrawGenderCircles('man', root.statistics.n_males, male_data);

      });
  },
  FetchParliamentData: function(date) {

      date = typeof date !== 'undefined' ? date : '';
      dateString = date.toISOString().slice(0,10)

      d3.json("/data/parliament.json?date=" + dateString, function(error, data) {
        P.GenerateChairsPositions(data);
        P.DrawMemberNodes(data.data);
      });
  },
  DrawMemberNodes: function(data) {
    var canvas = d3.select('svg#parliament_svg');

    console.log(data);

    var nodes = canvas.selectAll('g.member_node').data(data,function (d,i) { return d.member_id });

    //remove elements
    nodes.exit().remove();

    var new_nodes = nodes.enter()
                    .append('g').attr("class", 'member_node')
                    .attr("transform", "translate(" + (P.max_width/2) + "," + P.max_height +")");

    new_nodes.append("title")
      .text(function(d) { return d.member_id });

    new_nodes.append("circle")
        .style("stroke-width",'1px')
        .style("fill", function(d) {return P.partyColors[d.party]});

    //update the position for the olf ones and animate.
    nodes.transition().duration(1000)
         .attr("transform", function(d) { 
                    x = d.x;
                    y = d.y;
                    return "translate(" + x + "," + y + ")";
                   });
    
    //update the radius of the circle if needed.
    nodes.selectAll('circle').data(data).transition().attr("r", function(d) { return d.r; });
  },
  GenerateGenderPositions: function(data) {
    var padding = 5;
    var circle_radius = 10;
    
    female_data = {'name': 'root', 'children': data.children.filter(function (el) { return el.gender === 'kvinna' } )};
    male_data = {'name': 'root', 'children': data.children.filter(function (el) { return el.gender === 'man' } )};

    var pack = d3.layout.pack()
          .size([P.gender_radius, P.gender_radius])
          .radius(function () { return circle_radius })
          .value(function () {return 1})
          .sort(null)
          .padding(padding);

    if (female_data.children.length > 200) 
      pack.radius(function () {return 8});
    female_data = pack.nodes(female_data).filter(function(d) { return !d.children; });
    pack.radius(function() { return circle_radius});
    
    if(male_data.children.length > 200)
      pack.radius(function () {return 8});
    male_data = pack.nodes(male_data).filter(function(d) { return !d.children; });

    data = female_data.concat(male_data);

    for(var i=0; i < data.length; i++){
      if (data[i].gender === 'kvinna'){
        data[i].x += P.female_x0 - P.gender_radius/2;
        data[i].y += P.female_y0 - P.gender_radius/2;
      }
      else {
        data[i].x += P.male_x0 - P.gender_radius/2;
        data[i].y += P.male_y0 - P.gender_radius/2;
      }
    }

  },
  GenerateChairsPositions: function(data) {
    var nr = 10;
    var nrm = nr -1;
    var R = P.chairs_inner_radius;
    var p = 5;
    var k = (nrm*nrm +nrm)/2;

    var nc = data.data.length;

    var x0 = P.max_width/2;
    var y0 = P.max_height;

    //calculate the radius of the circles for fitting the number of circles into the figure.
    var rc = (Math.PI*nr*R + p*(Math.PI*k - (nc -1)))/(2*nc - 2*Math.PI*k);

    var circleData = [];

    //Calculate the radiuses for each row
    var rows = []
    for(var i = 0; i < nr; i++) {
      var r = R + i*(p + 2*rc);
      var n = Math.round(Math.PI*r/(p + 2*rc));
      rows.push({"r": r, "n": n});
    }

    var sum_n = 0;
    for(var i=0; i < rows.length; i++){
      sum_n += rows[i].n;
    }

    if(sum_n > data.statistics.n_members)
      rows[nr-1].n--;
    if(sum_n < data.statistics.n_members)
      rows[nr-1].n++;

    //calculate positions for each circle. indexing should be per column, not row. Modify incoming data.
    var current_circle_index = [];
    for(var i=0; i < nr; i++)
      current_circle_index.push(0);
    for(var i = 0; i < nc; i++) {
      //check the angle of the current circle for each row.
      var angles = [];
      var min_angle_row = 0; 
      var min_angle = 100;    
      for(var j=0; j < nr; j++) {
        //correct the angle from number of dots per row. (the above calculation is not perfect.)
        angles.push(Math.PI*(current_circle_index[j]/(rows[j].n-1)));
        if(angles[j] < min_angle) {
          min_angle_row = j;
          min_angle = angles[j]; 
        }
      }

      //calculate the x and y position of the lowest angle row.
      var x = -rows[min_angle_row].r*Math.cos(min_angle);
      var y = -rows[min_angle_row].r*Math.sin(min_angle);

      //update the current_circle_index
      current_circle_index[min_angle_row]++;

      //add the position to the data.
      data.data[i].x = x0 + x;
      data.data[i].y = y0 + y;
      data.data[i].r = rc;
    } 
  },
  gender_radius: 220,
  max_width: 1140,
  max_height: 1140/2,
  stroke_width: 8,
  partyColors: {"S": "#ED1B34", "M": "#52BDEC", "SD": "#FBC700", 
                  "MP": "#53A045", "C": "#016A3A", "V": "#A9291C",
                  "FP": "#004B92", "KD": "#073192", "NYD": "#FBC700", "-": "#CCCCCC"},
  page: '',
  chairs_inner_radius: 220
};

$(P.Setup)