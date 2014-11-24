
P = {
    ChairsObject: {
        SetupFigure: function () {
        //remove previous elements if there exists any
        $('#parliament_svg .decoration').remove();
        $('#parliament_mode_switcher button').removeClass( "active");
        $('#parliament_button').addClass('active');    
    },
    Update: function () {
        if(P.page !== 'parliament'){
            P.page = 'parliament';
            P.ChairsObject.SetupFigure();
        }
        P.UpdateDateFromSlider(P.ChairsObject);
        P.FetchData(P.ChairsObject); 
    },
    GeneratePositions: function () {
        this.member_node_data = this.data.data;

        var nr = 10;
        var nrm = nr -1;
        var R = this.chairs_inner_radius;
        var p = 5;
        var k = (nrm*nrm +nrm)/2;

        var nc = this.member_node_data.length;

        var x0 = P.max_width/2;
        var y0 = P.max_height;

        //calculate the radius of the circles for fitting the number of circles into the figure.
        var rc = (Math.PI*nr*R + p*(Math.PI*k - (nc -1)))/(2*nc - 2*Math.PI*k);

        var circleData = [];

        //Calculate the radiuses for each row
        var rows = [];
        for(var i = 0; i < nr; i++) {
            var r = R + i*(p + 2*rc);
            var n = Math.round(Math.PI*r/(p + 2*rc));
            rows.push({"r": r, "n": n});
        }

        var sum_n = 0;
        for(var i=0; i < rows.length; i++){
          sum_n += rows[i].n;
        }

        if(sum_n > nc)
            rows[nr-1].n--;
        if(sum_n < nc)
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
            this.member_node_data[i].x = x0 + x;
            this.member_node_data[i].y = y0 + y;
            this.member_node_data[i].r = rc;
        }
    },
    ParseData: function(error, data) {
        P.ChairsObject.data = data;
        P.ChairsObject.GeneratePositions();
        P.DrawMemberNodes(P.ChairsObject);
    },
    data: null,
    dataUrl: '/data/parliament.json',
    date_string: null,
    member_node_data: null,
    chairs_inner_radius: 220
},
GenderObject: {
    SetupFigure: function() {
        //remove previous elements if there exists any
        $('#parliament_svg .decoration').remove();
        $('#parliament_mode_switcher button').removeClass( "active");
        $('#gender_button').addClass('active');
    },
    ParseData: function(error, data) {
        P.GenderObject.data = data;
        P.GenderObject.GeneratePositions();
        P.GenderObject.DrawFigLabels();
        P.DrawMemberNodes(P.GenderObject);
    },
    Update: function() {
        if(P.page !== 'gender'){
            P.page = 'gender';
            P.GenderObject.SetupFigure();
        }
        P.UpdateDateFromSlider(P.GenderObject);
        P.FetchData(P.GenderObject);
    },
    GeneratePositions: function () {
        this.member_node_data = this.data.data;
        var data = this.member_node_data;
        var nc = data.length;
        //Get the parties and how many objects there is.
        var parties = {};
        var n_parties = 0;
        for(var i=0; i < nc; i++)
        {
            if(! (data[i].party in parties))
            {
                parties[data[i].party] = {'n_males': 0, 'n_females': 0};
                n_parties++;
            }
            if(data[i].gender === 'man')
                parties[data[i].party].n_males++;
            else
                parties[data[i].party].n_females++;
                
        }
        //Give each party some space.
        var x_scale = d3.scale.linear().domain([0,n_parties]).range([this.side_padding,P.max_width-this.side_padding]);
        var counter = 0;
        for (var key in parties) {
            if (parties.hasOwnProperty(key)) {
                parties[key].x1 = x_scale(counter++);
                parties[key].x2 = x_scale(counter);
            }
        }

        //find maximum value.
        var max_n = 0;
        for (var key in parties) {
            if (parties.hasOwnProperty(key)) {
                max_n = Math.max(Math.max(parties[key].n_males, parties[key].n_females),max_n);
            }
        }

        var y_scale = d3.scale.linear().domain([0, max_n-1])
                              .range([P.max_height-this.bottom_padding, this.bottom_padding]);


        var r = 15;//(P.max_height-this.bottom_padding - (max_n-1)*this.circle_padding)/(2*max_n);

        //for each party. generate positions.
        out_data = [];
        for (var key in parties) {
            if (parties.hasOwnProperty(key)) {
                var parties_data = data.filter(function (el) { return el.party === key });
                var female_x = parties[key].x1 + (parties[key].x2 - parties[key].x1)/4;
                var male_x = parties[key].x1 + 3*(parties[key].x2 - parties[key].x1)/4;

                var counter_male = 0;
                var counter_female = 0;
                for(var i=0; i < parties_data.length; i++) {
                    if(parties_data[i].gender === 'man') {
                        parties_data[i].x = male_x;
                        parties_data[i].y = y_scale(counter_male++);
                    }
                    else {
                        parties_data[i].x = female_x;
                        parties_data[i].y = y_scale(counter_female++);
                    }
                    parties_data[i].r = r;
                }
            }
        }
        console.log(data)
    },
    DrawFigLabels: function () {

    },
    data: null,
    side_padding: 50,
    circle_padding: 5,
    bottom_padding: 20,
    dataUrl: '/data/gender.json',
    date_string: null,
    member_node_data: null
},
Setup: function() {

    // Setup the slider.
    var date = new Date();
    s_today = date.getTime()/1000;

    var date_slider = $( "#date_slider" ).slider({
        value: s_today,
        min: s_today - 3600*24*365*30,
        max: s_today,
        step: 3600*24*365,
        change: P.SliderCallback
    });
    date_slider.slider("float", 
      { formatLabel: function(value) {
        date = new Date();
        date.setTime(value*1000);
        return date.toLocaleDateString();
    }});

    //connect the buttons.
    $('#parliament_button').on('click', function () { 
        P.current_obj = P.ChairsObject;
        P.SliderCallback(); } );
    $('#gender_button').on('click', function () {
        P.current_obj = P.GenderObject;
        P.SliderCallback(); } );

    //Start with the image over the parliament.
    P.current_obj = P.ChairsObject;
    P.SliderCallback();
},
SliderCallback: function (event, ui) {
    P.current_obj.Update();
},
UpdateDateFromSlider: function(obj) {
    var date_seconds = $("#date_slider").slider("value");
    var date = new Date();
    date.setTime(date_seconds*1000);

    obj.date_string = date.toISOString().slice(0,10);
},
FetchData: function(obj){
    d3.json(obj.dataUrl + "?date=" + obj.date_string, obj.ParseData);
},
DrawMemberNodes: function(obj) {
    var canvas = d3.select('svg#parliament_svg');

    data = obj.member_node_data;

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

    //Sort the nodes.
    nodes.sort( function(a , b) { 
        if(a.y > b.y)
            return -1; 
        else return 1;
    });

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
max_width: 1140,
max_height: 1140/2,
stroke_width: 8,
partyColors: {"S": "#ED1B34", "M": "#52BDEC", "SD": "#FBC700", 
"MP": "#53A045", "C": "#016A3A", "V": "#A9291C",
"FP": "#004B92", "KD": "#073192", "NYD": "#FBC700", "-": "#CCCCCC"},
page: '',
chairs_inner_radius: 220,
current_obj: null
};

$(P.Setup)