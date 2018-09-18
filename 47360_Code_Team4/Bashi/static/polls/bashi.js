// Function for Landing page to Results page tranistion
$(document).ready(
    function(){
        $('#map').hide();
        $('#detailed_info').hide();
        $('#time_input').hide()
	//Second Page
        $("#search").submit(function(e){
             e.preventDefault();
	     document.getElementById("weatherdark").style.display = "none";
             document.getElementById("weatherlight").style.display = "block";
	     $('#first_searchbar').hide();
	     $('.fixed-navbar').show();
	     $('.navbar').css('background-color','whitesmoke');
             $('.navbar-dark .navbar-nav .nav-link').css('color','black'); 
             $('.navbar-dark .navbar-brand').css('color','black');
             $('.navbar-dark .navbar-brand:hover').css('color','#04b5ff');
             $('.navbar-dark .navbar-toggler-icon').css('background-image','url("' + "data:image/svg+xml;charset=utf8,%3Csvg viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath stroke='rgba(0,0,0, 0.7)' stroke-width='2' stroke-linecap='round' stroke-miterlimit='10' d='M4 8h24M4 16h24M4 24h24'/%3E%3C/svg%3E" + '")');
             $('.navbar-dark .navbar-nav .active>.nav-link, .navbar-dark .navbar-nav .nav-link.active, .navbar-dark .navbar-nav .nav-link.show, .navbar-dark .navbar-nav .show>.nav-link').css('color','#04b5ff');
             $('.navbar-dark .navbar-nav .nav-link').hover(function(){
		$(this).css('color','#04b5ff');
		}).mouseout(function(){
			$(this).css('color','black');
		});
	     $('#bg').hide();
             $('.m-b-1').hide();
             $('#map').show();
             $('#detailed_info').show();
             $("input[type=text]").css("font-size","16px");
            var img1=document.getElementById("image1");
            img1.src = "/static/polls/black-tp.png";
            var start = $('#departure_input');
            var end = $('#destination_input');
            var start_flag = start.attr("data-place");
            var end_flag = end.attr("data-place");
            var start_2 =$('#departure_input_2');
            var end_2=$('#destination_input_2');
            start_2.attr("data-place", start_flag);
            end_2.attr("data-place", end_flag);
            start_2.val(start.val());
            end_2.val(end.val());
            start_2.attr("data-id", start.attr("data-id"));
            end_2.attr("data-id", end.attr("data-id"));
            var startPromise = filterflag(start_flag, start);
            var endPromise = filterflag(end_flag, end);
            Promise.all([startPromise, endPromise]).then(getDirection).then(data => drawRoute(data,"timeDate")).then(function(){
                $('#first_searchbar').hide();
                autocomplete(document.getElementById("departure_input_2"), autoCompleteOptions);
                autocomplete(document.getElementById("destination_input_2"), autoCompleteOptions);
                jQuery('#timeDate_2').datetimepicker({
                  allowTimes:['00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30',
                              '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
                              '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30'
             ],
                  minDate:'-1970/01/01',//yesterday is minimum date(for today use 0 or -1970/01/01)
                  maxDate:'+1970/01/05'
                });
            });
        });
        $("#search_2").submit(function(e){
            e.preventDefault();
            var start = $('#departure_input_2');
            var end = $('#destination_input_2');
            var start_flag = start.attr("data-place");
            var end_flag = end.attr("data-place");
            var startPromise = filterflag(start_flag, start);
            var endPromise = filterflag(end_flag, end);
            Promise.all([startPromise, endPromise]).then(getDirection).then(data => drawRoute(data,"timeDate_2")).then(function(){
                autocomplete(document.getElementById("departure_input_2"), autoCompleteOptions);
                autocomplete(document.getElementById("destination_input_2"), autoCompleteOptions);
            });
        });
        $("#exchange").click(function(){
            var departure = $("#departure_input");
            var destination = $('#destination_input');
            var medium = departure.val();
            departure.val(destination.val());
            destination.val( medium );
            var marker_medium = departure.attr("data-place");
            departure.attr("data-place", destination.attr("data-place"));
            destination.attr("data-place",marker_medium);
            var id_medium = departure.attr("data-id");
            departure.attr("data-id", destination.attr("data-id"));
            destination.attr("data-id",id_medium);
        });
        $("#exchange_2").click(function(){
            
            var departure = $("#departure_input_2");
            var destination = $('#destination_input_2');
            var medium = departure.val();
            departure.val(destination.val());
            destination.val( medium );
            var marker_medium = departure.attr("data-place");
            departure.attr("data-place", destination.attr("data-place"));
            destination.attr("data-place",marker_medium);
            var id_medium = departure.attr("data-id");
            departure.attr("data-id", destination.attr("data-id"));
            destination.attr("data-id",id_medium);
        });

        $('#change_time').click(
            function(){
                $('#time_input').show();
                $(this).find("span").hide()

            }
        )
    }
)

//Fucntion to Create Search Bar

var findGooglePosition = function (inp){
    return new Promise(function(resolve, reject){
        var placeid = inp.attr("data-id");
        if ( placeid !== '') {
            resolve({placeId: placeid});
        }else {
            reject(error("Can not find the position of address"));
        }});
};

var findDictPosition = function (address){
    return new Promise(function(resolve, reject){
        var selectedOption = autoCompleteDict.find(x => x.key === address);
        if(selectedOption){
            resolve( selectedOption.value )
        }else{
            reject(Error("Can not find the position on Dict"))
        }
    })
};

var findPossiblePosition = function(address,arr){
    var found = 0
    for( var i = 0; i<arr.length; i++){
    var matchIndexInDict = arr[i].toUpperCase().search(address.toUpperCase());
    if ( matchIndexInDict > -1){
        found = 1;
        
        return arr[i];
    }};
    return new Promise(function(resolve, reject){
        var service = new google.maps.places.AutocompleteService();
        
        service.getPlacePredictions({ input: address , componentRestrictions: {country: 'ie'}}, function(results,status){
            if (status != google.maps.places.PlacesServiceStatus.OK ) {
                reject(alert("Can not find your input address in Ireland"));
            }else{
                
                resolve({placeId: results[0]["place_id"]});
            };
        });
    });
}

function filterflag(flag,inp){
    var value = inp.val();
    
    if (flag == "stop"){
        return findDictPosition(value);
    }else if(flag == "google"){
        return findGooglePosition(inp);
    }else{
        return findPossiblePosition(value, autoCompleteOptions);
    };
};

$("#search").submit(function(e){
    return false;
});

$("#input_submit").click(
    function() {
        var start = $('#departure_input');
        var end = $('#destination_input')
        var start_flag = start.attr("data-place");
        var end_flag = end.attr("data-place");
        var startPromise = filterflag(start_flag, start);
        var endPromise = filterflag(end_flag, end);
        Promise.all([startPromise, endPromise]).then(getDirection).then(drawRoute);
    });


var getDirection = function(ArrPosition){
    var request = {
        origin: ArrPosition[0],
        destination: ArrPosition[1],
        provideRouteAlternatives: true,
        travelMode: 'TRANSIT',
        transitOptions: {
            modes: ['BUS'],
            routingPreference: 'FEWER_TRANSFERS'
        }
    };
    
    return  new Promise(function(resolve, reject){
        var directionsService = new google.maps.DirectionsService();
        directionsService.route(request, function (response, status){
            if (status == google.maps.DirectionsStatus.OK) {
                 resolve(response);
            }else{
                reject(error("Direction services are not available."));
            }
        });
    })

}

$("#exchange").click(function(){
        
        var departure = $("#departure_input");
        var destination = $('#destination_input');
        var medium = departure.val();
        departure.val(destination.val());
        destination.val( medium );
        var marker_medium = departure.attr("data-place");
        departure.attr("data-place", destination.attr("data-place"));
        destination.attr("data-place",marker_medium);
        var id_medium = departure.attr("data-id");
        departure.attr("data-id", destination.attr("data-id"));
        destination.attr("data-id",id_medium);
    });

function autocomplete(inp,arr){

    var currentFocus;
    inp.addEventListener("keyup", function(event){
        var KeyID = event.which;
        
        if(KeyID == 8 || KeyID == 46){
            console.log("delete");
            inp.setAttribute("data-place","");
            inp.setAttribute("data-id","");
        }
        var a,b,i,val = this.value;
        
        closeAllLists();
        if(!val) {return false;}
        currentFocus = -1;

        a = document.createElement("DIV");
        a.setAttribute("id",this.id + "autocomplete=list");
        a.setAttribute("class","autocomplete-items");

        this.parentNode.appendChild(a);
        var  numberofmatch = 0;
        for(i = 0; i<arr.length; i++){
            var matchIndex = arr[i].toUpperCase().search(val.toUpperCase());
            if(( matchIndex > -1 ) && ( numberofmatch < 2 )){
                var b = document.createElement("DIV");
                b.innerHTML ='<i class="fas fa-bus"></i>  Stop  ';
                b.innerHTML += arr[i].substr(0,matchIndex);
                b.innerHTML +="<strong>" + arr[i].substr(matchIndex,val.length) + "</strong>";
                b.innerHTML += arr[i].substr(matchIndex + val.length);
                b.innerHTML += '<input type="hidden" value ="' + arr[i] + '">';
                b.addEventListener("click", function(e){
                    inp.value =  this.getElementsByTagName("input")[0].value;
                    
                    closeAllLists();
                    $(inp).attr("data-place","stop");
                });
                a.appendChild(b);
                numberofmatch += 1;
            }
        }

        // Function to create a new div element

        var displaySuggestions = function(predictions, status) {
            if (status != google.maps.places.PlacesServiceStatus.OK) {
                // alert(status);
                return;
            }
	    var predictionSplit = predictions.slice(0,1);
            predictionSplit.forEach(function(prediction) {
                var b = document.createElement("DIV");
                b.innerHTML += "<i class=\"fas fa-search\"></i>  ";
                b.innerHTML += prediction.description;
                b.innerHTML += '<input type="hidden" value ="' + prediction.description + '">';
                b.addEventListener("click", function(e){
                    var selected = this.getElementsByTagName("input")[0].value;
                    inp.value = selected;
                    closeAllLists();
                    var filtered = predictions.filter ( o => o["description"] === selected);
                    $(inp).attr("data-place","google");
                    $(inp).attr("data-id",filtered[0]["place_id"]);
                });
                a.appendChild(b);
            });
        }
        // Send request for Google autocomplete service and get possible result
        var service = new google.maps.places.AutocompleteService();

        service.getPlacePredictions({ input: val, componentRestrictions: {country: 'ie'}}, displaySuggestions);


    });

    inp.addEventListener("keydown",function(e){
        var x = document.getElementById(this.id + "autocomplete-list");
        if(x) x = x.getElementsByTagName("div");
        if(e.keycode == 40){
            currentFocus++;
            addActive(x);
        }else if(e.keycode == 38){
            currentFocus--;
            addActive(x);
        }else if(e.keycode == 13){
            e.preventDefault()
            if (currentFocus > -1) {
                if (x) x[currentFocus].click();
            }
        }
    });


    /* Function to classify an item as "active" */
    function addActive(x) {
        if (!x) return false;
        /* Start by removing the "active" class on all items */
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /* Add class "autocomplete-active" */
        x[currentFocus].classList.add("autocomplete-active");
    };

    function removeActive(x){
        for (var i = 0; i<x.length; i++){
            x[i].classList.remove("autocomplete-activate");
        }
    };

    /* Close all autocomplete lists in the document
        except the one passed as an argument: */
    function closeAllLists(elmnt) {
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
          if (elmnt != x[i] && elmnt != inp) {
          x[i].parentNode.removeChild(x[i]);
        }
      }
    };

    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}










// Create the dropdowns from the stopData dictionary, value being latlng 
var stations = [];
var stationIDs = [];    

// MAP
// Create the map centered on Dublin 
var dublin = {lat: 53.346880, lng: -6.265615};
var map; 
 
// Array to hold a dictionary for each route option and information for each route
var journeyLatLng = [];
 
var currentLocation = [];
   
function initMap() {

    var infoWindow = new google.maps.InfoWindow;


    if (navigator.geolocation){
        navigator.geolocation.getCurrentPosition(function(position) {
        pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
//        infoWindow.setPosition(pos);
//        infoWindow.setContent('Current Location');
//        infoWindow.open(map);
        map.setCenter(pos);
        var geocoder = new google.maps.Geocoder;
        geocoder.geocode({
            location: pos,}, function(result,status){
            if(status === 'OK'){
                if (result[0]){
                    
                    $('#departure_input').val(result[0].formatted_address);
                    $('#departure_input').attr("data-id", result[0].place_id);
                    $('#departure_input').attr("data-place", 'google');
                    $('#departure_input').one("click", function (){$(this).select();});
                }else{
                    alert('No results found');
                }
            }
        });
        }, function() {
            handleLocationError(true, infoWindow, map.getCenter());
        });
    }else{
          // Browser doesn't support Geolocation
          handleLocationError(false, infoWindow, map.getCenter());
    }
    

    var directionsService = new google.maps.DirectionsService();
    var directionsDisplay = new google.maps.DirectionsRenderer();
    var myOptions = {
        zoom: 13,
        center: dublin,
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
    }

    map = new google.maps.Map(document.getElementById("map"), myOptions);
    directionsDisplay.setMap(map);


  
    
}

    
function handleLocationError(browserHasGeolocation, infoWindow, currentLocation) {
    infoWindow.setPosition(currentLocation);
    infoWindow.setContent(browserHasGeolocation ?                          'Error: The Geolocation service failed.' :
                          'Error: Your browser doesn\'t support geolocation.');
    infoWindow.open(map);
}
        


//Routes is an array to hold the directions renderer objects
var routes = [];
 
//Global varibable to track which route is active on the map
var activeRoute = 0;

 
var drawRoute = function(GoogleResponse,timeDate){
    var colours = ['red', 'green', 'blue', 'orange', 'purple', 'black'];
    // If routes is not empty, reset it to empty as a new request with new route options has been made
    if (routes.length > 0){
    routes[activeRoute].setMap(null);
    routes = [];
    activeRoute = 0;
}
    


    var totalLines = [];
    var routesIncluded = [];
    var journeyLatLng = [];
    var allInfo = "";
    
    for (var i = 0; i < GoogleResponse.routes.length; i++) {
       	
	// Boolean to check if there are any buses that are not run by Dublin Bus
        var notDublinBus = false;
	
	 var routesDD ="";
        // i = different route options

        // routesDD will be used to send the buttons to the html
               // console.log(routesDD);
        var lines = "";


        //put each route object in an array, set to null until their button is clicked
        routes.push( new google.maps.DirectionsRenderer({
            map: null,
            directions: GoogleResponse,
            routeIndex: i,
            polylineOptions: {
                strokeColor: colours[i],
                strokeWeight: 4,
                strokeOpacity: 1
            }
        })
    );

    
        // Array to hold dictionaries for the lat lng of the start and end bus stops along a single route, or the walk time
        // The key will be the mode of transport
        var routeLatLng = [];

        routesDD += '<div class="routesHolder col-sm-1 bg-warning" id= "button_'+ i +'"><span></span>';
	routesDD += '<div class = "timePreview" id = "timePreview_'+ i +'" style = "font-size:2vw;cursor: pointer;position: absolute;transform: rotate(-90deg); transform-origin: 35% 220%;width: 300%;text-align: left;"><img style="width: 22px; height: 22px;" id="svg-spinner" src="/static/polls/svg-spinner.svg" /> mins</div>';
        routesDD += '<div class = "holder" id = "holder_'+ i +'">';

        var routeLength = GoogleResponse.routes[i].legs[0].steps.length;
        routeWidth = String(Math.round(100/routeLength) - 3);
        routeWidth = routeWidth + "%";


        for (var j = 0; j < GoogleResponse.routes[i].legs[0].steps.length; j++) {
             // j = the different legs in a route
            var routeLength = GoogleResponse.routes[i].legs[0].steps.length -1;

            var travelMode = GoogleResponse.routes[i].legs[0].steps[j].travel_mode;

            if (j > 0){
                var travelModePrevious = GoogleResponse.routes[i].legs[0].steps[j-1].travel_mode;
            }


         if (travelMode == "TRANSIT"){

                // Check if the carrier is dublin bus, if not, dont include the route option
                var busCarrier = GoogleResponse.routes[i].legs[0].steps[j].transit.line.agencies[0].name;
                if (busCarrier != "Dublin Bus"){
                    notDublinBus = true;
                    break;
                }
	
		var busLine = " " + GoogleResponse.routes[i].legs[0].steps[j].transit.line.short_name ; //e.g. 145
                lines += busLine
                var departureLat = GoogleResponse.routes[i].legs[0].steps[j].transit.departure_stop.location.lat();
                var departureLng = GoogleResponse.routes[i].legs[0].steps[j].transit.departure_stop.location.lng();
                var departureLatLng = [departureLat, departureLng];
		
		        var instructionsBus = GoogleResponse.routes[i].legs[0].steps[j].instructions;

                var arrivalLat = GoogleResponse.routes[i].legs[0].steps[j].transit.arrival_stop.location.lat();
                var arrivalLng = GoogleResponse.routes[i].legs[0].steps[j].transit.arrival_stop.location.lng();
                var arrivalLatLng = [arrivalLat, arrivalLng];

                var headSign = GoogleResponse.routes[i].legs[0].steps[j].transit.headsign;
                
             if ( j == 0 ){
                routesDD += '<div id="journeyInfo"><div id="journey_'+i+'" class ="journeyTime"><img style="width: 22px; height: 22px;" id="svg-spinner" src="/static/polls/svg-spinner.svg" /> mins</div><div class = "journeyLineID" id="journeyLine_'+i+'"></div></div><div id="journeyDetail">';
            }

             //if previous travel was bus, dont add stop at the start
             if (travelModePrevious != 'TRANSIT'){ 
                routesDD += '<div id = "stopDiv"><div id="Pic"><img src = "/static/polls/bus_stop.png" height="100%"></div><div id="stopLineBus"></div></div>';
             }
             if ((routeLength+1) <= 3){
             //add the bus line
             routesDD += '<div id = "travelDiv" style="width:'+routeWidth+';"><div id="Pic" href="#" data-trigger="hover" data-placement="top" data-content="'+instructionsBus+'"><i class="fas fa-bus-alt"></i></div><div id="lineBus"></div><div id = "leg_'+i+j+'" class="Time"></div><div id ="wait_'+i+j+'" class="wait"></div><div id = "bustime_'+i+j+'" class="bustimes"></div></div>';
             }
             if ((routeLength+1) == 4){
             //add the bus line
             routesDD += '<div id = "travelDiv" style="width:'+routeWidth+';"><div id="Pic" href="#" data-trigger="hover" data-placement="top" data-content="'+instructionsBus+'"><i class="fas fa-bus-alt"></i></div><div id="lineBus"></div><div style="font-size:1.8vw" id = "leg_'+i+j+'" class="Time"></div><div id ="wait_'+i+j+'" class="wait" style="font-size:1.1vw"></div><div id = "bustime_'+i+j+'" class="bustimes"></div></div>';
             }
             if ((routeLength+1) >= 5){
             //add the bus line
             routesDD += '<div id = "travelDiv" style="width:'+routeWidth+';"><div id="Pic" href="#" data-trigger="hover" data-placement="top" data-content="'+instructionsBus+'"><i class="fas fa-bus-alt"></i></div><div id="lineBus"></div><div style="font-size:1.2vw" id = "leg_'+i+j+'" class="Time"></div><div id ="wait_'+i+j+'" class="wait" style="font-size:0.78vw"></div><div id = "bustime_'+i+j+'" class="bustimes"></div></div>';
             }

            routesDD += '<div id = "stopDiv"><div id="Pic"><img src = "/static/polls/bus_stop.png" height="100%"></div><div id="stopLineBus"></div></div>';

                routeLatLng.push({
                    key: travelMode,
                    value: [departureLatLng, arrivalLatLng, busLine, headSign]
                });
                
            }

        if (travelMode == "WALKING"){
            var instructionsWalk = GoogleResponse.routes[i].legs[0].steps[j].instructions;
            var walkTime = GoogleResponse.routes[i].legs[0].steps[j].duration.text;
                    
            if (j ==0){
                routesDD += '<div id="journeyInfo" class="raw pt-1"><div id="journey_'+i+'" class="col-sm-5 aligh-right journeyTime"><img style="width: 22px; height: 22px;" id="svg-spinner" src="/static/polls/svg-spinner.svg" /> mins</div><div class = "col-sm-6 journeyLineID text-info align-right" id="journeyLine_'+i+'"></div></div><div id="journeyDetail" class="d-none">';
            }            
	     if ((routeLength+1) <= 3){
                 routesDD+= '<div id = "travelDiv" style="width:'+routeWidth+';"> <div id="Pic" href="#" data-trigger="hover" data-placement="top" data-content="'+instructionsWalk+'" ><i class="fas fa-walking"></i></div><div id="lineWalk"></div> <div id = "leg_'+i+j+'" class="Time"></div></div>';
             }
             if ((routeLength+1) == 4){
                 routesDD+= '<div id = "travelDiv" style="width:'+routeWidth+';"> <div id="Pic" href="#" data-trigger="hover" data-placement="top" data-content="'+instructionsWalk+'" ><i class="fas fa-walking"></i></div><div id="lineWalk"></div> <div style="font-size:1.8vw" id = "leg_'+i+j+'" class="Time"></div></div>';
             }
             if ((routeLength+1) >= 5){
                  routesDD+= '<div id = "travelDiv" style="width:'+routeWidth+';"> <div id="Pic" href="#" data-trigger="hover" data-placement="top" data-content="'+instructionsWalk+'" ><i class="fas fa-walking"></i></div><div id="lineWalk"></div> <div style="font-size:1.2vw" id = "leg_'+i+j+'" class="Time"></div></div>';
             }

            routeLatLng.push({
                    'key': travelMode,
                    'value': walkTime
                });
            }
        //j loop ends        
        }

    if (totalLines.includes(lines))
    {
        
        continue;
    } 
    else if (notDublinBus)
    {
        
        continue; 
    }
    else
    {  
    
    totalLines.push(lines);
    
    
    routesIncluded.push(i);
    
    journeyLatLng.push(routeLatLng);
    allInfo += routesDD;
    allInfo += '</div></div></div>';
    }
    //i loop ends    
    }

    //if there is no routes to show i.e. all are not dublin bus, show on html
    if (routesIncluded.length == 0){
        allInfo = "<div style = 'margin: auto;color: whitesmoke;'>There are no Dublin Bus services on this route :-(</div>";        
    }
    document.getElementById('routesTest').innerHTML = allInfo;

    var divSize = String(4 - routesIncluded.length + 9);
    
    if (routesIncluded.length == 1){
        $(".routesHolder:last-child > span").css("background-color","transparent");
    }

    for (var i = 0; i < routesIncluded.length; i++) {
        document.getElementById('journeyLine_'+routesIncluded[i]).innerHTML = totalLines[i];
        document.getElementById("timePreview_0").style.display = "none";
        if (i>0){
            document.getElementById('holder_'+routesIncluded[i]).style.display = "none";
        }
    }
    console.log("yyy", journeyLatLng);
    var timeRequest = document.getElementById(timeDate).value;
    if (timeRequest == ""){
	timeRequest = "Now";
    }
    
    if (timeRequest == 'Now'){
        timeRequest = +new Date();
    }else{
        timeRequest = String(Date.parse(timeRequest));
        
    }
    
    $.ajax({
      url: "/AJAX",
      type: "POST",
      dataType: "json",
      data: {
          routesDict: JSON.stringify(journeyLatLng),
          timestamp: timeRequest,
          csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),
      },
 success: function (response) {        
          
          
      for (var i = 0; i < response.length; i++) {
	
      //i is the route option

            // if the response isnt empty:                    
                var total = 0;

                for (var j = 0; j < response[i].length; j++){
			 
                    // j is each leg on a route
                    if (response[i][j]['error_code'] == 0){
                    var wait = 0;
                    
			
			if (response[i][j]['key'] == "TRANSIT"){
                       
                        var leg = response[i][j]['value'][0][0];
			
                        if (leg < 0){
                          var leg = Math.round(GoogleResponse.routes[i].legs[0].steps[j].duration.value/60);
                         
                        }
                        wait += response[i][j]['value'][0][1];
                        var busTimes = response[i][j]['value'][1];
                        document.getElementById('bustime_'+routesIncluded[i]+j).innerHTML = busTimes;
                        var waitTime = 'Wait: ' + String(wait) +' mins';
                        
                        document.getElementById('wait_'+routesIncluded[i]+j).innerHTML = waitTime;
                        document.getElementById('wait_'+routesIncluded[i]+j).style.borderLeft = 'solid blue';
                        document.getElementById('bustime_'+routesIncluded[i]+j).style.borderLeft = 'solid blue';
                        document.getElementById('leg_'+routesIncluded[i]+j).style.borderLeft = 'solid blue';
                    }

                        

		   else{
                         var leg = response[i][j]['value'];
                        
                    }
                    total += wait;
                    total += leg;
                    
                    var legTime = String(leg) +' mins';
                    
                    document.getElementById('leg_'+routesIncluded[i]+j).innerHTML = legTime;
                    
                    if (j == response[i].length - 1){
                        var totalTime = String(total) + ' mins';
                        
                        document.getElementById('journey_'+routesIncluded[i]).innerHTML = totalTime;
			document.getElementById('timePreview_'+routesIncluded[i]).innerHTML = totalTime;
                        if (wait == 16666){
                            document.getElementById('journey_'+routesIncluded[i]).style.visibility = "hidden";
                        }
                    }
                }

		else{
                                
    
           
            //j = the different legs in a route
            var wait = 0;
            var travelMode = GoogleResponse.routes[routesIncluded[i]].legs[0].steps[j].travel_mode;
             
            if (travelMode == "TRANSIT"){
                var leg = Math.round(GoogleResponse.routes[routesIncluded[i]].legs[0].steps[j].duration.value/60);
                
		var legTime = String(leg) +' mins';
                document.getElementById('leg_'+routesIncluded[i]+j).innerHTML = legTime;
		
                var errorMessage = 'No wait/timetable info available';
                document.getElementById('wait_'+routesIncluded[i]+j).innerHTML = errorMessage;
		document.getElementById('wait_'+routesIncluded[i]+j).style.fontSize = "1.2vw";

            }
             else{
                var leg = Math.round(GoogleResponse.routes[routesIncluded[i]].legs[0].steps[j].duration.value/60);
                
		var legTime = String(leg) +' mins';
                document.getElementById('leg_'+routesIncluded[i]+j).innerHTML = legTime;
             }
             total += leg;
             if (j == GoogleResponse.routes[routesIncluded[i]].legs[0].steps.length - 1){
                var totalTime = String(total) + ' mins';
                
                document.getElementById('journey_'+routesIncluded[i]).innerHTML = totalTime;
		document.getElementById('timePreview_'+routesIncluded[i]).innerHTML = totalTime;
               }
                    
        
                }
                }
            }
        
        }  
                    
});

    $(document).ready(function(){
        $('[data-trigger="hover"]').popover(); 
    });
    //when directions are requested, the first route appears on the map
    if(routesIncluded.length == 0)
    	{
    routes[activeRoute].setMap(null);
    	}
    else
	{
    //when directions are requested, the first route appears on the map
    routes[activeRoute].setMap(map);
    var selectDivId = 'button_'+activeRoute;
    $('#'+ selectDivId).removeClass("col-sm-1").addClass("col-sm-"+divSize+" bg-light");
    $('#'+ selectDivId).find('#journeyDetail').removeClass("d-none");
	}
	
    //When a button for another route is clicked the currently active map is set to null
    //The active map is then reassined to the newly clicked route option
    //Add a liistenter to each of the buttons, if clicked, the corresponding route object is set to map (not null)
    for (let i = 0; i < routesIncluded.length; ++i) {
        var elem = document.getElementById('button_'+routesIncluded[i]);
        elem.addEventListener('click', function() {

            routes[activeRoute].setMap(null);
	    document.getElementById("holder_"+activeRoute).style.display = "none";
            document.getElementById("timePreview_"+activeRoute).style.display = "block"; 
            $('#'+ selectDivId).removeClass("col-sm-"+divSize+" bg-light").addClass("col-sm-1 bg-warning");
            $('#'+ selectDivId).find('#journeyDetail').addClass("d-none");
            $('#'+ selectDivId).find('span').css("background-color", "#fdc007")
            activeRoute = routesIncluded[i];
            selectDivId = 'button_'+activeRoute;

            routes[activeRoute].setMap(map);
            document.getElementById("holder_"+activeRoute).style.display = "block";
            document.getElementById("timePreview_"+activeRoute).style.display = "none";
              $('#'+ selectDivId).removeClass("col-sm-1").addClass("col-sm-"+divSize+" bg-light");
              $('#'+ selectDivId).find('span').css("background-color", "#f7f8f9")
              $('#'+ selectDivId).find('#journeyDetail').removeClass("d-none");

        });
    }
}

