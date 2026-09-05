const variantForm =
    document.getElementById(
        "variant-form"
    );

const productInput =
    document.getElementById(
        "product-id"
    );

const variantNameInput =
    document.getElementById(
        "variant-name"
    );

const variantSkuInput =
    document.getElementById(
        "variant-sku"
    );

const priceOverrideInput =
    document.getElementById(
        "price-override"
    );

const initialThresholdInput =
    document.getElementById(
        "initial-threshold"
    );

const thresholdCreateField =
    document.getElementById(
        "threshold-create-field"
    );

const variantFormTitle =
    document.getElementById(
        "variant-form-title"
    );

const variantSaveButton =
    document.getElementById(
        "variant-save-button"
    );

const cancelEditButton =
    document.getElementById(
        "cancel-edit"
    );

const formMessage =
    document.getElementById(
        "form-message"
    );


const inventorySearch =
    document.getElementById(
        "inventory-search"
    );

const productFilter =
    document.getElementById(
        "product-filter"
    );

const variantStatusFilter =
    document.getElementById(
        "variant-status-filter"
    );

const stockFilter =
    document.getElementById(
        "stock-filter"
    );

const applyFilterButton =
    document.getElementById(
        "apply-inventory-filter"
    );


const inventoryLoading =
    document.getElementById(
        "inventory-loading"
    );

const inventoryError =
    document.getElementById(
        "inventory-error"
    );

const inventoryTable =
    document.getElementById(
        "inventory-table"
    );


const movementSection =
    document.getElementById(
        "movement-section"
    );

const movementTitle =
    document.getElementById(
        "movement-title"
    );

const movementLoading =
    document.getElementById(
        "movement-loading"
    );

const movementTable =
    document.getElementById(
        "movement-table"
    );

const closeMovementsButton =
    document.getElementById(
        "close-movements"
    );

const logoutButton =
    document.getElementById(
        "logout-button"
    );


let editingVariantId = null;

let inventoryItems = [];

let products = [];


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


function showPageError(message) {
    inventoryError.textContent =
        message;

    inventoryError.style.display =
        "block";
}


function resetVariantForm() {
    editingVariantId = null;

    variantForm.reset();

    initialThresholdInput.value =
        "5";

    productInput.disabled =
        false;

    thresholdCreateField.style.display =
        "flex";

    variantFormTitle.textContent =
        "Add Product Variant";

    variantSaveButton.textContent =
        "Create Variant";

    cancelEditButton.style.display =
        "none";
}


function fillProductDropdowns() {
    productInput.innerHTML = "";

    productFilter.innerHTML = `
        <option value="">
            All Products
        </option>
    `;


    products.forEach(product => {

        if (product.is_active) {

            const createOption =
                document.createElement(
                    "option"
                );

            createOption.value =
                product.id;

            createOption.textContent =
                product.name;

            productInput.appendChild(
                createOption
            );
        }


        const filterOption =
            document.createElement(
                "option"
            );

        filterOption.value =
            product.id;

        filterOption.textContent =
            product.name;

        productFilter.appendChild(
            filterOption
        );
    });
}


function renderInventory() {
    inventoryTable.innerHTML = "";


    if (
        inventoryItems.length === 0
    ) {
        const row =
            document.createElement(
                "tr"
            );

        const cell =
            document.createElement(
                "td"
            );

        cell.colSpan = 8;

        cell.textContent =
            "No inventory records found.";

        row.appendChild(cell);

        inventoryTable.appendChild(
            row
        );

        return;
    }


    inventoryItems.forEach(item => {

        const row =
            document.createElement(
                "tr"
            );


        const productCell =
            document.createElement(
                "td"
            );

        productCell.textContent =
            item.product_name;


        const variantCell =
            document.createElement(
                "td"
            );

        variantCell.textContent =
            item.variant_name;


        const skuCell =
            document.createElement(
                "td"
            );

        skuCell.textContent =
            item.sku;


        const priceCell =
            document.createElement(
                "td"
            );

        priceCell.textContent =
            formatPrice(
                item.price_override
            );


        const quantityCell =
            document.createElement(
                "td"
            );

        const stockBadge =
            document.createElement(
                "span"
            );

        stockBadge.className =
            item.is_low_stock
                ? "stock-badge low-stock"
                : "stock-badge healthy-stock";

        stockBadge.textContent =
            item.quantity;

        quantityCell.appendChild(
            stockBadge
        );


        const thresholdCell =
            document.createElement(
                "td"
            );

        thresholdCell.textContent =
            item.low_stock_threshold;


        const statusCell =
            document.createElement(
                "td"
            );

        const statusBadge =
            document.createElement(
                "span"
            );

        statusBadge.className =
            item.is_active
                ? "status-badge active-status"
                : "status-badge inactive-status";

        statusBadge.textContent =
            item.is_active
                ? "Active"
                : "Inactive";

        statusCell.appendChild(
            statusBadge
        );


        const actionsCell =
            document.createElement(
                "td"
            );

        actionsCell.className =
            "inventory-actions";


        const editButton =
            createActionButton(
                "Edit",
                () => startEdit(item)
            );


        const adjustButton =
            createActionButton(
                "Adjust Stock",
                () => handleStockAdjustment(
                    item
                )
            );


        const thresholdButton =
            createActionButton(
                "Threshold",
                () => handleThresholdUpdate(
                    item
                )
            );


        const movementButton =
            createActionButton(
                "Movements",
                () => loadMovements(
                    item
                )
            );


        const statusButton =
            createActionButton(
                item.is_active
                    ? "Deactivate"
                    : "Activate",

                () => toggleVariantStatus(
                    item
                )
            );


        if (item.is_active) {
            statusButton.classList.add(
                "danger-table-button"
            );
        }


        actionsCell.append(
            editButton,
            adjustButton,
            thresholdButton,
            movementButton,
            statusButton
        );


        row.append(
            productCell,
            variantCell,
            skuCell,
            priceCell,
            quantityCell,
            thresholdCell,
            statusCell,
            actionsCell
        );


        inventoryTable.appendChild(
            row
        );
    });
}


function createActionButton(
    text,
    handler
) {
    const button =
        document.createElement(
            "button"
        );

    button.type = "button";

    button.textContent =
        text;

    button.className =
        "table-button";

    button.addEventListener(
        "click",
        handler
    );

    return button;
}


function startEdit(item) {
    editingVariantId =
        item.variant_id;


    productInput.value =
        item.product_id;

    productInput.disabled =
        true;


    variantNameInput.value =
        item.variant_name;


    variantSkuInput.value =
        item.sku;


    priceOverrideInput.value =
        item.price_override ?? "";


    thresholdCreateField.style.display =
        "none";


    variantFormTitle.textContent =
        "Edit Product Variant";


    variantSaveButton.textContent =
        "Save Changes";


    cancelEditButton.style.display =
        "inline-block";


    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
}


async function handleStockAdjustment(
    item
) {
    const quantityText =
        window.prompt(
            `Current stock: ${item.quantity}\n\nEnter quantity change.\nUse positive for stock in and negative for stock out.\n\nExample: 10 or -5`
        );


    if (quantityText === null) {
        return;
    }


    const quantityChange =
        Number(
            quantityText
        );


    if (
        !Number.isInteger(
            quantityChange
        ) ||
        quantityChange === 0
    ) {
        window.alert(
            "Quantity change must be a non-zero whole number."
        );

        return;
    }


    const reason =
        window.prompt(
            "Enter reason for stock adjustment:"
        );


    if (reason === null) {
        return;
    }


    if (
        reason.trim().length < 3
    ) {
        window.alert(
            "Reason must contain at least 3 characters."
        );

        return;
    }


    try {
        await adjustInventory(
            item.variant_id,
            quantityChange,
            reason.trim()
        );


        await loadInventory();


    } catch (error) {
        showPageError(
            error.message
        );
    }
}


async function handleThresholdUpdate(
    item
) {
    const thresholdText =
        window.prompt(
            "Enter new low-stock threshold:",
            item.low_stock_threshold
        );


    if (thresholdText === null) {
        return;
    }


    const threshold =
        Number(
            thresholdText
        );


    if (
        !Number.isInteger(
            threshold
        ) ||
        threshold < 0
    ) {
        window.alert(
            "Threshold must be zero or a positive whole number."
        );

        return;
    }


    try {
        await updateInventoryThreshold(
            item.variant_id,
            threshold
        );


        await loadInventory();


    } catch (error) {
        showPageError(
            error.message
        );
    }
}


async function toggleVariantStatus(
    item
) {
    try {
        await updateVariant(
            item.variant_id,
            {
                is_active:
                    !item.is_active,
            }
        );


        await loadInventory();


    } catch (error) {
        showPageError(
            error.message
        );
    }
}


async function loadMovements(item) {
    movementSection.style.display =
        "block";

    movementLoading.style.display =
        "block";

    movementTable.innerHTML = "";


    movementTitle.textContent =
        `Inventory Movements — ${item.product_name} / ${item.variant_name}`;


    try {
        const data =
            await getInventoryMovements(
                item.variant_id
            );


        if (data.items.length === 0) {
            const row =
                document.createElement(
                    "tr"
                );

            const cell =
                document.createElement(
                    "td"
                );

            cell.colSpan = 5;

            cell.textContent =
                "No inventory movements found.";

            row.appendChild(cell);

            movementTable.appendChild(
                row
            );

            return;
        }


        data.items.forEach(
            movement => {

                const row =
                    document.createElement(
                        "tr"
                    );


                const dateCell =
                    document.createElement(
                        "td"
                    );

                dateCell.textContent =
                    new Date(
                        movement.created_at
                    ).toLocaleString();


                const changeCell =
                    document.createElement(
                        "td"
                    );

                changeCell.textContent =
                    movement.quantity_change > 0
                        ? `+${movement.quantity_change}`
                        : movement.quantity_change;


                const balanceCell =
                    document.createElement(
                        "td"
                    );

                balanceCell.textContent =
                    movement.balance_after;


                const reasonCell =
                    document.createElement(
                        "td"
                    );

                reasonCell.textContent =
                    movement.reason;


                const userCell =
                    document.createElement(
                        "td"
                    );

                userCell.textContent =
                    movement.created_by_user_id;


                row.append(
                    dateCell,
                    changeCell,
                    balanceCell,
                    reasonCell,
                    userCell
                );


                movementTable.appendChild(
                    row
                );
            }
        );


        movementSection.scrollIntoView({
            behavior: "smooth",
        });


    } catch (error) {
        showPageError(
            error.message
        );

    } finally {
        movementLoading.style.display =
            "none";
    }
}


async function loadProducts() {
    const data =
        await getAdminProducts({
            page: 1,
            page_size: 100,
        });


    products =
        data.items;


    fillProductDropdowns();
}


async function loadInventory() {
    inventoryLoading.style.display =
        "block";

    inventoryError.style.display =
        "none";


    try {
        const data =
            await getAdminInventory({
                page: 1,
                page_size: 100,

                search:
                    inventorySearch.value
                        .trim(),

                product_id:
                    productFilter.value,

                is_active:
                    variantStatusFilter.value,

                low_stock:
                    stockFilter.value,
            });


        inventoryItems =
            data.items;


        renderInventory();


    } catch (error) {
        showPageError(
            error.message
        );

    } finally {
        inventoryLoading.style.display =
            "none";
    }
}


variantForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();


        const priceOverride =
            priceOverrideInput.value
                ? Number(
                    priceOverrideInput.value
                )
                : null;


        try {

            if (
                editingVariantId === null
            ) {

                const data = {
                    product_id:
                        Number(
                            productInput.value
                        ),

                    name:
                        variantNameInput.value
                            .trim(),

                    sku:
                        variantSkuInput.value
                            .trim()
                            .toUpperCase(),

                    price_override:
                        priceOverride,

                    low_stock_threshold:
                        Number(
                            initialThresholdInput.value
                        ),
                };


                await createVariant(
                    data
                );


                showFormMessage(
                    "Variant created successfully."
                );


            } else {

                const data = {
                    name:
                        variantNameInput.value
                            .trim(),

                    sku:
                        variantSkuInput.value
                            .trim()
                            .toUpperCase(),

                    price_override:
                        priceOverride,
                };


                await updateVariant(
                    editingVariantId,
                    data
                );


                showFormMessage(
                    "Variant updated successfully."
                );
            }


            resetVariantForm();

            await loadInventory();


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
        resetVariantForm();
    }
);


applyFilterButton.addEventListener(
    "click",
    async () => {
        await loadInventory();
    }
);


inventorySearch.addEventListener(
    "keydown",
    async event => {
        if (
            event.key === "Enter"
        ) {
            await loadInventory();
        }
    }
);


closeMovementsButton.addEventListener(
    "click",
    () => {
        movementSection.style.display =
            "none";
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
        await loadProducts();

        resetVariantForm();

        await loadInventory();


    } catch (error) {
        showPageError(
            error.message
        );

        inventoryLoading.style.display =
            "none";
    }
}


initializePage();