demokratikollen.graphics.layeredSankey = function() {

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
          dy = 0.3 - (words.length-1)*lineHeight*0.5; //ems
      text.text(null);
      while (word = words.pop()) {
        tspan = text.append("tspan").attr("dx",dx).attr("x", x).attr("y", y).attr("dy", lineNumber++ * lineHeight + dy + "em").text(word);
      }
    });
  }

  var width, height;
  var onNodeSelected, onNodeDeselected;
  var labelspace = {top:50,left:100,right:70,bottom:0};
  var selectedNodeAddress = null;

  var nodeYSpacing = 3,
      nodeGroupYSpacing = 0;

  var nodeGroupYPadding = 10;

  var nodeWidth = 30;

  var groupLabelDistance = 5;
  var flowStartWidth = 20;

  function chart(selection) {

    selection.each(function(data){

      var parent = d3.select(this);
      var yscale;
      var currentlyActive = null;

      var availableWidth = width - (labelspace.right+labelspace.left);
      var availableHeight = height - (labelspace.top + labelspace.bottom);

      var flow_area_data = [];


      /* 
      The anonymous function is used to scope the algorithm for
      preparing the data.

      It computes sizes and positions for all nodes 
      and flows and saves them on original data structure.

      It does not mutate original data (because then multiple call() would
      then destroy the chart.) 
      */ 
      (function() {

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
        // availableHeight == size*yscale + group_spacing + group_padding + node_spacing
        // (take worst case: smallest value)
        yscale = d3.min(nodes, function(d){
          return (availableHeight 
                  - d.num_group_spacings*nodeGroupYSpacing
                  - d.items.length*nodeGroupYPadding*2
                  - d.num_node_spacings*nodeYSpacing)/d.size;
        });

        nodes.forEach(function(layer){
          layer.totalHeight = layer.size * yscale
                              + layer.num_group_spacings*nodeGroupYSpacing
                              + layer.items.length*nodeGroupYPadding*2
                              + layer.num_node_spacings*nodeYSpacing;
        });


        // use sizes to compute positions of all layers, groups and nodes
        nodes.forEach(function(layer, layer_idx){
          var y = 0.5*(availableHeight-layer.totalHeight) + labelspace.top;
          layer.y = y;
          layer.items.forEach(function(group, group_idx){

            group.x = labelspace.left+(availableWidth-nodeWidth)*layer.x;
            group.y = y;
            y += nodeGroupYPadding;

            group.items.forEach(function(node, node_idx){
              node.x = group.x;
              node.y = y;
              y += node.size * yscale;
              node.height = y - node.y;
              y += nodeYSpacing;

              node.layer_idx = layer_idx;
              node.group_idx = group_idx;
              node.node_idx = node_idx;
              node.unique_id = [layer_idx, group_idx, node_idx].join("-");
 
              if (!node.color) node.color = d3.hsl("#aaa");
            });

            y -= nodeYSpacing;
            y += nodeGroupYPadding;
            group.height = y - group.y;
            
            y += nodeGroupYSpacing;

          });
          y -= nodeGroupYSpacing;
        });


        
        // Compute all the path data for the flows.
        // First make a deep copy of the flows data because
        // algorithm is destructive
        var flows_copy = data.flows.map(function(f){
          var f2 = {magnitude: f.magnitude};
          f2.extra_classes = f.path.map(function(addr){return "passes-"+addr.join("-");}).join(" ");
          f2.path = f.path.map(function(addr){
            return addr.slice(0);
          });
          return f2;
        });

        while(true) {

          flows_copy = flows_copy.filter(function(d){return d.path.length > 1;});
          if (flows_copy.length === 0) return;

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
                      {x: source.x+nodeWidth, y0: source_y0, y1: source_y1},
                      {x: source.x+nodeWidth+flowStartWidth, y0: source_y0, y1: source_y1},
                      {x: target.x-flowStartWidth, y0: target_y0, y1: target_y1},
                      {x: target.x, y0: target_y0, y1: target_y1},
                    ],
              class: ["flow", flow.extra_classes].join(" ")
              });

            flow.path.shift();
          });
        }        

      })(); // end of data preparation


      // Create all svg elements: layers, groups, nodes and flows.

      var nodeLayers = parent.selectAll(".node-layers")
                            .data(prop("nodes"));

      nl_labelx = function(d){return labelspace.left+d.x*(availableWidth-nodeWidth)+0.5*nodeWidth;};
      nl_labely = function(d){return 0.5*labelspace.top;};
      nodeLayers.enter()
                  .append("g").classed("node-layer",true)
                  .append("text")
                    .attr("class", "layer-label")
                    .attr("text-anchor","middle")
                    .attr("dx",0)
                    .attr("dy",0);

      nodeLayers.selectAll("text")
                    .attr("x", nl_labelx)
                    .attr("y", nl_labely)
                    .text(prop("title")).call(linebreak);

      nodeLayers.exit().remove();

      var nodeGroups = nodeLayers.selectAll("g.node-group").data(prop("items"));
      var enteringNodeGroups = nodeGroups.enter().append("g").classed("node-group", true);

      enteringNodeGroups.append("rect").classed("node-group", true);
      var enteringNodeGroupsG = enteringNodeGroups.append("g").attr("class","node-group-label");

      enteringNodeGroupsG.append("path");
      enteringNodeGroupsG.append("text");

      nodeGroups.selectAll("g.node-group > rect")
            .attr("x", prop("x"))
            .attr("y", prop("y"))
            .attr("width", nodeWidth)
            .attr("height", prop("height"));

      nodeGroups.selectAll("g.node-group > g")
        .style("display",function(d){return d.label ? "" : "none";});

      ng_labelx = function(d){return d.x+0.5*nodeWidth+0.5*d.label*nodeWidth;};
      ng_labely = function(d){return d.y + 0.5*d.height;};
      nodeGroups.selectAll("g.node-group > g > path")
        .attr("d", function(d){
          return d3.svg.line()([
            [ng_labelx(d)+groupLabelDistance*d.label ,d.y+nodeGroupYPadding],
            [ng_labelx(d)+groupLabelDistance*d.label ,d.y+d.height-nodeGroupYPadding]
            ]);});

      nodeGroups.selectAll("g.node-group > g > text")
        .attr("text-anchor","end")
        .attr("dx",function(d){return d.label*(groupLabelDistance*2);})
        .attr("dy","0.3em")
        .attr("x", ng_labelx)
        .attr("y", ng_labely)
        .text(prop("title")).call(linebreak);


      nodeGroups.exit().remove();

      // TODO get rid of dependency
      var tip = d3.tip().attr('class', 'd3-tip')
        .direction('e')
        .html(function(d) { return d.title; });
      parent.call(tip);

      var flowElements = parent.selectAll("path.flow").data(flow_area_data);
      flowElements.enter().append("path").attr("class", prop("class"));

      flowElements  
        .datum(prop("area"))
        .attr("d", 
          d3.svg.area()
            .x(prop("x"))
            .y0(prop("y0"))
            .y1(prop("y1"))
            .interpolate("basis"));
      flowElements.exit().remove();

      
      function activateNode(d){
        var node_id = d.unique_id;
        var theflows, thenode;

        if (currentlyActive) {
          if (currentlyActive.id == node_id) {
            return;
          }

          if (onNodeDeselected) onNodeDeselected(currentlyActive.d);

          theflows = parent.selectAll(".passes-"+currentlyActive.id);
          thenode = parent.selectAll(".node-"+currentlyActive.id);

          theflows
            .style("fill", null)
            .style("fill-opacity", null);
        }

        theflows = parent.selectAll(".passes-"+node_id);
        thenode = parent.selectAll(".node-"+node_id);

        theflows.transition()
          .style("fill", d.color)
          .style("fill-opacity", 1.0);

        thenode.style("fill", d.color);
        currentlyActive = {"id": node_id, "d": d};
        selectedNodeAddress = node_id.split("-").map(function(d){return parseInt(d);});
        if (onNodeSelected) onNodeSelected(d);        
      }

      function mouseoverNode(d) {
        tip.show(d);
        if (currentlyActive && currentlyActive.id == d.unique_id) {
          return;
        }
        d3.select(this).transition().style("fill", d.color.brighter());
      }

      function mouseoutNode(d) {
        tip.hide(d);
        if (currentlyActive && currentlyActive.id == d.unique_id) {
          return;
        }
        d3.select(this).transition().style("fill", d.color);
      }

      var nodeElements = nodeGroups.selectAll("rect.node").data(prop("items"));
      nodeElements.enter().append("rect").attr("class", function(d){return "node node-"+d.unique_id;});
      nodeElements
        .attr("x", prop("x"))
        .attr("y", prop("y"))
        .attr("width", nodeWidth)
        .attr("height",prop("height"))
        .style("fill", function(d){return d.color;})
        .on("mouseover", mouseoverNode)
        .on("mouseout", mouseoutNode)
        .on("click", activateNode);
      nodeElements.exit().remove();
      
      if (selectedNodeAddress) {
        var node = data.nodes[selectedNodeAddress[0]]
                          .items[selectedNodeAddress[1]]
                          .items[selectedNodeAddress[2]];
        activateNode(node);
      }        
    }); // selection.each()
  }
  
  chart.width = function(_) {
    if (!arguments.length) return width;
    else width = +_;
    return chart;
  };
  chart.height = function(_) {
    if (!arguments.length) return height;
    else height = +_;
    return chart;
  };    
  chart.onNodeSelected = function(_) {
    if (!arguments.length) return onNodeSelected;
    else onNodeSelected = _;
    return chart;
  };   
  chart.onNodeDeselected = function(_) {
    if (!arguments.length) return onNodeDeselected;
    else onNodeDeselected = _;
    return chart;
  };
  chart.selectedNodeAddress = function(_) {
    if (!arguments.length) return selectedNodeAddress;
    else selectedNodeAddress = _;
    return chart;
  }; 
  return chart;
};
