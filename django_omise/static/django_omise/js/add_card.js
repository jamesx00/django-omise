const checkoutForm = document.getElementById('checkout');
const cardNumberInput = document.getElementById('id_card_number');
const nameOnCardInput = document.getElementById('id_name_on_card');
const expirationMonthInput = document.getElementById('id_expiration_month');
const expirationYearInput = document.getElementById('id_expiration_year');
const securityCodeInput = document.getElementById('id_security_number');
const omiseTokenInput = document.getElementById('id_omise_token');
const omisePublicKeyInput = document.getElementById('id_omise_public_key');
const submitButton = document.getElementById('submit_button');
const tokenError = document.getElementById('token_errors');

Omise.setPublicKey(omisePublicKeyInput.value);

$('#id_card_number').payment('formatCardNumber');

checkoutForm.addEventListener('submit', function (e) {
	e.preventDefault();
	tokenError.classList.add('hidden');

	submitButton.setAttribute('disabled', true);

	const card = {
		number: cardNumberInput.value,
		name: nameOnCardInput.value,
		expiration_month: expirationMonthInput.value,
		expiration_year: expirationYearInput.value,
		security_code: securityCodeInput.value,
	};

	Omise.createToken('card', card, function (statusCode, response) {
		if (response.object == 'error' || !response.card.security_code_check) {
			tokenError.classList.remove('hidden');

			var message_text = 'SET YOUR SECURITY CODE CHECK FAILED MESSAGE';

			if (response.object == 'error') {
				message_text = response.message;
			}

			tokenError.innerHTML = message_text;

			submitButton.removeAttribute('disabled');
		} else {
			omiseTokenInput.value = response.id;
			cardNumberInput.value = '';
			nameOnCardInput.value = '';
			expirationMonthInput.value = '';
			expirationYearInput.value = '';
			securityCodeInput.value = '';

			checkoutForm.submit();
		}
	});

	return false;
});
