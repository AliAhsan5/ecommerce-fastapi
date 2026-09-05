const ordersContainer =
    document.getElementById(
        "orders-container"
    );

const ordersLoading =
    document.getElementById(
        "orders-loading"
    );

const ordersError =
    document.getElementById(
        "orders-error"
    );

const previousButton =
    document.getElementById(
        "previous-orders"
    );

const nextButton =
    document.getElementById(
        "next-orders"
    );

const pageInfo =
    document.getElementById(
        "orders-page-info"
    );


let currentPage = 1;

const pageSize = 10;

let totalOrders = 0;


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


function formatDate(date) {
    return new Date(
        date
    ).toLocaleString();
}


function renderOrders(orders) {
    ordersContainer.innerHTML = "";


    if (orders.length === 0) {
        const message =
            document.createElement(
                "p"
            );

        message.textContent =
            "You have no orders yet.";

        ordersContainer.appendChild(
            message
        );

        return;
    }


    orders.forEach(order => {
        const card =
            document.createElement(
                "article"
            );

        card.className =
            "order-card";


        const title =
            document.createElement(
                "h3"
            );

        title.textContent =
            `Order #${order.id}`;


        const date =
            document.createElement(
                "p"
            );

        date.textContent =
            formatDate(
                order.created_at
            );


        const status =
            document.createElement(
                "p"
            );

        status.textContent =
            `Status: ${order.status}`;


        const total =
            document.createElement(
                "strong"
            );

        total.textContent =
            formatPrice(
                order.total_amount
            );


        const link =
            document.createElement(
                "a"
            );

        link.href =
            `order-detail.html?id=${order.id}`;

        link.className =
            "view-button";

        link.textContent =
            "View Details";


        card.append(
            title,
            date,
            status,
            total,
            link
        );


        ordersContainer.appendChild(
            card
        );
    });
}


function updatePagination() {
    const totalPages =
        Math.max(
            1,
            Math.ceil(
                totalOrders /
                pageSize
            )
        );


    pageInfo.textContent =
        `Page ${currentPage} of ${totalPages}`;


    previousButton.disabled =
        currentPage <= 1;


    nextButton.disabled =
        currentPage >= totalPages;
}


async function loadOrders() {
    ordersLoading.style.display =
        "block";

    ordersError.style.display =
        "none";


    try {
        const data =
            await getOrders(
                currentPage,
                pageSize
            );


        totalOrders =
            data.total;


        renderOrders(
            data.items
        );


        updatePagination();


    } catch (error) {
        ordersError.textContent =
            error.message;

        ordersError.style.display =
            "block";

    } finally {
        ordersLoading.style.display =
            "none";
    }
}


previousButton.addEventListener(
    "click",
    () => {
        if (currentPage > 1) {
            currentPage--;

            loadOrders();
        }
    }
);


nextButton.addEventListener(
    "click",
    () => {
        const totalPages =
            Math.ceil(
                totalOrders /
                pageSize
            );


        if (
            currentPage <
            totalPages
        ) {
            currentPage++;

            loadOrders();
        }
    }
);


loadOrders();