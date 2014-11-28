Search = {
  Setup: function() {
    var members = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('full_name'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      prefetch: {
        url: "/data/members_search.json",
        filter: function(obj) {
          return obj.d;
        }
      }
    });

    members.initialize();


    $('#main-search input').typeahead(null,{
        name: 'members',
        displayKey: 'full_name',
        source: members.ttAdapter(),
        templates: {
          empty: [
            '<div class="empty-message">',
            'Hittade inga ledamöter.',
            '</div>'
          ].join('\n'),
          suggestion: function(d) {
            return '<p>'+d.full_name+' ('+d.party+')</p>';
          }
        }
    }).on('typeahead:selected', function (obj, datum) {
        $('#test').html(datum.full_name);
    });
  }
};