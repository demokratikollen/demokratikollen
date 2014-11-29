Search = {
  Setup: function() {
    var getBloodhound = function(url) {
      return new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('tokens'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
          url: url,
          filter: function(obj) {
            return obj.d;
          }
        }
      });
    }

    var members = getBloodhound('/data/members_search.json');
    members.initialize();

    var parties = getBloodhound('/data/parties_search.json');
    parties.initialize();

    var groups = getBloodhound('/data/groups_search.json');
    groups.initialize();


    $('#main-search input').typeahead(null,
    {
      name: 'members',
      displayKey: 'fullName',
      source: members.ttAdapter(),
      templates: {
        header: '<h3 class="category-title">Organ</h3>',
        suggestion: function(d) {
          return '<p>'+d.fullName+' ('+d.party+')</p>';
        }
      }
    },
    {
      name: 'parties',
      displayKey: 'groupName',
      source: parties.ttAdapter(),
      templates: {
        header: '<h3 class="category-title">Partier</h3>',
        suggestion: function(d) {
          return '<p>'+d.groupName+'</p>';
        }
      }
    },
    {
      name: 'groups',
      displayKey: 'gruopName',
      source: groups.ttAdapter(),
      templates: {
        header: '<h3 class="category-title">Organ</h3>',
        suggestion: function(d) {
          return '<p>'+d.groupName+'</p>';
        }
      }
    }).on('typeahead:selected', function (obj, datum) {
      $('#test').html(datum.full_name);
    });
  }
};