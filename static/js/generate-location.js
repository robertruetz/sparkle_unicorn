var elBody = document.getElementById('third_page');

// generate single location
function generateLocation(image, locationName, concepts) {
	htmlBodyString = "<div class='w3-card-4 w3-margin w3-white' id='entry_container'>" +
    				"<div class='row'>" +
      					"<div class='col-sm-4'>" +
        					"<img src=" + image + "alt='Nature' style='width:100%'/>" +
      					"</div>" +

      					"<div class='col-sm-8'>" +
        					"<div class='w3-container w3-padding-8'>" +
          						"<h3><b>" + locationName + "</b></h3>" +
        					"</div>" +

        				"<div class='w3-container' id='activity_description'>" +
          					generateConcepts(concepts) +
        				"</div>" +
      				"</div>" +
        				"<div class='w3-row button_see_hotels'>" +
          					"<div class='w3-col m8 s12'>" +
            					"<p><button class='w3-btn w3-padding-large w3-white w3-border w3-hover-border-black'><b>See Hotels</b></button></p>" +
        					"</div>" +
      					"</div>"
    				"</div>" +
  				"</div>";

//  	htmlBodyString += generateHotels();

  	return htmlBodyString;
}

// create html concepts in <p> tag for generateLocation()
function generateConcepts(concepts) {
	var conceptsHtml = ""
	for (var i = 0; i <= concepts.length-1; i++) {
		var totalLength = concepts.length;
		conceptsHtml += "<p>" + concepts[i] + ". </p>";
	}

	return conceptsHtml
}

// generate entire html content
function generateMultipleCities(LocationNameList) {
	var fullHtmlString = "";
	for(var i=0; i <= LocationNameList.length-1; i++) {
		fullHtmlString += generateLocation();
	}
	elBody.innerHTML = fullHtmlString;
}


function generateHotels(hotelList) {
	var htmlHotelString = "<ul class='w3-card-4 w3-margin w3-white hotel-list'>";
	for(var i = 0; i <= hotelList.length-1; i++) {
		var hotelName = //GRAB NAME
		htmlHotelString += "<li>" +
      							"<h6>" + hotelName + "</h6>" +
    						"</li>" +
    						"<hr>";
    	// if last iteration
    	if (i === hotelList.length-1) {
    		htmlHotelString += "</ul>";
    	}
	}
	return htmlHotelString;
}