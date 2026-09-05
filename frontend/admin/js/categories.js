const categoryForm =
    document.getElementById(
        "category-form"
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
        "categories-table"
    );

const logoutButton =
    document.getElementById(
        "logout-button"
    );


let editingCategoryId = null;

let categories = [];


function resetForm() {
    editingCategoryId = null;

    categoryForm.reset();

    formTitle.textContent =
        "Add Category";

    saveButton.textContent =
        "Create Category";

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


function renderCategories() {
    tableBody.innerHTML = "";


    categories.forEach(category => {
        const row =
            document.createElement(
                "tr"
            );


        const idCell =
            document.createElement(
                "td"
            );

        idCell.textContent =
            category.id;


        const nameCell =
            document.createElement(
                "td"
            );

        nameCell.textContent =
            category.name;


        const slugCell =
            document.createElement(
                "td"
            );

        slugCell.textContent =
            category.slug;


        const statusCell =
            document.createElement(
                "td"
            );

        const badge =
            document.createElement(
                "span"
            );

        badge.className =
            category.is_active
                ? "status-badge active-status"
                : "status-badge inactive-status";

        badge.textContent =
            category.is_active
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
                editingCategoryId =
                    category.id;

                nameInput.value =
                    category.name;

                slugInput.value =
                    category.slug;

                formTitle.textContent =
                    "Edit Category";

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
            category.is_active
                ? "Deactivate"
                : "Activate";

        statusButton.className =
            category.is_active
                ? "table-button danger-table-button"
                : "table-button";


        statusButton.addEventListener(
            "click",
            async () => {
                try {
                    await updateCategory(
                        category.id,
                        {
                            is_active:
                                !category.is_active,
                        }
                    );

                    await loadCategories();

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


async function loadCategories() {
    loading.style.display =
        "block";

    pageError.style.display =
        "none";


    try {
        const data =
            await getAdminCategories();

        categories =
            data.items;

        renderCategories();

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


categoryForm.addEventListener(
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
                editingCategoryId === null
            ) {
                await createCategory(
                    data
                );

                showFormMessage(
                    "Category created successfully."
                );

            } else {
                await updateCategory(
                    editingCategoryId,
                    data
                );

                showFormMessage(
                    "Category updated successfully."
                );
            }


            resetForm();

            await loadCategories();


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

    await loadCategories();
}


initializePage();