const cartItemsContainer =
    document.getElementById(
        "cart-items"
    );

const cartSummary =
    document.getElementById(
        "cart-summary"
    );

const cartLoading =
    document.getElementById(
        "cart-loading"
    );

const cartError =
    document.getElementById(
        "cart-error"
    );


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
    cartError.textContent =
        message;

    cartError.style.display =
        "block";
}


function renderCart(cart) {
    cartItemsContainer.innerHTML = "";
    cartSummary.innerHTML = "";


    if (cart.items.length === 0) {
        const emptyMessage =
            document.createElement("p");

        emptyMessage.textContent =
            "Your cart is empty.";

        cartItemsContainer.appendChild(
            emptyMessage
        );

        return;
    }


    cart.items.forEach(item => {
        const row =
            document.createElement(
                "article"
            );

        row.className =
            "cart-item";


        const info =
            document.createElement(
                "div"
            );

        const title =
            document.createElement("h3");

        title.textContent =
            `${item.product_name} - ${item.variant_name}`;


        const sku =
            document.createElement("p");

        sku.textContent =
            `SKU: ${item.sku}`;


        const unitPrice =
            document.createElement("p");

        unitPrice.textContent =
            `Unit Price: ${formatPrice(item.unit_price)}`;


        info.append(
            title,
            sku,
            unitPrice
        );


        const quantity =
            document.createElement(
                "input"
            );

        quantity.type = "number";
        quantity.min = "1";
        quantity.value =
            item.quantity;


        const updateButton =
            document.createElement(
                "button"
            );

        updateButton.textContent =
            "Update";


        updateButton.addEventListener(
            "click",
            async () => {
                try {
                    const requestedQuantity =
                        Number(
                            quantity.value
                        );

                    if (
                        !Number.isInteger(
                            requestedQuantity
                        ) ||
                        requestedQuantity < 1
                    ) {
                        showError(
                            "Enter a valid quantity."
                        );

                        return;
                    }

                    const updated =
                        await updateCartItem(
                            item.id,
                            requestedQuantity
                        );

                    renderCart(updated);

                } catch (error) {
                    showError(
                        error.message
                    );
                }
            }
        );


        const removeButton =
            document.createElement(
                "button"
            );

        removeButton.textContent =
            "Remove";

        removeButton.className =
            "danger-button";


        removeButton.addEventListener(
            "click",
            async () => {
                try {
                    await removeCartItem(
                        item.id
                    );

                    await loadCart();

                } catch (error) {
                    showError(
                        error.message
                    );
                }
            }
        );


        const subtotal =
            document.createElement(
                "strong"
            );

        subtotal.textContent =
            formatPrice(
                item.subtotal
            );


        row.append(
            info,
            quantity,
            updateButton,
            removeButton,
            subtotal
        );


        cartItemsContainer.appendChild(
            row
        );
    });


    const totalItems =
        document.createElement("p");

    totalItems.textContent =
        `Total Items: ${cart.total_items}`;


    const subtotal =
        document.createElement("h2");

    subtotal.textContent =
        `Subtotal: ${formatPrice(cart.subtotal)}`;


    const checkoutLink =
        document.createElement("a");

    checkoutLink.href =
        "checkout.html";

    checkoutLink.className =
        "view-button";

    checkoutLink.textContent =
        "Proceed to Checkout";


    const clearButton =
        document.createElement(
            "button"
        );

    clearButton.textContent =
        "Clear Cart";

    clearButton.className =
        "danger-button";


    clearButton.addEventListener(
        "click",
        async () => {
            try {
                await clearCart();
                await loadCart();

            } catch (error) {
                showError(
                    error.message
                );
            }
        }
    );


    cartSummary.append(
        totalItems,
        subtotal,
        checkoutLink,
        document.createTextNode(" "),
        clearButton
    );
}


async function loadCart() {
    cartLoading.style.display =
        "block";

    cartError.style.display =
        "none";


    try {
        const cart =
            await getCart();

        renderCart(cart);

    } catch (error) {
        if (
            !getAccessToken() &&
            !getRefreshToken()
        ) {
            window.location.href =
                "login.html?next=cart.html";

            return;
        }

        showError(
            error.message
        );

    } finally {
        cartLoading.style.display =
            "none";
    }
}


loadCart();