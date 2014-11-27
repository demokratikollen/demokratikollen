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
        displayKey: function(m) {
          return m.full_name + ' (' + m.party + ')';
        },
        source: members.ttAdapter()
    }).on('typeahead:selected', function (obj, datum) {
        $('#test').html(datum.full_name);
    });
  }
};