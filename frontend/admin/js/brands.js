const brandForm =
    document.getElementById(
        "brand-form"
    );

const nameInput =
    document.getElementById(
        "name"
    );

const slugInput =
    document.getElementById(
        "slug"
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
        "brands-table"
    );

const logoutButton =
    document.getElementById(
        "logout-button"
    );


let editingBrandId = null;

let brands = [];


function resetForm() {
    editingBrandId = null;

    brandForm.reset();

    formTitle.textContent =
        "Add Brand";

    saveButton.textContent =
        "Create Brand";

    cancelEditButton.style.display =
        "none";
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


function renderBrands() {
    tableBody.innerHTML = "";


    brands.forEach(brand => {
        const row =
            document.createElement(
                "tr"
            );


        const idCell =
            document.createElement(
                "td"
            );

        idCell.textContent =
            brand.id;


        const nameCell =
            document.createElement(
                "td"
            );

        nameCell.textContent =
            brand.name;


        const slugCell =
            document.createElement(
                "td"
            );

        slugCell.textContent =
            brand.slug;


        const statusCell =
            document.createElement(
                "td"
            );

        const badge =
            document.createElement(
                "span"
            );

        badge.className =
            brand.is_active
                ? "status-badge active-status"
                : "status-badge inactive-status";

        badge.textContent =
            brand.is_active
                ? "Active"
                : "Inactive";

        statusCell.appendChild(
            badge
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
                editingBrandId =
                    brand.id;

                nameInput.value =
                    brand.name;

                slugInput.value =
                    brand.slug;

                formTitle.textContent =
                    "Edit Brand";

                saveButton.textContent =
                    "Save Changes";

                cancelEditButton.style.display =
                    "inline-block";

                window.scrollTo({
                    top: 0,
                    behavior: "smooth",
                });
            }
        );


        const statusButton =
            document.createElement(
                "button"
            );

        statusButton.textContent =
            brand.is_active
                ? "Deactivate"
                : "Activate";

        statusButton.className =
            brand.is_active
                ? "table-button danger-table-button"
                : "table-button";


        statusButton.addEventListener(
            "click",
            async () => {
                try {
                    await updateBrand(
                        brand.id,
                        {
                            is_active:
                                !brand.is_active,
                        }
                    );

                    await loadBrands();

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


        row.append(
            idCell,
            nameCell,
            slugCell,
            statusCell,
            actionsCell
        );


        tableBody.appendChild(row);
    });
}


async function loadBrands() {
    loading.style.display =
        "block";

    pageError.style.display =
        "none";


    try {
        const data =
            await getAdminBrands();

        brands =
            data.items;

        renderBrands();

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


brandForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();


        const data = {
            name:
                nameInput.value.trim(),

            slug:
                slugInput.value
                    .trim()
                    .toLowerCase(),
        };


        try {
            if (
                editingBrandId === null
            ) {
                await createBrand(
                    data
                );

                showFormMessage(
                    "Brand created successfully."
                );

            } else {
                await updateBrand(
                    editingBrandId,
                    data
                );

                showFormMessage(
                    "Brand updated successfully."
                );
            }


            resetForm();

            await loadBrands();


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

    resetForm();

    await loadBrands();
}


initializePage();