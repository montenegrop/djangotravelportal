function loadVaccinationPopovers() {
    $(function () {
        $("[data-toggle=vaccine-popover]").click(function (event) {
            event.preventDefault();
        });

        $("[data-toggle=vaccine-popover]").popover({
            sanitize: false,
            html: true,
            content: function () {
                var content = $(this).attr("data-popover-content");

                return $(content).children(".popover-body").html();
            },
            title: function () {
                var title = $(this).attr("data-popover-content");
                return $(title).children(".popover-heading").html();
            }
        });
    });
}

function loadCurrencyPopover() {
    $(function () {
        $("[data-toggle=currency-popover]").click(function (event) {
            event.preventDefault();
        });

        $("[data-toggle=currency-popover]").popover({
            sanitize: false,
            html: true,
            content: function () {
                var content = $(this).attr("data-popover-content");

                return $(content).children(".popover-body").html();
            },
            title: function () {
                var title = $(this).attr("data-popover-content");
                return $(title).children(".popover-heading").html();
            },
            template: '<div class="popover exchange-table" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
        });
    });
}

function initMap() {

    var map;
    var townToggle = 0;
    var townLayer;
    var markersArray = [];

    // country:
    var lat = parseFloat(country[0]['fields']['latitude'])
    var lng = parseFloat(country[0]['fields']['longitude'])


    var notownsStyle = [{
        "stylers": [
            {"weight": 0.5}
        ]
    }, {
        "featureType": "administrative.locality",
        "elementType": "labels",
        "stylers": [
            {"visibility": "off", "weight": 1.5}
        ]
    }, {
        "featureType": "poi",
        "elementType": "labels",
        "stylers": [
            {"visibility": "off"}
        ]
    }, {
        "featureType": "administrative.country",
        "elementType": "labels",
        "stylers": [
            {"visibility": "on", "weight": 1},
            {"invert_lightness": false}
        ]
    }];

    var townsStyle = [{
        "stylers": [
            {"weight": 0.5}
        ]
    }, {
        "featureType": "poi",
        "elementType": "labels",
        "stylers": [
            {"visibility": "off"}
        ]
    }, {
        "featureType": "administrative.country",
        "elementType": "labels",
        "stylers": [
            {"visibility": "on", "weight": 1},
            {"invert_lightness": false}
        ]
    }];

    function FullScreenControl(controlDiv, map) {
        controlDiv.style.padding = '5px';

        // Set CSS for the control border
        var fullscreenUI = document.createElement('a');
        fullscreenUI.style.backgroundColor = 'white';
        fullscreenUI.style.backgroundImage = "url('//static3.yourafricansafari.com/images/icons/fullscreen.png')";
        fullscreenUI.style.borderStyle = 'solid';
        fullscreenUI.style.display = 'block';
        fullscreenUI.style.width = '24px';
        fullscreenUI.style.height = '24px';
        fullscreenUI.style.borderColor = '#cccccc';
        fullscreenUI.style.borderWidth = '1px';
        fullscreenUI.style.className += 'fullscreen';
        fullscreenUI.style.cursor = 'pointer';
        fullscreenUI.style.textAlign = 'center';
        fullscreenUI.title = 'Open a larger map';
        controlDiv.appendChild(fullscreenUI);

        google.maps.event.addDomListener(fullscreenUI, 'click', function () {
            window.location = '';
        });
    }

    function TownControl(controlDiv, map) {
        controlDiv.style.padding = '5px';

        // Set CSS for the control border
        var townControlUI = document.createElement('a');
        townControlUI.style.backgroundColor = 'white';
        townControlUI.style.backgroundImage = "url('//static3.yourafricansafari.com/images/icons/gmaps_town.png')";
        townControlUI.style.borderStyle = 'solid';
        townControlUI.style.display = 'block';
        townControlUI.style.width = '36px';
        townControlUI.style.height = '36px';
        townControlUI.style.borderColor = '#cccccc';
        townControlUI.style.borderWidth = '1px';
        townControlUI.style.className += 'fullscreen';
        townControlUI.style.cursor = 'pointer';
        townControlUI.style.textAlign = 'center';
        townControlUI.title = 'See the towns/cities';
        controlDiv.appendChild(townControlUI);

        google.maps.event.addDomListener(townControlUI, 'click', function () {
            if (townToggle == 0) {
                map.setMapTypeId('towns');
                townToggle = 1;
                this.style.backgroundColor = '#eaeaea';
            } else {
                map.setMapTypeId('no-towns');
                townToggle = 0;
                this.style.backgroundColor = '#fff';
            }
        });
    }

    function clearOverlays() {
        if (markersArray) {
            for (var i = 0; i < markersArray.length; i++) {
                markersArray[i].setMap(null);
            }
        }
    }

    function showOverlays(map) {
        if (markersArray) {
            for (var i = 0; i < markersArray.length; i++) {
                markersArray[i].setMap(map);
                markersArray[i].labelVisible = (map.getZoom() > 5);
            }
        }
    }

    function initialize() {
        /* map options */
        var mapOptions = {
            center: new google.maps.LatLng(lat, lng),
            zoom: 5,
            panControl: false,
            streetViewControl: false,
            scrollwheel: false,
            zoomControlOptions: {
                style: google.maps.ZoomControlStyle.SMALL
            },
            mapTypeControlOptions: {
                position: google.maps.ControlPosition.TOP_LEFT
            },
        };

        /* Initial the maps and style maps */
        map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);

        var notownsType = new google.maps.StyledMapType(notownsStyle, {map: map, name: 'no-towns'});
        map.mapTypes.set('no-towns', notownsType);
        map.setMapTypeId('no-towns');

        var townsType = new google.maps.StyledMapType(townsStyle, {map: map, name: 'towns'});
        map.mapTypes.set('towns', townsType);

        /* Place the custom button */

        var townDiv = document.createElement('div');
        var townControl = new TownControl(townDiv, map);
        map.controls[google.maps.ControlPosition.TOP_RIGHT].push(townDiv);

        var current_location = new google.maps.Marker({
            position: new google.maps.LatLng(lat, lng),
            map: map,
            draggable: false,
            animation: google.maps.Animation.DROP,
            label: '',
        });
        google.maps.event.addListener(current_location, 'click', function () {
            window.parent.location = '/'.concat(country['fields']['name']);
        });

        markersArray.push(current_location);

        for (var parkData of parks) {
            (function () {
                var lat = parseFloat(parkData['fields']['latitude'])
                var lng = parseFloat(parkData['fields']['longitude'])

                var park = new MarkerWithLabel({
                    position: new google.maps.LatLng(lat, lng),
                    map: map,
                    draggable: false,
                    title: parkData['fields']['name'],
                    icon: '/static/places/images/gmap_tree.png',
                    labelAnchor: new google.maps.Point(50, -2),
                    labelContent: '<nobr>'.concat(parkData['fields']['name'], '<nobr>'),
                    labelInBackground: true,
                    labelClass: "gmaps_label gm_position_bottom",
                    labelVisible: true,
                });

                google.maps.event.addListener(park, 'click', function () {
                    window.parent.location = '/parks/'.concat(parkData['fields']['slug']);
                });
                markersArray.push(park);

            })()


        }

        google.maps.event.addListener(map, 'zoom_changed', function () {
            showOverlays(map);
        });

        showOverlays(map);
    }

    $(document).bind('webkitfullscreenchange mozfullscreenchange fullscreenchange', function () {
        var isFullScreen = document.fullScreen ||
            document.mozFullScreen ||
            document.webkitIsFullScreen;
        if (isFullScreen) {
            map.setCenter({lat: lat, lng: lng});
        } else {
            map.setCenter({lat: lat, lng: lng});
        }
    })

    google.maps.event.addDomListener(window, 'load', initialize);

}