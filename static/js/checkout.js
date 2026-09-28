document.addEventListener('DOMContentLoaded', function () {
    const addressCards = document.querySelectorAll('.address-card');
    const radioInputs = document.querySelectorAll('input[name="selected_address"]');
    const newAddrCollapse = document.getElementById('newAddressFormCollapse');

    // Sync address card selections
    radioInputs.forEach(radio => {
        radio.addEventListener('change', function () {
            addressCards.forEach(card => card.classList.remove('selected'));
            if (this.checked) {
                const parentCard = this.closest('.address-card');
                if (parentCard) {
                    parentCard.classList.add('selected');
                }
                // Close collapse if open when choosing existing address
                if (newAddrCollapse && newAddrCollapse.classList.contains('show')) {
                    const bsCollapse = bootstrap.Collapse.getInstance(newAddrCollapse) || new bootstrap.Collapse(newAddrCollapse);
                    bsCollapse.hide();
                }
            }
        });
    });

    // Make whole card clickable for address radio
    addressCards.forEach(card => {
        card.addEventListener('click', function (e) {
            if (e.target.tagName !== 'INPUT') {
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change'));
                }
            }
        });
    });
});