demokratikollen = {};
demokratikollen.utils = {};
demokratikollen.graphics = {};

// global utils (aka danger zone)

function prop(p) {
  return function(d) {
    return d[p];
  };
}

function compose(f,g) {
  return function(d) {
    return f(g(d));
  };
}

//Enable touch hover on links
$('a.taphover').on("touchstart", function (e)
{
	'use strict'; //satisfy code inspectors
    var link = $(this); //preselect the link
    if (link.hasClass('hover')) {
    	return true;
    } else {
    	link.addClass('hover');
    	$('a.taphover').not(this).removeClass('hover');
    	e.preventDefault();
    	return false; //extra, and to make sure the function has consistent return points
    }
});