/* global document, window, fetch, cytoscape */

(function(){
  var toJson = function(res){ return res.json(); };

  window.cy = cytoscape({
    container: document.getElementById('cy'),

    layout: {
      name: 'grid'
    },

    style: fetch('static/js/cy-style.json').then(toJson),

    elements: fetch('static/js/data.json').then(toJson)
  });
})();