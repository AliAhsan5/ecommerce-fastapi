const addressForm =
    document.getElementById(
        "address-form"
    );

const addressesContainer =
    document.getElementById(
        "addresses-container"
    );

const loadingMessage =
    document.getElementById(
        "loading-message"
    );

const messageBox =
    document.getElementById(
        "message"
    );

const formTitle =
    document.getElementById(
        "form-title"
    );

const saveButton =
    document.getElementById(
        "save-button"
    );

const cancelEditButton =
    document.getElementById(
        "cancel-edit-button"
    );


const addressIdInput =
    document.getElementById(
        "address-id"
    );

const labelInput =
    document.getElementById(
        "label"
    );

const recipientNameInput =
    document.getElementById(
        "recipient-name"
    );

const phoneInput =
    document.getElementById(
        "phone"
    );

const addressLine1Input =
    document.getElementById(
        "address-line1"
    );

const addressLine2Input =
    document.getElementById(
        "address-line2"
    );

const cityInput =
    document.getElementById(
        "city"
    );

const stateInput =
    document.getElementById(
        "state"
    );

const postalCodeInput =
    document.getElementById(
        "postal-code"
    );

const countryInput =
    document.getElementById(
        "country"
    );

const isDefaultInput =
    document.getElementById(
        "is-default"
    );


let savedAddresses = [];


/* =========================
   MESSAGE
========================= */

function showMessage(
    message,
    type
) {
    messageBox.textContent =
        message;

    messageBox.className =
        type;
}


function clearMessage() {
    messageBox.textContent = "";
    messageBox.className = "";
}


/* =========================
   FORM DATA
========================= */

function getAddressFormData() {

    return {
        label:
            labelInput.value.trim(),

        recipient_name:
            recipientNameInput.value.trim(),

        phone:
            phoneInput.value.trim(),

        address_line1:
            addressLine1Input.value.trim(),

        address_line2:
            addressLine2Input.value.trim()
            || null,

        city:
            cityInput.value.trim(),

        state:
            stateInput.value.trim(),

        postal_code:
            postalCodeInput.value.trim()
            || null,

        country:
            countryInput.value.trim(),

        is_default:
            isDefaultInput.checked,
    };
}


/* =========================
   RESET FORM
========================= */

function resetAddressForm() {

    addressForm.reset();

    addressIdInput.value = "";

    stateInput.value =
        "Sindh";

    countryInput.value =
        "Pakistan";

    formTitle.textContent =
        "Add Shipping Address";

    saveButton.textContent =
        "Save Address";

    cancelEditButton.style.display =
        "none";
}


/* =========================
   RENDER
========================= */

function renderAddresses(
    addresses
) {

    addressesContainer.innerHTML =
        "";


    if (
        !addresses ||
        addresses.length === 0
    ) {

        const emptyMessage =
            document.createElement(
                "p"
            );

        emptyMessage.className =
            "empty";

        emptyMessage.textContent =
            "No addresses saved yet.";

        addressesContainer.appendChild(
            emptyMessage
        );

        return;
    }


    addresses.forEach(
        address => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "address-card";


            const title =
                document.createElement(
                    "h3"
                );

            title.textContent =
                address.label;


            if (
                address.is_default
            ) {

                const badge =
                    document.createElement(
                        "span"
                    );

                badge.className =
                    "default-badge";

                badge.textContent =
                    "Default";

                title.appendChild(
                    badge
                );
            }


            const recipient =
                document.createElement(
                    "p"
                );

            recipient.textContent =
                address.recipient_name;


            const phone =
                document.createElement(
                    "p"
                );

            phone.textContent =
                address.phone;


            const fullAddress =
                document.createElement(
                    "p"
                );

            let addressText =
                address.address_line1;


            if (
                address.address_line2
            ) {
                addressText +=
                    `, ${address.address_line2}`;
            }


            addressText +=
                `, ${address.city}`;

            addressText +=
                `, ${address.state}`;

            if (
                address.postal_code
            ) {
                addressText +=
                    ` ${address.postal_code}`;
            }

            addressText +=
                `, ${address.country}`;


            fullAddress.textContent =
                addressText;


            const actions =
                document.createElement(
                    "div"
                );

            actions.className =
                "actions";


            const editButton =
                document.createElement(
                    "button"
                );

            editButton.className =
                "secondary-button";

            editButton.textContent =
                "Edit";

            editButton.addEventListener(
                "click",
                () => {
                    startEditAddress(
                        address
                    );
                }
            );


            const deleteButton =
                document.createElement(
                    "button"
                );

            deleteButton.className =
                "danger-button";

            deleteButton.textContent =
                "Delete";

            deleteButton.addEventListener(
                "click",
                () => {
                    removeAddress(
                        address.id
                    );
                }
            );


            actions.append(
                editButton,
                deleteButton
            );


            card.append(
                title,
                recipient,
                phone,
                fullAddress,
                actions
            );


            addressesContainer.appendChild(
                card
            );
        }
    );
}


/* =========================
   LOAD
========================= */

async function loadAddresses() {

    loadingMessage.style.display =
        "block";

    try {

        const data =
            await getAddresses();


        savedAddresses =
            Array.isArray(data)
                ? data
                : data?.items || [];


        renderAddresses(
            savedAddresses
        );


    } catch (error) {

        showMessage(
            error.message,
            "error"
        );


    } finally {

        loadingMessage.style.display =
            "none";
    }
}


/* =========================
   EDIT
========================= */

function startEditAddress(
    address
) {

    clearMessage();


    addressIdInput.value =
        address.id;

    labelInput.value =
        address.label;

    recipientNameInput.value =
        address.recipient_name;

    phoneInput.value =
        address.phone;

    addressLine1Input.value =
        address.address_line1;

    addressLine2Input.value =
        address.address_line2
        || "";

    cityInput.value =
        address.city;

    stateInput.value =
        address.state;

    postalCodeInput.value =
        address.postal_code
        || "";

    countryInput.value =
        address.country;

    isDefaultInput.checked =
        address.is_default;


    formTitle.textContent =
        "Edit Shipping Address";

    saveButton.textContent =
        "Update Address";

    cancelEditButton.style.display =
        "block";


    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
}


/* =========================
   SAVE
========================= */

addressForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();

        clearMessage();


        const addressData =
            getAddressFormData();


        const addressId =
            Number(
                addressIdInput.value
            );


        saveButton.disabled =
            true;


        try {

            if (
                Number.isInteger(
                    addressId
                )
                &&
                addressId > 0
            ) {

                await updateAddress(
                    addressId,
                    addressData
                );

                showMessage(
                    "Address updated successfully.",
                    "success"
                );

            } else {

                await createAddress(
                    addressData
                );

                showMessage(
                    "Address saved successfully.",
                    "success"
                );
            }


            resetAddressForm();

            await loadAddresses();


        } catch (error) {

            showMessage(
                error.message,
                "error"
            );


        } finally {

            saveButton.disabled =
                false;
        }
    }
);


/* =========================
   DELETE
========================= */

async function removeAddress(
    addressId
) {

    const confirmed =
        window.confirm(
            "Delete this address?"
        );


    if (!confirmed) {
        return;
    }


    clearMessage();


    try {

        await deleteAddress(
            addressId
        );


        showMessage(
            "Address deleted successfully.",
            "success"
        );


        await loadAddresses();


    } catch (error) {

        showMessage(
            error.message,
            "error"
        );
    }
}


/* =========================
   CANCEL EDIT
========================= */

cancelEditButton.addEventListener(
    "click",
    () => {

        resetAddressForm();
        clearMessage();
    }
);


/* =========================
   INITIALIZE
========================= */

async function initializeAddresses() {

    if (
        !getAccessToken()
        &&
        !getRefreshToken()
    ) {

        window.location.href =
            "login.html?next=addresses.html";

        return;
    }


    await loadAddresses();
}


initializeAddresses();