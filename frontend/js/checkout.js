const addressSelect =
    document.getElementById(
        "address-select"
    );

const checkoutItems =
    document.getElementById(
        "checkout-items"
    );

const checkoutTotal =
    document.getElementById(
        "checkout-total"
    );

const checkoutLoading =
    document.getElementById(
        "checkout-loading"
    );

const checkoutError =
    document.getElementById(
        "checkout-error"
    );

const checkoutContent =
    document.getElementById(
        "checkout-content"
    );

const placeOrderButton =
    document.getElementById(
        "place-order-button"
    );


const IDEMPOTENCY_STORAGE_KEY =
    "checkout_idempotency_key";


function formatPrice(price) {
    return Number(price).toLocaleString(
        "en-PK",
        {
            style: "currency",
            currency: "PKR",
            maximumFractionDigits: 0,
        }
    );
}


function showError(message) {
    checkoutError.textContent =
        message;

    checkoutError.style.display =
        "block";
}


function getOrCreateIdempotencyKey() {
    let key =
        sessionStorage.getItem(
            IDEMPOTENCY_STORAGE_KEY
        );


    if (key) {
        return key;
    }


    if (
        window.crypto &&
        crypto.randomUUID
    ) {
        key =
            crypto.randomUUID();

    } else {
        key =
            `checkout-${Date.now()}-${Math.random()
                .toString(16)
                .slice(2)}`;
    }


    sessionStorage.setItem(
        IDEMPOTENCY_STORAGE_KEY,
        key
    );


    return key;
}


function renderAddresses(data) {
    addressSelect.innerHTML = "";


    const addresses =
        Array.isArray(data)
            ? data
            : data?.items || [];


    if (addresses.length === 0) {
        const option =
            document.createElement(
                "option"
            );

        option.textContent =
            "No address found";

        option.value = "";

        addressSelect.appendChild(
            option
        );

        placeOrderButton.disabled =
            true;

        showError(
            "You need a shipping address before checkout."
        );

        return;
    }


    addresses.forEach(address => {
        const option =
            document.createElement(
                "option"
            );

        option.value =
            address.id;

        option.textContent =
            `${address.label} - ${address.address_line1}, ${address.city}`;


        if (address.is_default) {
            option.selected = true;
        }


        addressSelect.appendChild(
            option
        );
    });
}


function renderCart(cart) {
    checkoutItems.innerHTML = "";


    if (cart.items.length === 0) {
        showError(
            "Your cart is empty."
        );

        placeOrderButton.disabled =
            true;

        return;
    }


    cart.items.forEach(item => {
        const row =
            document.createElement(
                "div"
            );

        row.className =
            "checkout-item";


        const name =
            document.createElement(
                "span"
            );

        name.textContent =
            `${item.product_name} - ${item.variant_name} × ${item.quantity}`;


        const subtotal =
            document.createElement(
                "strong"
            );

        subtotal.textContent =
            formatPrice(
                item.subtotal
            );


        row.append(
            name,
            subtotal
        );


        checkoutItems.appendChild(
            row
        );
    });


    checkoutTotal.textContent =
        `Total: ${formatPrice(cart.subtotal)}`;
}


async function initializeCheckout() {
    if (
        !getAccessToken() &&
        !getRefreshToken()
    ) {
        window.location.href =
            "login.html?next=checkout.html";

        return;
    }


    try {
        const [
            addresses,
            cart,
        ] = await Promise.all([
            getAddresses(),
            getCart(),
        ]);


        renderAddresses(
            addresses
        );

        renderCart(
            cart
        );


        getOrCreateIdempotencyKey();


    } catch (error) {
        showError(
            error.message
        );

    } finally {
        checkoutLoading.style.display =
            "none";
    }
}


placeOrderButton.addEventListener(
    "click",
    async () => {
        checkoutError.style.display =
            "none";


        const addressId =
            Number(
                addressSelect.value
            );


        if (
            !Number.isInteger(addressId) ||
            addressId <= 0
        ) {
            showError(
                "Please select a valid shipping address."
            );

            return;
        }


        placeOrderButton.disabled =
            true;

        placeOrderButton.textContent =
            "Placing Order...";


        try {
            const idempotencyKey =
                getOrCreateIdempotencyKey();


            const order =
                await checkoutOrder(
                    addressId,
                    idempotencyKey
                );


            sessionStorage.removeItem(
                IDEMPOTENCY_STORAGE_KEY
            );


            window.location.href =
                `order-success.html?id=${order.id}`;


        } catch (error) {
            showError(
                error.message
            );

            placeOrderButton.disabled =
                false;

            placeOrderButton.textContent =
                "Place Order";
        }
    }
);


initializeCheckout();