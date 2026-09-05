const productsContainer =
    document.getElementById(
        "products-container"
    );

const loadingMessage =
    document.getElementById(
        "loading-message"
    );

const errorMessage =
    document.getElementById(
        "error-message"
    );


const searchInput =
    document.getElementById(
        "search-input"
    );

const categoryFilter =
    document.getElementById(
        "category-filter"
    );

const brandFilter =
    document.getElementById(
        "brand-filter"
    );

const minPrice =
    document.getElementById(
        "min-price"
    );

const maxPrice =
    document.getElementById(
        "max-price"
    );

const sortFilter =
    document.getElementById(
        "sort-filter"
    );


const applyFiltersButton =
    document.getElementById(
        "apply-filters"
    );

const resetFiltersButton =
    document.getElementById(
        "reset-filters"
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


let currentPage = 1;
const pageSize = 6;
let totalProducts = 0;


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


function createProductCard(product) {
    const card = document.createElement(
        "article"
    );

    card.className = "product-card";


    const imageArea =
        document.createElement("div");


    if (product.image_url) {
        const image =
            document.createElement("img");

        image.src = product.image_url;
        image.alt = product.name;
        image.className =
            "product-image";

        imageArea.appendChild(image);

    } else {
        const placeholder =
            document.createElement("div");

        placeholder.className =
            "product-image-placeholder";

        placeholder.textContent =
            "No Image";

        imageArea.appendChild(
            placeholder
        );
    }


    const content =
        document.createElement("div");

    content.className =
        "product-content";


    const name =
        document.createElement("h2");

    name.textContent =
        product.name;


    const sku =
        document.createElement("p");

    sku.className = "sku";

    sku.textContent =
        `SKU: ${product.sku}`;


    const price =
        document.createElement("div");

    price.className = "price";


    const currentPrice =
        document.createElement("span");

    currentPrice.textContent =
        formatPrice(
            product.sale_price ??
            product.price
        );

    price.appendChild(
        currentPrice
    );


    if (product.sale_price) {
        const oldPrice =
            document.createElement("span");

        oldPrice.className =
            "old-price";

        oldPrice.textContent =
            formatPrice(
                product.price
            );

        price.appendChild(
            oldPrice
        );
    }


    const viewButton =
        document.createElement("a");

    viewButton.className =
        "view-button";

    viewButton.href =
        `product.html?id=${product.id}`;

    viewButton.textContent =
        "View Product";


    content.append(
        name,
        sku,
        price,
        viewButton
    );


    card.append(
        imageArea,
        content
    );

    return card;
}


function renderProducts(products) {
    productsContainer.innerHTML = "";

    if (products.length === 0) {
        const message =
            document.createElement("p");

        message.className =
            "empty-message";

        message.textContent =
            "No products found.";

        productsContainer.appendChild(
            message
        );

        return;
    }

    products.forEach(product => {
        productsContainer.appendChild(
            createProductCard(product)
        );
    });
}


function getFilterValues() {
    return {
        page: currentPage,
        page_size: pageSize,
        search: searchInput.value.trim(),
        category_id:
            categoryFilter.value,
        brand_id:
            brandFilter.value,
        min_price:
            minPrice.value,
        max_price:
            maxPrice.value,
        sort_by:
            sortFilter.value,
    };
}


function updatePagination() {
    const totalPages = Math.max(
        1,
        Math.ceil(
            totalProducts / pageSize
        )
    );

    pageInfo.textContent =
        `Page ${currentPage} of ${totalPages}`;

    previousPageButton.disabled =
        currentPage <= 1;

    nextPageButton.disabled =
        currentPage >= totalPages;
}


async function loadProducts() {
    loadingMessage.style.display =
        "block";

    errorMessage.style.display =
        "none";

    try {
        const data = await getProducts(
            getFilterValues()
        );

        totalProducts = data.total;

        renderProducts(
            data.items
        );

        updatePagination();

    } catch (error) {
        errorMessage.textContent =
            error.message;

        errorMessage.style.display =
            "block";

    } finally {
        loadingMessage.style.display =
            "none";
    }
}


async function loadCategories() {
    const data =
        await getCategories();

    data.items.forEach(category => {
        const option =
            document.createElement(
                "option"
            );

        option.value = category.id;
        option.textContent =
            category.name;

        categoryFilter.appendChild(
            option
        );
    });
}


async function loadBrands() {
    const data =
        await getBrands();

    data.items.forEach(brand => {
        const option =
            document.createElement(
                "option"
            );

        option.value = brand.id;
        option.textContent =
            brand.name;

        brandFilter.appendChild(
            option
        );
    });
}


applyFiltersButton.addEventListener(
    "click",
    () => {
        currentPage = 1;
        loadProducts();
    }
);


resetFiltersButton.addEventListener(
    "click",
    () => {
        searchInput.value = "";
        categoryFilter.value = "";
        brandFilter.value = "";
        minPrice.value = "";
        maxPrice.value = "";
        sortFilter.value = "newest";

        currentPage = 1;

        loadProducts();
    }
);


previousPageButton.addEventListener(
    "click",
    () => {
        if (currentPage > 1) {
            currentPage--;
            loadProducts();
        }
    }
);


nextPageButton.addEventListener(
    "click",
    () => {
        const totalPages =
            Math.ceil(
                totalProducts /
                pageSize
            );

        if (
            currentPage <
            totalPages
        ) {
            currentPage++;
            loadProducts();
        }
    }
);


searchInput.addEventListener(
    "keydown",
    event => {
        if (event.key === "Enter") {
            currentPage = 1;
            loadProducts();
        }
    }
);


async function initializeCatalog() {
    try {
        await Promise.all([
            loadCategories(),
            loadBrands(),
        ]);

        await loadProducts();

    } catch (error) {
        errorMessage.textContent =
            error.message;

        errorMessage.style.display =
            "block";
    }
}


initializeCatalog();