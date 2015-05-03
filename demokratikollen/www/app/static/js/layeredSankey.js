demokratikollen.graphics.layeredSankey = function() {

  var width, height;
  var onNodeSelected, onNodeDeselected;
  var total_width, total_height;
  var labelspace = {top:50,left:100,right:70,bottom:0};

  var node_yspacing = 3,
      node_group_yspacing = 0;

  var node_group_ypadding = 10;

  var node_group_width = 30;
  var node_width = 30;

  var group_label_distance = 5;
  var flow_start_width = 20;

  function chart(selection) {

    var oldWidth = width;
    var oldHeight = height;
    total_width=oldWidth;
    total_height=oldHeight;
    width = oldWidth - (labelspace.right+labelspace.left);
    height = oldHeight - (labelspace.top + labelspace.bottom);

    selection.each(function(data){

      var yscale;
      
      var currently_active = null;

      function linebreak(text) {
        text.each(function() {
          var text = d3.select(this),
              words = text.text().split(/\n/).reverse(),
              word,
              lineNumber = 0,
              lineHeight = 1.1, // ems
              y = text.attr("y"),
              x = text.attr("x"),
              dx = text.attr("dx"),
              dy = .3 - (words.length-1)*lineHeight*0.5; //ems
          text.text(null);
          while (word = words.pop()) {
            tspan = text.append("tspan").attr("dx",dx).attr("x", x).attr("y", y).attr("dy", lineNumber++ * lineHeight + dy + "em").text(word);
          }
        });
      }

      compute_positions = function() {
        node_layers = data.nodes;

        node_layers.forEach(function(layer, layer_idx){
          var y = 0.5*(height-layer.total_height) + labelspace.top;
          layer.y = y;
          layer.items.forEach(function(group, group_idx){

            group.x = labelspace.left+(width-node_group_width)*layer.x;
            group.y = y;
            y += node_group_ypadding;

            group.items.forEach(function(node, node_idx){
              node.x = group.x + 0.5*(node_group_width-node_width);
              node.y = y;
              y += node.size * yscale;
              node.height = y - node.y;
              y += node_yspacing;

              node.layer_idx = layer_idx;
              node.group_idx = group_idx;
              node.node_idx = node_idx;
              node.unique_id = [layer_idx, group_idx, node_idx].join("-");
 
              if (!node.color) node.color = "#aaa";
            });

            y -= node_yspacing;
            y += node_group_ypadding;
            group.height = y - group.y;
            
            y += node_group_yspacing;

          });
          y -= node_group_yspacing;
        });
      };

      compute_sizes = function() {

        var nodes = data.nodes;
        var flows = data.flows;

        // reset counters from any previous render
        nodes.forEach(function(layer){
          layer.size = 0;
          layer.items.forEach(function(group){
            group.size = 0;
            group.items.forEach(function(node){
              node.size = 0;
              node.filled_out_y = 0;
              node.filled_in_y = 0;
            });
          });
        });

        // compute and store sizes of all layers, groups and nodes by counting flows through them
        flows.forEach(function(flow){
          flow.path.forEach(function(p) {
            layer = nodes[p[0]];
            node_group = layer.items[p[1]];
            node = node_group.items[p[2]];
            layer.size += flow.magnitude;
            node_group.size += flow.magnitude;
            node.size += flow.magnitude;
          });
        });

        
        nodes.forEach(function(layer){
          layer.num_node_spacings = d3.sum(layer.items, function(g){return g.items.length-1;});
          layer.num_group_spacings = layer.items.length-1;
        });

        // yscale calibrated to fill height after equation:
        // height == size*yscale + group_spacing + group_padding + node_spacing
        // (take worst case: smallest value)
        yscale = d3.min(nodes, function(d){
          return (height 
                  - d.num_group_spacings*node_group_yspacing
                  - d.items.length*node_group_ypadding*2
                  - d.num_node_spacings*node_yspacing)/d.size;
        });

        nodes.forEach(function(layer){
          layer.total_height = layer.size * yscale
                              + layer.num_group_spacings*node_group_yspacing
                              + layer.items.length*node_group_ypadding*2
                              + layer.num_node_spacings*node_yspacing;
        });


      };

      compute_flow_areas = function() {

        var nodes = data.nodes;
        var flows = data.flows;
        var flows_copy = data.flows.map(function(f){
          var f2 = {magnitude: f.magnitude};
          f2.path = f.path.map(function(addr){
            return addr.slice(0);
          });
          return f2;
        });
        
        flows.forEach(function(flow){
          flow.extra_classes = flow.path.map(function(addr){return "passes-"+addr.join("-");}).join(" ");
        });


        while(true) {

          flows_copy = flows_copy.filter(function(d){return d.path.length > 1});
          if (flows_copy.length == 0) return;

          flows_copy.sort(function(a,b){
            return   a.path[0][0]-b.path[0][0] 
                  || a.path[0][1]-b.path[0][1] 
                  || a.path[0][2]-b.path[0][2]
                  || a.path[1][0]-b.path[1][0] 
                  || a.path[1][1]-b.path[1][1] 
                  || a.path[1][2]-b.path[1][2];
          });

          var layer_idx = flows_copy[0].path[0][0];
          flows_copy.forEach(function(flow){

            if (flow.path[0][0] != layer_idx) return;
            var from = flow.path[0];
            var to = flow.path[1];
            var h = flow.magnitude*yscale;

            var source = nodes[from[0]].items[from[1]].items[from[2]];
            var target = nodes[to[0]].items[to[1]].items[to[2]];

            var source_y0 = source.filled_out_y || source.y;
            var source_y1 = source_y0 + h;
            source.filled_out_y = source_y1;
            var target_y0 = target.filled_in_y || target.y;
            var target_y1 = target_y0 + h;
            target.filled_in_y = target_y1;

            flow_area_data.push({
              area: [
                      {x: source.x+node_width, y0: source_y0, y1: source_y1},
                      {x: source.x+node_width+flow_start_width, y0: source_y0, y1: source_y1},
                      {x: target.x-flow_start_width, y0: target_y0, y1: target_y1},
                      {x: target.x, y0: target_y0, y1: target_y1},
                    ],
              class: ["flow", flow.extra_classes].join(" ")
              });

            flow.path.shift();
          });
        }        

      };

      var flow_area_data = [];

      compute_sizes();
      compute_positions();
      compute_flow_areas();

      var parent = d3.select(this);

      var node_layers = parent.selectAll(".node-layers")
                            .data(prop("nodes"));
      nl_labelx = function(d){return labelspace.left+d.x*(width-node_width)+0.5*node_width;}
      nl_labely = function(d){return 0.5*labelspace.top;}

      node_layers.enter()
                  .append("g").classed("node-layer",true)
                  .append("text")
                    .attr("class", "layer-label")
                    .attr("text-anchor","middle")
                    .attr("dx",0)
                    .attr("dy",0)
                    .attr("x", nl_labelx)
                    .attr("y", nl_labely)
                    .text(prop("title")).call(linebreak);

      var node_groups = node_layers.selectAll(".node-group")
                                    .data(prop("items"));
      node_groups.enter()
                  .append("g").classed("node-group", true);

      node_groups.append("rect")
            .classed("node-group", true)
            .attr("x", prop("x"))
            .attr("y", prop("y"))
            .attr("width", node_group_width)
            .attr("height", prop("height"));

      ng_labelx = function(d){return d.x+0.5*node_width+0.5*d.label*node_width;}
      ng_labely = function(d){return d.y + 0.5*d.height;}

      var tip = d3.tip().attr('class', 'd3-tip')
      .direction('e')
      .html(function(d) { return d.title; });
      parent.call(tip)
      
      var group_labels = node_groups.append("g")
        .style("display",function(d){return d.label ? "" : "none";})
        .attr("class","node-group-label");
      group_labels.append("text")
        .attr("text-anchor","end")
        .attr("dx",function(d){return d.label*(group_label_distance*2);})
        .attr("dy","0.3em")
        .attr("x", ng_labelx)
        .attr("y", ng_labely)
        .text(prop("title")).call(linebreak);


      group_labels.append("path")
        .attr("d", function(d){
          return d3.svg.line()([
            [ng_labelx(d)+group_label_distance*d.label ,d.y+node_group_ypadding],
            [ng_labelx(d)+group_label_distance*d.label ,d.y+d.height-node_group_ypadding]
            ]);});

      var flows_elements = parent.selectAll(".flow").data(flow_area_data)
        .enter()
          .append("path")
          .attr("class", prop("class"))
          .datum(prop("area"))
          .attr("d", 
            d3.svg.area()
              .x(prop("x"))
              .y0(prop("y0"))
              .y1(prop("y1"))
              .interpolate("basis"));

      var nodes_elements = node_groups.selectAll(".node")
                          .data(prop("items"));
      nodes_elements.enter()
            .append("g").attr("class", "node");
      nodes_elements.append("rect")
            .attr("class", function(d){return "node-"+d.unique_id;})
            .attr("x", prop("x"))
            .attr("y", prop("y"))
            .attr("width", node_width)
            .attr("height",prop("height"))
            .style("fill", function(d){return d.color;})
            .on("mouseover", function(d){
              d3.select(this).transition().style("fill", d.color.brighter());
              tip.show(d);
            })
            .on("mouseout", function(d){
              d3.select(this).transition().style("fill", d.color);
              tip.hide(d);
            })
            .on("click", function(d,i){
              
              var node_id = d.unique_id;

              if (currently_active) {
                if (onNodeDeselected) onNodeDeselected(currently_active.d);

                var theflows = parent.selectAll(".passes-"+currently_active.id);
                var thenode = parent.selectAll(".node-"+currently_active.id);

                theflows.transition()
                  .style("fill", null)
                  .style("fill-opacity", null);


                 if (currently_active.id == node_id) {
                   currently_active = null;
                   return;
                 }
              }

              theflows = parent.selectAll(".passes-"+node_id);
              thenode = parent.selectAll(".node-"+node_id);


              theflows.transition()
                .style("fill", d.color)
                .style("fill-opacity", 1.0);

              currently_active = {"id": node_id, "d": d};
              if (onNodeSelected) onNodeSelected(d);
              
            });          
    }); // selection.each()
    width = oldWidth;
    height = oldHeight;
  };
  
  chart.width = function(_) {
    if (!arguments.length) return width;
    else width = +_;
    return chart;
  }
  chart.height = function(_) {
    if (!arguments.length) return height;
    else height = +_;
    return chart;
  }    
  chart.onNodeSelected = function(_) {
    if (!arguments.length) return onNodeSelected;
    else onNodeSelected = _;
    return chart;
  }   
  chart.onNodeDeselected = function(_) {
    if (!arguments.length) return onNodeDeselected;
    else onNodeDeselected = _;
    return chart;
  }    

  return chart;
};
