function setdata(callback){
          $.ajax({
            url: "/stars/mapper/",
            dataType: "json",
            success: function(data){
                $("#wrapper").fadeOut( "fast" );
                $("#map").show();
                callback(data);
            }
          })
      }

function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 53.346880, lng: -6.265615},
        zoom: 13,
        styles: [
            {
                "featureType": "administrative",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#444444"
                    }
                ]
            },
            {
                "featureType": "landscape",
                "elementType": "all",
                "stylers": [
                    {
                        "color": "#f2f2f2"
                    }
                ]
            },
            {
                "featureType": "poi",
                "elementType": "all",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            },
            {
                "featureType": "road",
                "elementType": "all",
                "stylers": [
                    {
                        "saturation": -100
                    },
                    {
                        "lightness": 45
                    }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "all",
                "stylers": [
                    {
                        "visibility": "simplified"
                    }
                ]
            },
            {
                "featureType": "road.arterial",
                "elementType": "labels.icon",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            },
            {
                "featureType": "transit",
                "elementType": "all",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            },
            {
                "featureType": "water",
                "elementType": "all",
                "stylers": [
                    {
                        "color": "#46bcec"
                    },
                    {
                        "visibility": "on"
                    }
                ]
            }
        ]
    });
    setdata(function(data){allfunction(map, data);});
}

function allfunction(map, shape_json){

    var shape_data = shape_json;

    for (var j = 0; j<Object.keys(shape_data).length; j++)
    {
        var carPathlist = new google.maps.MVCArray();
        drawShape(map, carPathlist, Object.values(shape_data)[j])
    }
}

var drawShape = function(map, carPath, shapeInfo) {
            var shape = new google.maps.Polyline({
                strokeColor: '#58cd66',
                strokeOpacity: 1.0,
                strokeWeight: 2,
            });

            marker_position = shapeInfo["position"]
            each_shape = shapeInfo["shapeList"]

            for (var i = 0; i < each_shape.length; i++) {
                if (i === 0) {
                    carPath.push(new google.maps.LatLng(each_shape[i]["shape_pt_lat"], each_shape[i]["shape_pt_lon"]));
                    shape.setPath(carPath);
                } else {
                    for(var j = 0; j < marker_position.length; j++){
                         if (each_shape[i]["shape_dist_traveled"] <= Object.values(marker_position[j])[0][1] && Object.values(marker_position[j])[0][1] < each_shape[i]["next_shape_dist"]){
                             var ratio = (Object.values(marker_position[j])[0][1]-each_shape[i]["shape_dist_traveled"])/ (each_shape[i]["next_shape_dist"] - each_shape[i]["shape_dist_traveled"]);
                             var leg = each_shape.slice(i);
                             var myLatLng = getPointBetween(each_shape[i],each_shape[i+1], ratio);

                            var template = [
                                '<?xml version="1.0"?>',
                                    '<svg width="26px" height="26px" viewBox="0 0 100 100" version="1.1" xmlns="http://www.w3.org/2000/svg">',
                                        '<circle stroke="#FAE008" fill="none" stroke-width="10" cx="50" cy="50" r="35"/>',
                                         '<text text-anchor="middle" style="font: bold 40px sans-serif;" x="50" y="60" fill="#FF236B">{{ line }}</text>',
                                    '</svg>'
                                ].join('\n');
                            var svg = template.replace('{{ line }}', Object.values(marker_position[j])[0][0]);

                             var icon = {
                                        url: 'data:image/svg+xml;charset=UTF-8;base64,' + btoa(svg),
                                        anchor: new google.maps.Point(15,15),
                                        scaledSize: new google.maps.Size(30,30),
                             }

                             var marker = new google.maps.Marker({
                                  position: myLatLng,
                                  title: Object.values(marker_position[j])[0][0],
                                  id: Object.keys(marker_position[j])[0],
                                  icon: icon,
                                 });
                             marker.setMap(map);
                             google.maps.event.addListener(marker, 'click',function(){callback(marker);} );
                             function callback(marker){
                                   // do something with this marker ..
                                   marker.setTitle('I am clicked');
                                   $('.navbar').show();
                                   $('#map').css('height',"63%");
                                   $('#detailed_info').show();
                                   $('.navbar-dark .navbar-toggler-icon').css('background-image','url("' + "data:image/svg+xml;charset=utf8,%3Csvg viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath stroke='rgba(0,0,0, 0.7)' stroke-width='2' stroke-linecap='round' stroke-miterlimit='10' d='M4 8h24M4 16h24M4 24h24'/%3E%3C/svg%3E" + '")');
                                   $.ajax({
                                        url: '/stars/trip_info/',
                                        data: {
                                          'id': marker.id,
                                            'pos': marker.position.toString(),
                                        },
                                        success: function(data) {
                                             $('#detailed_info').html(data);
                                             if ($(window).width() < 768) {
                                                 $(".lineInfo").css("width", "100%");
                                             }else{
                                                 var count = $(".lineInfo").children().length * 60 + 60;
                                                 $(".lineInfo").css('width', count+"px");
                                             };
                                        }
                                    });
                                };
                             startRouteAnimation(marker,ratio,leg);
                         }
                         // marker_position.remove(marker_position[j]);
                    }

                    setTimeout((function (LatLng) {
                        return function () {
                            carPath.push(LatLng);
                        };
                    })(new google.maps.LatLng(each_shape[i]["shape_pt_lat"], each_shape[i]["shape_pt_lon"])), 50 * i);
                }
                shape.setMap(map);


            };
            function showStopsInfo(lat,lon){
                return marker = new google.maps.Marker({
                    position: new google.maps.LatLng(lat,lon),
                    title: "Stop",
                 });
            };
            function setMapOnAll(markers){
                for(var i =0; i<markers.length; i++){
                    markers[i].setMap(map);
                }
            }
            function clearMarkers(markers){
                for(var j = 0; j<markers.length; j++){
                    markers[j].setMap(null);
                    console.log("!!!!")

                }
                console.log("Are they null now? ")
                console.log(markers);
            }


    }


// helper method to calculate a point between A and B at some ratio
function getPointBetween(a, b, ratio) {
    // console.log(parseFloat(a["shape_pt_lat"]) + (parseFloat(b["shape_pt_lat"]) - parseFloat(a["shape_pt_lat"])) * ratio)
    return new google.maps.LatLng(parseFloat(a["shape_pt_lat"]) + (parseFloat(b["shape_pt_lat"]) - parseFloat(a["shape_pt_lat"])) * ratio, parseFloat(a["shape_pt_lon"]) + (parseFloat(b["shape_pt_lon"]) - parseFloat(a["shape_pt_lon"])) * ratio);
}

function startRouteAnimation(marker, ratio, leg) {

    var speed = 0.01;

    var autoDriveSteps = new Array();

    var offset = 0;

    while (ratio <= 1) {
        var nextStopLatLng = getPointBetween(leg[offset], leg[offset + 1], ratio);
        autoDriveSteps.push(nextStopLatLng);
        ratio += speed;
    }


    var autoDriveTimer = setInterval(function () {
            // stop the timer if the route is finished
            if (autoDriveSteps.length === 0) {
                // clearInterval(autoDriveTimer);
                ratio = 0;
                offset += 1;
                while (ratio <= 1 && offset < leg.length - 1) {
                    nextStopLatLng = getPointBetween(leg[offset], leg[offset + 1], ratio);
                    autoDriveSteps.push(nextStopLatLng);
                    ratio += speed;
                }
            } else {
                // move marker to the next position (always the first in the array)
                marker.setPosition(autoDriveSteps[0]);
                // remove the processed position
                autoDriveSteps.shift();
            }
        }, 100);
}


