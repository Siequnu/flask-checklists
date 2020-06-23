// On changing a tick box, send API request to update database
$('input:checkbox').change(function () {
	var id = this.id;
	var completed = this.checked;

	// PUT data via AJAX
	$.ajax({
		type: 'PUT',
		url: '/api/v1/checklist/item/' + id,
		contentType: 'application/json',
		headers: { 'key': config.apiKey },
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
					$('#progress-circle').removeClass();
					$('#progress-circle').addClass('progress-circle').addClass('progress-' + data.completed_percentage);
					$('#progress-circle span').text(data.completed_percentage);

					if (data.items_remaining == 1) {
						$('.text-muted').text(data.items_remaining + ' item remaining');
					} else {
						$('.text-muted').text(data.items_remaining + ' items remaining');
					}
				 },
			});
			
		}
	});
});