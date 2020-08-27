// On changing a tick box, send API request to update database
$('input:checkbox').change(function () {
	var checklist_item_id = this.id.replace(/checklist-item-/g,'');
	var completed = this.checked;
	// Very ugly. Is there a better way to traverse the DOM in an ascending fashion?
	var checklist_id = $(this).parent().parent().parent().parent().parent().parent().prop('id').replace(/checklist-/g, '');

	// Get the csrf token
	const csrftoken = Cookies.get('_csrf_token');

	// PUT data via AJAX
	$.ajax({
		type: 'PUT',
		url: '/api/v1/checklist/item/' + checklist_item_id,
		contentType: 'application/json',
		headers: { 'key': config.apiKey, 'X-CSRFToken': csrftoken},
		data: JSON.stringify({
			completed: completed
		}),
		error: function (jqXHR, textStatus, errorThrown) {
			toastr.error(errorThrown);
			toastr.error(textStatus);
		},
		success: function (data) {
			toastr.success('Checklist updated.');
			// Update the progress bar and remaining items count
			// GET data via AJAX
			$.ajax({
				url: '/api/v1/checklist/' + checklist_id,
				headers: { 'key': config.apiKey },
				success: function (data) {
					$('#checklist-' + checklist_id + ' #progress-circle').removeClass();
					$('#checklist-' + checklist_id + ' #progress-circle').addClass('progress-circle').addClass('progress-' + data.completed_percentage);
					$('#checklist-' + checklist_id + ' #progress-circle span').text(data.completed_percentage);
					console.log(data)

					if (data.items_remaining == 1) {
						$('#checklist-' + checklist_id + ' .text-muted').text(data.items_remaining + ' item remaining');
					} else {
						$('#checklist-' + checklist_id + ' .text-muted').text(data.items_remaining + ' items remaining');
					}
				 },
			});
			
		}
	});
});


// Save button click handler
$('#save-colour').click(function () {
    var myColor = colorWheel.color.hsl;
    var hue = myColor.h
    var saturation = myColor.s
    var lightness = myColor.l

	var checklist_id = $(this).attr("data-checklist-id")
	
	// Get the csrf token
	const csrftoken = Cookies.get('_csrf_token');
	
	// PUT data via AJAX
    $.ajax({
      type: 'PUT',
      url: '/api/v1/checklist/colour/' + checklist_id,
      contentType: 'application/json',
      headers: {'key': config.apiKey, 'X-CSRFToken': csrftoken},
      data: JSON.stringify({
        hue: hue,
        saturation: saturation,
        lightness: lightness
      }),
      error: function (jqXHR, textStatus, errorThrown) {
        toastr.error(errorThrown);
        toastr.error(textStatus);
      },
      success: function (data) {
		toastr.success('Colour updated.');
		$('#colour-picker-modal').modal('hide')
      }
    });
  });