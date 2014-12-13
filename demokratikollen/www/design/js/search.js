Search = {
  Setup: function() {
    $('#main-search input').on('focusin',function (event) { 
      $('#main-search').addClass('open'); 
    });
    $('#main-search input').on('focusout',function (event) { 
      $('#main-search').removeClass('open'); 
    });

    var searchCfg = {
      minChars: 2
    }

    var f;
    $.getJSON( "/data/parliament/members_search.json", function( data ) {
      f = new Fuse(data.d, {keys: ['fullName','party','groups'], threshold:0.6});
    });

    $('#main-search input').on('input',function (e) {
      if (e.target.value.length >= searchCfg.minChars) {
        console.log(e);
        $('#main-search .dropdown-menu').addClass('open');
        $('#test').html(e.target.value);
      }      
    });
  }
};