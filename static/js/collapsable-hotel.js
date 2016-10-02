var shownState = false;

$( document ).ready( function() {
	$('ul.hotel-list').hide();
	$('div.button_see_hotels').on('click', function() {
		if (!shownState) {
			$('ul.hotel-list').slideDown();
			switchShownState();
		} else {
			$('ul.hotel-list').slideUp();
			switchShownState();
		}
	});
});

var switchShownState = function() {
	if (shownState == false) {
		shownState = true;
	} else {
		shownState = false
	}
}