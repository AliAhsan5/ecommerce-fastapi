const logoutButton =
    document.getElementById(
        "logout-button"
    );


const dashboardLoading =
    document.getElementById(
        "dashboard-loading"
    );

const dashboardError =
    document.getElementById(
        "dashboard-error"
    );


const customersCount =
    document.getElementById(
        "customers-count"
    );

const productsCount =
    document.getElementById(
        "products-count"
    );

const ordersCount =
    document.getElementById(
        "orders-count"
    );

const pendingCount =
    document.getElementById(
        "pending-count"
    );

const lowStockCount =
    document.getElementById(
        "low-stock-count"
    );

const todayCount =
    document.getElementById(
        "today-count"
    );

const salesTotal =
    document.getElementById(
        "sales-total"
    );


const recentOrdersTable =
    document.getElementById(
        "recent-orders-table"
    );


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


function renderRecentOrders(
    orders
) {

    recentOrdersTable.innerHTML =
        "";


    if (
        orders.length === 0
    ) {

        const row =
            document.createElement(
                "tr"
            );

        const cell =
            document.createElement(
                "td"
            );

        cell.colSpan = 6;

        cell.textContent =
            "No orders found.";


        row.appendChild(
            cell
        );

        recentOrdersTable.appendChild(
            row
        );

        return;
    }


    orders.forEach(
        order => {

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
                `#${order.user_id}`;


            const dateCell =
                document.createElement(
                    "td"
                );

            dateCell.textContent =
                new Date(
                    order.created_at
                ).toLocaleString();


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


            const badge =
                document.createElement(
                    "span"
                );

            badge.className =
                `status-badge ${getStatusClass(
                    order.status
                )}`;

            badge.textContent =
                order.status;


            statusCell.appendChild(
                badge
            );


            const actionCell =
                document.createElement(
                    "td"
                );


            const link =
                document.createElement(
                    "a"
                );

            link.href =
                `order-detail.html?id=${order.id}`;

            link.className =
                "table-link-button";

            link.textContent =
                "View";


            actionCell.appendChild(
                link
            );


            row.append(
                orderCell,
                userCell,
                dateCell,
                totalCell,
                statusCell,
                actionCell
            );


            recentOrdersTable.appendChild(
                row
            );
        }
    );
}


function renderDashboard(data) {

    customersCount.textContent =
        data.customers;


    productsCount.textContent =
        data.products;


    ordersCount.textContent =
        data.orders;


    pendingCount.textContent =
        data.pending_orders;


    lowStockCount.textContent =
        data.low_stock;


    todayCount.textContent =
        data.todays_orders;


    salesTotal.textContent =
        formatPrice(
            data.sales_total
        );


    renderRecentOrders(
        data.recent_orders
    );
}


async function loadDashboard() {

    dashboardLoading.style.display =
        "block";

    dashboardError.style.display =
        "none";


    try {

        const data =
            await getAdminDashboard();


        renderDashboard(
            data
        );


    } catch (error) {

        dashboardError.textContent =
            error.message;

        dashboardError.style.display =
            "block";


    } finally {

        dashboardLoading.style.display =
            "none";
    }
}


logoutButton.addEventListener(
    "click",
    async () => {

        await adminLogout();

    }
);


async function initializeDashboard() {

    const isAdmin =
        await verifyAdmin();


    if (!isAdmin) {
        return;
    }


    await loadDashboard();
}


initializeDashboard();