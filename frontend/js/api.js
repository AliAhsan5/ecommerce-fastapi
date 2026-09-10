const API_BASE_URL =
    "http://127.0.0.1:8000/api/v1";


function getAccessToken() {
    return sessionStorage.getItem(
        "access_token"
    );
}


function getRefreshToken() {
    return localStorage.getItem(
        "refresh_token"
    );
}


function saveTokens(tokens) {
    sessionStorage.setItem(
        "access_token",
        tokens.access_token
    );

    localStorage.setItem(
        "refresh_token",
        tokens.refresh_token
    );
}


function clearTokens() {
    sessionStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "refresh_token"
    );
}


async function refreshAccessToken() {
    const refreshToken =
        getRefreshToken();

    if (!refreshToken) {
        throw new Error(
            "Please login first."
        );
    }

    const response = await fetch(
        `${API_BASE_URL}/auth/refresh`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify({
                refresh_token:
                    refreshToken,
            }),
        }
    );

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        clearTokens();

        throw new Error(
            data?.message ||
            "Your session has expired."
        );
    }

    saveTokens(data);

    return data.access_token;
}


async function apiRequest(
    endpoint,
    options = {},
    requiresAuth = false,
    retry = true
) {
    const headers = {
        "Content-Type":
            "application/json",

        ...options.headers,
    };


    if (requiresAuth) {
        if (!getAccessToken()) {
            if (!getRefreshToken()) {
                throw new Error(
                    "Please login first."
                );
            }

            await refreshAccessToken();
        }

        headers.Authorization =
            `Bearer ${getAccessToken()}`;
    }


    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers,
        }
    );


    if (
        response.status === 401 &&
        requiresAuth &&
        retry &&
        getRefreshToken()
    ) {
        await refreshAccessToken();

        return apiRequest(
            endpoint,
            options,
            true,
            false
        );
    }


    let data = null;

    if (response.status !== 204) {
        try {
            data =
                await response.json();
        } catch {
            data = null;
        }
    }


    if (!response.ok) {
        throw new Error(
            data?.message ||
            "Something went wrong."
        );
    }


    return data;
}


/* =========================
   AUTH
========================= */

async function loginUser(
    email,
    password
) {
    const tokens =
        await apiRequest(
            "/auth/login",
            {
                method: "POST",

                body: JSON.stringify({
                    email,
                    password,
                }),
            }
        );

    saveTokens(tokens);

    return tokens;
}


async function logoutUser() {
    const refreshToken =
        getRefreshToken();

    try {
        if (refreshToken) {
            await apiRequest(
                "/auth/logout",
                {
                    method: "POST",

                    body: JSON.stringify({
                        refresh_token:
                            refreshToken,
                    }),
                }
            );
        }
    } finally {
        clearTokens();
    }
}


/* =========================
   PUBLIC CATALOG
========================= */

async function getProducts(
    filters = {}
) {
    const params =
        new URLSearchParams();

    Object.entries(filters).forEach(
        ([key, value]) => {
            if (
                value !== null &&
                value !== undefined &&
                value !== ""
            ) {
                params.append(
                    key,
                    value
                );
            }
        }
    );

    return apiRequest(
        `/products?${params.toString()}`
    );
}


async function getProduct(
    productId
) {
    return apiRequest(
        `/products/${productId}`
    );
}


async function getProductVariants(
    productId
) {
    return apiRequest(
        `/variants/product/${productId}`
    );
}


async function getCategories() {
    return apiRequest(
        "/categories?page=1&page_size=100"
    );
}


async function getBrands() {
    return apiRequest(
        "/brands?page=1&page_size=100"
    );
}


/* =========================
   CART
========================= */

async function getCart() {
    return apiRequest(
        "/cart",
        {},
        true
    );
}


async function addCartItem(
    variantId,
    quantity
) {
    return apiRequest(
        "/cart/items",
        {
            method: "POST",

            body: JSON.stringify({
                variant_id: variantId,
                quantity,
            }),
        },
        true
    );
}


async function updateCartItem(
    itemId,
    quantity
) {
    return apiRequest(
        `/cart/items/${itemId}`,
        {
            method: "PATCH",

            body: JSON.stringify({
                quantity,
            }),
        },
        true
    );
}


async function removeCartItem(
    itemId
) {
    return apiRequest(
        `/cart/items/${itemId}`,
        {
            method: "DELETE",
        },
        true
    );
}


async function clearCart() {
    return apiRequest(
        "/cart/items",
        {
            method: "DELETE",
        },
        true
    );
}


/* =========================
   ADDRESSES
========================= */

async function getAddresses() {
    return apiRequest(
        "/addresses",
        {},
        true
    );
}


/* =========================
   CHECKOUT / ORDERS
========================= */

async function checkoutOrder(
    addressId,
    idempotencyKey
) {
    return apiRequest(
        "/orders/checkout",
        {
            method: "POST",

            body: JSON.stringify({
                address_id:
                    addressId,

                idempotency_key:
                    idempotencyKey,

                payment_method:
                    "cod",
            }),
        },
        true
    );
}


async function getOrders(
    page = 1,
    pageSize = 20
) {
    return apiRequest(
        `/orders?page=${page}&page_size=${pageSize}`,
        {},
        true
    );
}


async function getOrder(
    orderId
) {
    return apiRequest(
        `/orders/${orderId}`,
        {},
        true
    );
}


/* =========================
   ADMIN CATEGORIES
========================= */

async function getAdminCategories() {
    return apiRequest(
        "/admin/categories?page=1&page_size=100",
        {},
        true
    );
}


async function createCategory(
    categoryData
) {
    return apiRequest(
        "/categories",
        {
            method: "POST",

            body: JSON.stringify(
                categoryData
            ),
        },
        true
    );
}


async function updateCategory(
    categoryId,
    categoryData
) {
    return apiRequest(
        `/categories/${categoryId}`,
        {
            method: "PATCH",

            body: JSON.stringify(
                categoryData
            ),
        },
        true
    );
}


/* =========================
   ADMIN BRANDS
========================= */

async function getAdminBrands() {
    return apiRequest(
        "/admin/brands?page=1&page_size=100",
        {},
        true
    );
}


async function createBrand(
    brandData
) {
    return apiRequest(
        "/brands",
        {
            method: "POST",

            body: JSON.stringify(
                brandData
            ),
        },
        true
    );
}


async function updateBrand(
    brandId,
    brandData
) {
    return apiRequest(
        `/brands/${brandId}`,
        {
            method: "PATCH",

            body: JSON.stringify(
                brandData
            ),
        },
        true
    );
}

async function getAdminProducts(
    filters = {}
) {
    const params =
        new URLSearchParams();


    Object.entries(filters).forEach(
        ([key, value]) => {
            if (
                value !== null &&
                value !== undefined &&
                value !== ""
            ) {
                params.append(
                    key,
                    value
                );
            }
        }
    );


    return apiRequest(
        `/admin/products?${params.toString()}`,
        {},
        true
    );
}


async function createProduct(
    productData
) {
    return apiRequest(
        "/products",
        {
            method: "POST",

            body: JSON.stringify(
                productData
            ),
        },
        true
    );
}


async function updateProduct(
    productId,
    productData
) {
    return apiRequest(
        `/products/${productId}`,
        {
            method: "PATCH",

            body: JSON.stringify(
                productData
            ),
        },
        true
    );
}

async function getAdminInventory(
    filters = {}
) {
    const params =
        new URLSearchParams();


    Object.entries(filters).forEach(
        ([key, value]) => {
            if (
                value !== null &&
                value !== undefined &&
                value !== ""
            ) {
                params.append(
                    key,
                    value
                );
            }
        }
    );


    return apiRequest(
        `/admin/inventory?${params.toString()}`,
        {},
        true
    );
}


async function createVariant(
    variantData
) {
    return apiRequest(
        "/variants",
        {
            method: "POST",

            body: JSON.stringify(
                variantData
            ),
        },
        true
    );
}


async function updateVariant(
    variantId,
    variantData
) {
    return apiRequest(
        `/variants/${variantId}`,
        {
            method: "PATCH",

            body: JSON.stringify(
                variantData
            ),
        },
        true
    );
}


async function adjustInventory(
    variantId,
    quantityChange,
    reason
) {
    return apiRequest(
        `/inventory/${variantId}/adjust`,
        {
            method: "POST",

            body: JSON.stringify({
                quantity_change:
                    quantityChange,

                reason:
                    reason,
            }),
        },
        true
    );
}


async function updateInventoryThreshold(
    variantId,
    threshold
) {
    return apiRequest(
        `/inventory/${variantId}/threshold`,
        {
            method: "PATCH",

            body: JSON.stringify({
                low_stock_threshold:
                    threshold,
            }),
        },
        true
    );
}


async function getInventoryMovements(
    variantId
) {
    return apiRequest(
        `/inventory/${variantId}/movements?page=1&page_size=100`,
        {},
        true
    );
}

async function getAdminOrders(
    filters = {}
) {
    const params =
        new URLSearchParams();


    Object.entries(filters).forEach(
        ([key, value]) => {
            if (
                value !== null &&
                value !== undefined &&
                value !== ""
            ) {
                params.append(
                    key,
                    value
                );
            }
        }
    );


    return apiRequest(
        `/admin/orders?${params.toString()}`,
        {},
        true
    );
}


async function getAdminOrder(
    orderId
) {
    return apiRequest(
        `/admin/orders/${orderId}`,
        {},
        true
    );
}


async function updateAdminOrderStatus(
    orderId,
    status
) {
    return apiRequest(
        `/admin/orders/${orderId}/status`,
        {
            method: "PATCH",

            body: JSON.stringify({
                status,
            }),
        },
        true
    );
}

async function getAdminDashboard() {
    return apiRequest(
        "/admin/dashboard",
        {},
        true
    );
}

async function sendChatMessage(
    message,
    history = []
) {
    return apiRequest(
        "/chat",
        {
            method: "POST",

            body: JSON.stringify({
                message: message,
                history: history,
            }),
        }
    );
}