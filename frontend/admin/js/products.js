const productForm =
    document.getElementById(
        "product-form"
    );

const nameInput =
    document.getElementById(
        "product-name"
    );

const slugInput =
    document.getElementById(
        "product-slug"
    );

const skuInput =
    document.getElementById(
        "product-sku"
    );

const categoryInput =
    document.getElementById(
        "category-id"
    );

const brandInput =
    document.getElementById(
        "brand-id"
    );

const priceInput =
    document.getElementById(
        "product-price"
    );

const salePriceInput =
    document.getElementById(
        "sale-price"
    );

const imageUrlInput =
    document.getElementById(
        "image-url"
    );

const descriptionInput =
    document.getElementById(
        "description"
    );


const searchFilter =
    document.getElementById(
        "search-filter"
    );

const categoryFilter =
    document.getElementById(
        "category-filter"
    );

const brandFilter =
    document.getElementById(
        "brand-filter"
    );

const statusFilter =
    document.getElementById(
        "status-filter"
    );


const applyFilterButton =
    document.getElementById(
        "apply-filter"
    );

const saveButton =
    document.getElementById(
        "save-button"
    );

const cancelEditButton =
    document.getElementById(
        "cancel-edit"
    );

const formTitle =
    document.getElementById(
        "form-title"
    );

const formMessage =
    document.getElementById(
        "form-message"
    );

const pageError =
    document.getElementById(
        "page-error"
    );

const loading =
    document.getElementById(
        "loading"
    );

const tableBody =
    document.getElementById(
        "products-table"
    );

const logoutButton =
    document.getElementById(
        "logout-button"
    );


let editingProductId = null;

let products = [];
let categories = [];
let brands = [];


function formatPrice(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "-";
    }

    return Number(value).toLocaleString(
        "en-PK",
        {
            style: "currency",
            currency: "PKR",
            maximumFractionDigits: 0,
        }
    );
}


function getCategoryName(id) {
    const category =
        categories.find(
            item => item.id === id
        );

    return category
        ? category.name
        : `#${id}`;
}


function getBrandName(id) {
    const brand =
        brands.find(
            item => item.id === id
        );

    return brand
        ? brand.name
        : `#${id}`;
}


function showFormMessage(
    message,
    isError = false
) {
    formMessage.textContent =
        message;

    formMessage.className =
        isError
            ? "admin-message admin-message-error"
            : "admin-message admin-message-success";

    formMessage.style.display =
        "block";
}


function resetForm() {
    editingProductId = null;

    productForm.reset();

    formTitle.textContent =
        "Add Product";

    saveButton.textContent =
        "Create Product";

    cancelEditButton.style.display =
        "none";
}


function fillDropdowns() {
    categoryInput.innerHTML = "";

    brandInput.innerHTML = "";


    categoryFilter.innerHTML = `
        <option value="">
            All Categories
        </option>
    `;


    brandFilter.innerHTML = `
        <option value="">
            All Brands
        </option>
    `;


    categories.forEach(category => {
        if (category.is_active) {

            const formOption =
                document.createElement(
                    "option"
                );

            formOption.value =
                category.id;

            formOption.textContent =
                category.name;

            categoryInput.appendChild(
                formOption
            );
        }


        const filterOption =
            document.createElement(
                "option"
            );

        filterOption.value =
            category.id;

        filterOption.textContent =
            category.name;

        categoryFilter.appendChild(
            filterOption
        );
    });


    brands.forEach(brand => {
        if (brand.is_active) {

            const formOption =
                document.createElement(
                    "option"
                );

            formOption.value =
                brand.id;

            formOption.textContent =
                brand.name;

            brandInput.appendChild(
                formOption
            );
        }


        const filterOption =
            document.createElement(
                "option"
            );

        filterOption.value =
            brand.id;

        filterOption.textContent =
            brand.name;

        brandFilter.appendChild(
            filterOption
        );
    });
}


function renderProducts() {
    tableBody.innerHTML = "";


    if (products.length === 0) {
        const row =
            document.createElement(
                "tr"
            );

        const cell =
            document.createElement(
                "td"
            );

        cell.colSpan = 9;

        cell.textContent =
            "No products found.";

        row.appendChild(cell);

        tableBody.appendChild(row);

        return;
    }


    products.forEach(product => {
        const row =
            document.createElement(
                "tr"
            );


        const values = [
            product.id,
            product.name,
            product.sku,
            getCategoryName(
                product.category_id
            ),
            getBrandName(
                product.brand_id
            ),
            formatPrice(
                product.price
            ),
            formatPrice(
                product.sale_price
            ),
        ];


        values.forEach(value => {
            const cell =
                document.createElement(
                    "td"
                );

            cell.textContent =
                value;

            row.appendChild(cell);
        });


        const statusCell =
            document.createElement(
                "td"
            );

        const badge =
            document.createElement(
                "span"
            );

        badge.className =
            product.is_active
                ? "status-badge active-status"
                : "status-badge inactive-status";

        badge.textContent =
            product.is_active
                ? "Active"
                : "Inactive";

        statusCell.appendChild(
            badge
        );

        row.appendChild(
            statusCell
        );


        const actionsCell =
            document.createElement(
                "td"
            );


        const editButton =
            document.createElement(
                "button"
            );

        editButton.textContent =
            "Edit";

        editButton.className =
            "table-button";


        editButton.addEventListener(
            "click",
            () => {
                startEdit(product);
            }
        );


        const statusButton =
            document.createElement(
                "button"
            );

        statusButton.textContent =
            product.is_active
                ? "Deactivate"
                : "Activate";

        statusButton.className =
            product.is_active
                ? "table-button danger-table-button"
                : "table-button";


        statusButton.addEventListener(
            "click",
            async () => {
                try {
                    await updateProduct(
                        product.id,
                        {
                            is_active:
                                !product.is_active,
                        }
                    );

                    await loadProducts();

                } catch (error) {
                    pageError.textContent =
                        error.message;

                    pageError.style.display =
                        "block";
                }
            }
        );


        actionsCell.append(
            editButton,
            statusButton
        );


        row.appendChild(
            actionsCell
        );


        tableBody.appendChild(row);
    });
}


function startEdit(product) {
    editingProductId =
        product.id;

    nameInput.value =
        product.name;

    slugInput.value =
        product.slug;

    skuInput.value =
        product.sku;

    categoryInput.value =
        product.category_id;

    brandInput.value =
        product.brand_id;

    priceInput.value =
        product.price;

    salePriceInput.value =
        product.sale_price ?? "";

    imageUrlInput.value =
        product.image_url ?? "";

    descriptionInput.value =
        product.description ?? "";


    formTitle.textContent =
        "Edit Product";

    saveButton.textContent =
        "Save Changes";

    cancelEditButton.style.display =
        "inline-block";


    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
}


async function loadCatalogOptions() {
    const [
        categoryData,
        brandData,
    ] = await Promise.all([
        getAdminCategories(),
        getAdminBrands(),
    ]);


    categories =
        categoryData.items;

    brands =
        brandData.items;


    fillDropdowns();
}


async function loadProducts() {
    loading.style.display =
        "block";

    pageError.style.display =
        "none";


    try {
        const filters = {
            page: 1,
            page_size: 100,

            search:
                searchFilter.value
                    .trim(),

            category_id:
                categoryFilter.value,

            brand_id:
                brandFilter.value,

            is_active:
                statusFilter.value,
        };


        const data =
            await getAdminProducts(
                filters
            );


        products =
            data.items;


        renderProducts();


    } catch (error) {
        pageError.textContent =
            error.message;

        pageError.style.display =
            "block";

    } finally {
        loading.style.display =
            "none";
    }
}


productForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();


        const salePrice =
            salePriceInput.value
                ? Number(
                    salePriceInput.value
                )
                : null;


        const data = {
            category_id:
                Number(
                    categoryInput.value
                ),

            brand_id:
                Number(
                    brandInput.value
                ),

            name:
                nameInput.value.trim(),

            slug:
                slugInput.value
                    .trim()
                    .toLowerCase(),

            sku:
                skuInput.value
                    .trim()
                    .toUpperCase(),

            description:
                descriptionInput.value
                    .trim() || null,

            price:
                Number(
                    priceInput.value
                ),

            sale_price:
                salePrice,

            image_url:
                imageUrlInput.value
                    .trim() || null,
        };


        try {
            if (
                editingProductId === null
            ) {
                await createProduct(
                    data
                );

                showFormMessage(
                    "Product created successfully."
                );

            } else {
                await updateProduct(
                    editingProductId,
                    data
                );

                showFormMessage(
                    "Product updated successfully."
                );
            }


            resetForm();

            await loadProducts();


        } catch (error) {
            showFormMessage(
                error.message,
                true
            );
        }
    }
);


cancelEditButton.addEventListener(
    "click",
    () => {
        resetForm();
    }
);


applyFilterButton.addEventListener(
    "click",
    async () => {
        await loadProducts();
    }
);


searchFilter.addEventListener(
    "keydown",
    async event => {
        if (event.key === "Enter") {
            await loadProducts();
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


    try {
        await loadCatalogOptions();

        resetForm();

        await loadProducts();

    } catch (error) {
        pageError.textContent =
            error.message;

        pageError.style.display =
            "block";

        loading.style.display =
            "none";
    }
}


initializePage();