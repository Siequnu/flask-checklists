// On changing a tick box, send API request to update database
$('input:checkbox').change(function () {
	var id = this.id.replace(/checklist-item-/g,'');
	var completed = this.checked;
	// Very ugly. Is there a better way to traverse the DOM in an ascending fashion?
	var checklist_id = $(this).parent().parent().parent().parent().parent().parent().prop('id').replace(/checklist-/g, '');

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
					$('#checklist-' + checklist_id + ' #progress-circle').removeClass();
					$('#checklist-' + checklist_id + ' #progress-circle').addClass('progress-circle').addClass('progress-' + data.completed_percentage);
					$('#checklist-' + checklist_id + ' #progress-circle span').text(data.completed_percentage);

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