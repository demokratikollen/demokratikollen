TC = {
    Setup: function(){ 

	var xRange = d3.time.scale().domain([new Date("2014-09-21"), new Date("2014-09-22")]).range([TC.graph.margins.left, TC.graph.width- TC.graph.margins.right]);
	var yRange = d3.scale.linear().range([TC.graph.height - TC.graph.margins.top, TC.graph.margins.bottom]).domain([0, 100]);

	var xAxis = d3.svg.axis().scale(xRange).tickSize(5).tickSubdivide(true);
	var yAxis = d3.svg.axis().scale(yRange).tickSize(5).orient("left").tickSubdivide(true);

	TC.graph.element = d3.select('#graph');
	TC.graph.element.append("svg:g").attr("class", "x axis").attr("transform", "translate(0," + (TC.graph.height - TC.graph.margins.bottom) + ")").call(xAxis);
	TC.graph.element.append("svg:g").attr("class", "y axis").attr("transform", "translate(" + (TC.graph.margins.left) + ",0)").call(yAxis);

	TC.graph.element.append("text").attr("class", "x label").attr("text-anchor", "end").attr("x", TC.graph.width-TC.graph.margins.right).attr("y", TC.graph.height - TC.graph.margins.bottom-10).text("Time");


	var button = $("#placeholder").append('<button id="refresh">Refresh</button>');
	button.on('click', null, function(){ TC.InitiateNewDataRequest();});

        TC.InitiateNewDataRequest();
    },
    InitiateNewDataRequest: function() {
        $.get('http://simlogger.apps.rohlen.net/temperature', TC.ParseReceivedData);
    },
    ParseReceivedData: function(json_data, textStatus, jqxhr) {
        var data = $.parseJSON(json_data);
        var time_zone_offset = new Date().getTimezoneOffset()*60*1000;
	TC.graph_data = [];
        data.forEach(function(datum) {
            TC.graph_data.push([Math.round(datum.date_time - time_zone_offset), datum.temperature]);
        })

	var xRange = d3.time.scale().domain([new Date(TC.graph_data[0][0]), new Date(TC.graph_data[TC.graph_data.length - 1][0])]).range([TC.graph.margins.left, TC.graph.width -TC.graph.margins.right]);
	var xAxis = d3.svg.axis().scale(xRange).tickSize(5).tickSubdivide(true);
	
	var yRange = d3.scale.linear().range([TC.graph.height - TC.graph.margins.top, TC.graph.margins.bottom]).domain([0, d3.max(TC.graph_data, function(data) {return data[1];} )+5]);
	var yAxis = d3.svg.axis().scale(yRange).tickSize(5).orient("left").tickSubdivide(true);

	//Update the axises
	TC.graph.element.select('g.x.axis').call(xAxis);
	TC.graph.element.select('g.y.axis').call(yAxis);

	//kill old path.
	TC.graph.element.select('path#data-path').remove();

	//add new path
	var lineFunc = d3.svg.line().x(function(d) { return xRange(d[0]); }).y(function(d) { return yRange(d[1]);}).interpolate('linear');
	TC.graph.element.append('svg:path').attr("id","data-path").attr('d', lineFunc(TC.graph_data)).attr('stroke', 'blue').attr('stroke-width', 2).attr('fill', 'none');

	if (window.console) console.log('got new data');

    },
    graph_data: [],
    graph: {
	element: null,
	width: 1000,
	height: 500,
	margins: {
		top: 20,
		right: 20,
		bottom: 20,
		left: 50
	}	
   }	
}

$(TC.Setup);


