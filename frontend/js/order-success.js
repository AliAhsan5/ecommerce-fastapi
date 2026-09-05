const successLoading =
    document.getElementById(
        "success-loading"
    );

const successError =
    document.getElementById(
        "success-error"
    );

const successDetails =
    document.getElementById(
        "success-details"
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

    if (
        !Number.isInteger(id) ||
        id <= 0
    ) {
        return null;
    }

    return id;
}


async function loadOrder() {
    const orderId =
        getOrderId();


    if (orderId === null) {
        successLoading.style.display =
            "none";

        successError.textContent =
            "Invalid order ID.";

        successError.style.display =
            "block";

        return;
    }


    try {
        const order =
            await getOrder(
                orderId
            );


        const orderNumber =
            document.createElement(
                "h2"
            );

        orderNumber.textContent =
            `Order #${order.id}`;


        const status =
            document.createElement(
                "p"
            );

        status.textContent =
            `Status: ${order.status}`;


        const total =
            document.createElement(
                "p"
            );

        total.textContent =
            `Total: ${formatPrice(
                order.total_amount
            )}`;


        const detailLink =
            document.createElement(
                "a"
            );

        detailLink.href =
            `order-detail.html?id=${order.id}`;

        detailLink.className =
            "view-button";

        detailLink.textContent =
            "View Order";


        const ordersLink =
            document.createElement(
                "a"
            );

        ordersLink.href =
            "orders.html";

        ordersLink.className =
            "view-button";

        ordersLink.textContent =
            "My Orders";


        successDetails.append(
            orderNumber,
            status,
            total,
            detailLink,
            document.createTextNode(
                " "
            ),
            ordersLink
        );


    } catch (error) {
        successError.textContent =
            error.message;

        successError.style.display =
            "block";

    } finally {
        successLoading.style.display =
            "none";
    }
}


loadOrder();