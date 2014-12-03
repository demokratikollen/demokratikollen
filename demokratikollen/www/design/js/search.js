Search = {
  Setup: function() {
    var f;
    $.getJSON( "/parliament/members_search.json", function( data ) {
      f = new Fuse(data.d, {keys: ['fullName','party'], threshold:0.2});
    });


    $('#main-search input').typeahead({hint:false,minLength:2},{
        name: 'members',
        displayKey: 'fullName',
        source: function(query,cb) {
          setTimeout(function(){cb(f.search(query));},0);
        },
        templates: {
          empty: [
            '<div class="empty-message">',
            'Hittade inga ledamöter.',
            '</div>'
          ].join('\n'),
          suggestion: function(d) {
            return '<p>'+d.fullName+' <small>('+d.party+')</small></p>';
        }
    }).on('typeahead:selected', function (obj, datum) {
        $('#test').html(datum.fullName);
    });
  }
};