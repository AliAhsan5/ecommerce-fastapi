const ordersTable =
    document.getElementById(
        "orders-table"
    );

const ordersLoading =
    document.getElementById(
        "orders-loading"
    );

const ordersError =
    document.getElementById(
        "orders-error"
    );


const statusFilter =
    document.getElementById(
        "status-filter"
    );

const userFilter =
    document.getElementById(
        "user-filter"
    );

const fromDate =
    document.getElementById(
        "from-date"
    );

const toDate =
    document.getElementById(
        "to-date"
    );


const applyFilterButton =
    document.getElementById(
        "apply-filter"
    );

const resetFilterButton =
    document.getElementById(
        "reset-filter"
    );


const previousPageButton =
    document.getElementById(
        "previous-page"
    );

const nextPageButton =
    document.getElementById(
        "next-page"
    );

const pageInfo =
    document.getElementById(
        "page-info"
    );


const logoutButton =
    document.getElementById(
        "logout-button"
    );


let currentPage = 1;

const pageSize = 20;

let totalOrders = 0;


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


function formatDate(value) {
    return new Date(
        value
    ).toLocaleString();
}


function getStatusClass(status) {
    if (
        status === "delivered"
    ) {
        return "active-status";
    }


    if (
        status === "cancelled"
    ) {
        return "inactive-status";
    }


    return "pending-status";
}


function renderOrders(orders) {
    ordersTable.innerHTML = "";


    if (orders.length === 0) {
        const row =
            document.createElement(
                "tr"
            );

        const cell =
            document.createElement(
                "td"
            );

        cell.colSpan = 7;

        cell.textContent =
            "No orders found.";

        row.appendChild(cell);

        ordersTable.appendChild(row);

        return;
    }


    orders.forEach(order => {

        const row =
            document.createElement(
                "tr"
            );


        const orderCell =
            document.createElement(
                "td"
            );

        orderCell.textContent =
            `#${order.id}`;


        const userCell =
            document.createElement(
                "td"
            );

        userCell.textContent =
            order.user_id;


        const dateCell =
            document.createElement(
                "td"
            );

        dateCell.textContent =
            formatDate(
                order.created_at
            );


        const paymentCell =
            document.createElement(
                "td"
            );

        paymentCell.textContent =
            order.payment_method
                .toUpperCase();


        const totalCell =
            document.createElement(
                "td"
            );

        totalCell.textContent =
            formatPrice(
                order.total_amount
            );


        const statusCell =
            document.createElement(
                "td"
            );


        const statusBadge =
            document.createElement(
                "span"
            );

        statusBadge.className =
            `status-badge ${getStatusClass(
                order.status
            )}`;

        statusBadge.textContent =
            order.status;


        statusCell.appendChild(
            statusBadge
        );


        const actionCell =
            document.createElement(
                "td"
            );


        const detailLink =
            document.createElement(
                "a"
            );

        detailLink.href =
            `order-detail.html?id=${order.id}`;

        detailLink.className =
            "table-link-button";

        detailLink.textContent =
            "View";


        actionCell.appendChild(
            detailLink
        );


        row.append(
            orderCell,
            userCell,
            dateCell,
            paymentCell,
            totalCell,
            statusCell,
            actionCell
        );


        ordersTable.appendChild(
            row
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


    previousPageButton.disabled =
        currentPage <= 1;


    nextPageButton.disabled =
        currentPage >= totalPages;
}


function buildFilters() {
    return {
        page:
            currentPage,

        page_size:
            pageSize,

        status:
            statusFilter.value,

        user_id:
            userFilter.value,

        created_from:
            fromDate.value,

        created_to:
            toDate.value,
    };
}


async function loadOrders() {
    ordersLoading.style.display =
        "block";

    ordersError.style.display =
        "none";


    try {
        const data =
            await getAdminOrders(
                buildFilters()
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


applyFilterButton.addEventListener(
    "click",
    async () => {
        currentPage = 1;

        await loadOrders();
    }
);


resetFilterButton.addEventListener(
    "click",
    async () => {
        statusFilter.value = "";
        userFilter.value = "";
        fromDate.value = "";
        toDate.value = "";

        currentPage = 1;

        await loadOrders();
    }
);


previousPageButton.addEventListener(
    "click",
    async () => {
        if (currentPage > 1) {
            currentPage--;

            await loadOrders();
        }
    }
);


nextPageButton.addEventListener(
    "click",
    async () => {
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

            await loadOrders();
        }
    }
);


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


    await loadOrders();
}


initializePage();