setInterval(function () {
	fetch(chargeStatusUrl, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken'),
		},
		body: JSON.stringify({ charge: charge }),
	})
		.then((response) => {
			return response.json().then((data) => data);
		})
		.then((body) => {
			const chargeStatus = body.data.status;
			if (chargeStatus != 'pending') {
				window.location.reload();
			}
		});
}, 5000);
