var mapData = worldmap;

$('#worldMap').vectorMap({
  map: 'world_mill_en',
  zoomButtons : false,
  backgroundColor: "transparent",
  regionStyle: {
    initial: {
      fill: '#e4e4e4',
      "fill-opacity": 0.9,
      stroke: 'none',
      "stroke-width": 0,
      "stroke-opacity": 0
    }
  },

  series: {
    regions: [{
      values: mapData,
      scale: ["#AAAAAA", "#444444"],
      normalizeFunction: 'polynomial'
    }]
  },
})