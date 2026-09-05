const orderContainer =
    document.getElementById(
        "order-container"
    );

const orderLoading =
    document.getElementById(
        "order-loading"
    );

const orderError =
    document.getElementById(
        "order-error"
    );

const logoutButton =
    document.getElementById(
        "logout-button"
    );


const STATUS_TRANSITIONS = {
    pending: [
        "confirmed",
        "cancelled",
    ],

    confirmed: [
        "processing",
        "cancelled",
    ],

    processing: [
        "shipped",
    ],

    shipped: [
        "delivered",
    ],

    delivered: [],

    cancelled: [],
};


function getOrderId() {
    const params =
        new URLSearchParams(
            window.location.search
        );

    const id =
        Number(
            params.get("id")
        );


    if (
        !Number.isInteger(id) ||
        id <= 0
    ) {
        return null;
    }


    return id;
}


function formatPrice(value) {
    return Number(value).toLocaleString(
        "en-PK",
        {
            style: "currency",
            currency: "PKR",
            maximumFractionDigits: 0,
        }
    );
}


function createTextElement(
    tag,
    text
) {
    const element =
        document.createElement(tag);

    element.textContent =
        text;

    return element;
}


function renderOrder(order) {
    orderContainer.innerHTML = "";


    const overview =
        document.createElement(
            "section"
        );

    overview.className =
        "admin-detail-card";


    overview.append(
        createTextElement(
            "h2",
            `Order #${order.id}`
        ),

        createTextElement(
            "p",
            `Customer User ID: ${order.user_id}`
        ),

        createTextElement(
            "p",
            `Payment: ${order.payment_method.toUpperCase()}`
        ),

        createTextElement(
            "p",
            `Status: ${order.status}`
        ),

        createTextElement(
            "p",
            `Subtotal: ${formatPrice(
                order.subtotal
            )}`
        ),

        createTextElement(
            "p",
            `Shipping: ${formatPrice(
                order.shipping_amount
            )}`
        ),

        createTextElement(
            "h3",
            `Total: ${formatPrice(
                order.total_amount
            )}`
        )
    );


    const statusSection =
        document.createElement(
            "section"
        );

    statusSection.className =
        "admin-detail-card";


    statusSection.appendChild(
        createTextElement(
            "h2",
            "Process Order"
        )
    );


    const allowedStatuses =
        STATUS_TRANSITIONS[
            order.status
        ] || [];


    if (
        allowedStatuses.length === 0
    ) {
        statusSection.appendChild(
            createTextElement(
                "p",
                order.status ===
                    "delivered"
                    ? "Order is completed."
                    : "Order is cancelled."
            )
        );

    } else {

        const select =
            document.createElement(
                "select"
            );


        allowedStatuses.forEach(
            status => {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    status;

                option.textContent =
                    status;

                select.appendChild(
                    option
                );
            }
        );


        const updateButton =
            document.createElement(
                "button"
            );

        updateButton.textContent =
            "Update Status";

        updateButton.className =
            "admin-action-button";


        const result =
            document.createElement(
                "p"
            );

        result.className =
            "admin-message";


        updateButton.addEventListener(
            "click",
            async () => {

                updateButton.disabled =
                    true;


                try {
                    const updated =
                        await updateAdminOrderStatus(
                            order.id,
                            select.value
                        );


                    renderOrder(
                        updated
                    );


                } catch (error) {
                    result.textContent =
                        error.message;

                    result.className =
                        "admin-message admin-message-error";

                    result.style.display =
                        "block";


                    updateButton.disabled =
                        false;
                }
            }
        );


        statusSection.append(
            select,
            updateButton,
            result
        );
    }


    const address =
        document.createElement(
            "section"
        );

    address.className =
        "admin-detail-card";


    address.append(
        createTextElement(
            "h2",
            "Shipping Address"
        ),

        createTextElement(
            "p",
            order.recipient_name
        ),

        createTextElement(
            "p",
            order.phone
        ),

        createTextElement(
            "p",
            order.address_line1
        )
    );


    if (order.address_line2) {
        address.appendChild(
            createTextElement(
                "p",
                order.address_line2
            )
        );
    }


    address.append(
        createTextElement(
            "p",
            `${order.city}, ${order.state}`
        ),

        createTextElement(
            "p",
            `${
                order.postal_code ||
                ""
            } ${order.country}`
        )
    );


    const items =
        document.createElement(
            "section"
        );

    items.className =
        "admin-detail-card";


    items.appendChild(
        createTextElement(
            "h2",
            "Order Items"
        )
    );


    order.items.forEach(item => {

        const row =
            document.createElement(
                "div"
            );

        row.className =
            "admin-order-item";


        row.append(
            createTextElement(
                "span",
                `${item.product_name} - ${item.variant_name}`
            ),

            createTextElement(
                "span",
                `${item.quantity} × ${formatPrice(
                    item.unit_price
                )}`
            ),

            createTextElement(
                "strong",
                formatPrice(
                    item.subtotal
                )
            )
        );


        items.appendChild(row);
    });


    const history =
        document.createElement(
            "section"
        );

    history.className =
        "admin-detail-card";


    history.appendChild(
        createTextElement(
            "h2",
            "Status History"
        )
    );


    order.status_history.forEach(
        record => {

            const row =
                document.createElement(
                    "div"
                );

            row.className =
                "history-row";


            row.append(
                createTextElement(
                    "strong",
                    record.status
                ),

                createTextElement(
                    "span",
                    new Date(
                        record.created_at
                    ).toLocaleString()
                ),

                createTextElement(
                    "span",
                    record.changed_by_user_id
                        ? `User #${record.changed_by_user_id}`
                        : "System"
                )
            );


            history.appendChild(
                row
            );
        }
    );


    orderContainer.append(
        overview,
        statusSection,
        address,
        items,
        history
    );
}


async function loadOrder() {
    const orderId =
        getOrderId();


    if (orderId === null) {
        orderLoading.style.display =
            "none";

        orderError.textContent =
            "Invalid order ID.";

        orderError.style.display =
            "block";

        return;
    }


    try {
        const order =
            await getAdminOrder(
                orderId
            );


        renderOrder(order);


    } catch (error) {
        orderError.textContent =
            error.message;

        orderError.style.display =
            "block";

    } finally {
        orderLoading.style.display =
            "none";
    }
}


logoutButton.addEventListener(
    "click",
    async () => {
        await adminLogout();
    }
);


async function initializePage() {
    const isAdmin =
        await verifyAdmin();


    if (!isAdmin) {
        return;
    }


    await loadOrder();
}


initializePage();