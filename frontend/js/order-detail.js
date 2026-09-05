const orderContainer =
    document.getElementById(
        "order-detail-container"
    );

const orderLoading =
    document.getElementById(
        "order-loading"
    );

const orderError =
    document.getElementById(
        "order-error"
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


function getOrderId() {
    const params =
        new URLSearchParams(
            window.location.search
        );

    const id =
        Number(
            params.get("id")
        );

    return Number.isInteger(id) &&
        id > 0
        ? id
        : null;
}


function createTextElement(
    tag,
    text
) {
    const element =
        document.createElement(tag);

    element.textContent = text;

    return element;
}


function renderOrder(order) {
    orderContainer.innerHTML = "";


    const header =
        document.createElement(
            "section"
        );

    header.className =
        "order-detail-card";


    header.append(
        createTextElement(
            "h2",
            `Order #${order.id}`
        ),
        createTextElement(
            "p",
            `Status: ${order.status}`
        ),
        createTextElement(
            "p",
            `Payment: ${order.payment_method.toUpperCase()}`
        ),
        createTextElement(
            "h3",
            `Total: ${formatPrice(order.total_amount)}`
        )
    );


    const address =
        document.createElement(
            "section"
        );

    address.className =
        "order-detail-card";


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
            order.country
        )
    );


    const items =
        document.createElement(
            "section"
        );

    items.className =
        "order-detail-card";


    items.appendChild(
        createTextElement(
            "h2",
            "Items"
        )
    );


    order.items.forEach(item => {
        const row =
            document.createElement(
                "div"
            );

        row.className =
            "checkout-item";


        row.append(
            createTextElement(
                "span",
                `${item.product_name} - ${item.variant_name} × ${item.quantity}`
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
        "order-detail-card";


    history.appendChild(
        createTextElement(
            "h2",
            "Status History"
        )
    );


    order.status_history.forEach(
        record => {
            history.appendChild(
                createTextElement(
                    "p",
                    `${record.status} - ${new Date(
                        record.created_at
                    ).toLocaleString()}`
                )
            );
        }
    );


    orderContainer.append(
        header,
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
            await getOrder(
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


loadOrder();