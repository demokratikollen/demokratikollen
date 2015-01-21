(function(context){

  var dataURL = '/search.json';
  var searchboxSelector = '#searchbox';
  var innerProducts;

  context.initSearch = function(){

    var searchboxElement = d3.select(searchboxSelector);
    var trigramLookup = d3.map();
    var n = 3;
    var relativeScoreCutoff = 0.85; // filter all matches with score < cutoff * maxScore
    var maxHitsPerGroup = 3;

    function countGrams(s) {
      var s = " ".concat(s.trim(), " ");
      var index = s.length - n + 1;
      var gramCounts = d3.map();

      if (index < 1) return gramCounts;

      while (index--) {
        var gram = s.substr(index, n);
        gramCounts.set(gram, gramCounts.get(gram) + 1 || 1);
      }

      return gramCounts;
    }

    d3.json(dataURL, function(err,data){
      if (err) {
        console.warn(err);
        return;
      }

      var keywords = data.keywords;

      // make space for all inner products
      innerProducts = Array(keywords.length);

      // index keywords
      data.keywords.forEach(function(keyword, keywordIdx) {
        var gramCounts = countGrams(keyword.string);
        var invNormSquared = 1.0/d3.sum(gramCounts.values()
                          .map(function(x){return x*x;}));

        gramCounts.forEach(function(gram, count){

          if(!trigramLookup.has(gram)){
            trigramLookup.set(gram, []);
          }
          trigramLookup.get(gram).push([keywordIdx, count]);

        });
      });


      function search(query) {

        for (var i = keywords.length-1; i; i--) {
          innerProducts[i] = 0;
        }

        var queryGramCounts = countGrams(query.toLowerCase());

        queryGramCounts.forEach(function(queryGram, queryGramCount) {
          var keywordList = trigramLookup.get(queryGram);
          if (!keywordList) return;
          keywordList.forEach(function(pair){
            var keywordIdx = pair[0];
            var keywordGramCount = pair[1];
            innerProducts[keywordIdx] += keywordGramCount * queryGramCount;
          });
        });

        var maxScore = d3.max(innerProducts);
        var matches = innerProducts
                  .map(function(x,i){return {keyword: keywords[i], score: x};})
                  .filter(function(p){return p.score > relativeScoreCutoff*maxScore;})
                  .sort(function(a,b) {return b.score-a.score;});

        if (!matches) return null;

        var primary = matches[0].keyword.primary;
        var result = {
          top: data.groups[primary[0]].objects[primary[1]],
          groups: data.groups.map(function(g){return {title:g.title, objects: []};})
        };

        // first add all primary matches, if result set is not full, add secondary matches
        matches.some(function(m){
          var primary = m.keyword.primary;
          var primaryGroup = result.groups[primary[0]];
          if (primaryGroup.objects.length >= maxHitsPerGroup) return;

          if (-1 == primaryGroup.objects.indexOf(primary[1])) {
            primaryGroup.objects.push(primary[1]);
          }

          // stop when all groups have >= some number of hits
          return result.groups
              .map(function(g){return g.objects.length >= maxHitsPerGroup})
              .reduce(function(acc, x){return acc && x;})
        });
        matches.some(function(m){
          m.keyword.secondaries.forEach(function(secondary){
            var secondaryGroup = result.groups[secondary[0]];
            if (secondaryGroup.objects.length >= maxHitsPerGroup) return;

            if (-1 == secondaryGroup.objects.indexOf(secondary[1])) {
              secondaryGroup.objects.push(secondary[1]);
            }

          // stop when all groups have >= some number of hits
          return result.groups
              .map(function(g){return g.objects.length >= maxHitsPerGroup})
              .reduce(function(acc, x){return acc && x;})

          });
        });
        result.groups.forEach(function(g,gIdx){
          g.objects = g.objects.map(function(o){
            return data.groups[gIdx].objects[o];
          });
        });

        return result;

      }

      d3.select('#main-search')
            .on("focusout",function() {
              d3.select(this).classed("open",false);
            })
            .on("focusin",function() {
              var q = searchboxElement.property("value");
              if (q.length < 2) return;
              d3.select(this).classed("open",true);
            });

      var results = [];
      searchboxElement.on("keydown", function() {
        if (d3.event.keyCode == 13) { // Enter key
          if (results) {
            d3.event.preventDefault();
            location.href = results.top.url;
          }
        }
      });
      searchboxElement.on("keyup", function(){


        var q = this.value;
        if (q.length < 2) {
          d3.select('#main-search').classed("open",false);
          return;
        }

        results = search(q);



        d3.select('#main-search').classed("open",true);
        var ul = d3.select("#searchresults");

        var tophit = ul.selectAll(".tophit").data([results.top]);
        tophit.enter().append("li").attr("class", "tophit").attr("role", "presentation").append("a");
        tophit.select("a")        
          .attr("href", prop("url"))
          .text(prop("title"));

        var groups = ul.selectAll(".group").data(results.groups);
        var enteringGroups = groups.enter().append("ul").attr("class","group");
        enteringGroups.append("li");
        enteringGroups.append("ul").attr("class", "group-items");

        groups.select("li").text(function(d){return d.title;});

        groups.exit().remove();

        var items = groups.select("ul").selectAll("li").data(function(d){return d.objects;});
        items.enter().append("li").attr("class", "group-item").attr("role", "presentation")
           .append("a");

        items.select("a")
          .attr("href", prop("url"))
          .text(prop("title"));

        items.exit().remove();


      });

    });



  };

})(demokratikollen);