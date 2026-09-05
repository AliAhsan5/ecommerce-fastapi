const productDetail =
    document.getElementById(
        "product-detail"
    );

const variantsSection =
    document.getElementById(
        "variants-section"
    );

const variantsContainer =
    document.getElementById(
        "variants-container"
    );

const loadingMessage =
    document.getElementById(
        "loading-message"
    );

const errorMessage =
    document.getElementById(
        "error-message"
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


function getProductId() {
    const params =
        new URLSearchParams(
            window.location.search
        );

    const productId =
        Number(
            params.get("id")
        );

    if (
        !Number.isInteger(productId) ||
        productId <= 0
    ) {
        return null;
    }

    return productId;
}


function renderProduct(product) {
    productDetail.innerHTML = "";


    const imageColumn =
        document.createElement("div");

    imageColumn.className =
        "product-detail-image";


    if (product.image_url) {
        const image =
            document.createElement("img");

        image.src =
            product.image_url;

        image.alt =
            product.name;

        imageColumn.appendChild(image);

    } else {
        const placeholder =
            document.createElement(
                "div"
            );

        placeholder.className =
            "detail-image-placeholder";

        placeholder.textContent =
            "No Image";

        imageColumn.appendChild(
            placeholder
        );
    }


    const information =
        document.createElement("div");

    information.className =
        "product-detail-content";


    const name =
        document.createElement("h1");

    name.textContent =
        product.name;


    const sku =
        document.createElement("p");

    sku.className =
        "detail-sku";

    sku.textContent =
        `SKU: ${product.sku}`;


    const price =
        document.createElement("div");

    price.className =
        "detail-price";


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


    const description =
        document.createElement("p");

    description.className =
        "product-description";

    description.textContent =
        product.description ||
        "No description available.";


    information.append(
        name,
        sku,
        price,
        description
    );


    productDetail.append(
        imageColumn,
        information
    );
}


function renderVariants(
    variants,
    product
) {
    variantsContainer.innerHTML = "";

    if (variants.length === 0) {
        variantsSection.innerHTML = `
            <h2>Available Variants</h2>
            <p>No variants available.</p>
        `;

        return;
    }


    const selector =
        document.createElement(
            "select"
        );

    selector.id =
        "variant-selector";


    variants.forEach(variant => {
        const option =
            document.createElement(
                "option"
            );

        option.value =
            variant.id;


        const effectivePrice =
            variant.price_override ??
            product.sale_price ??
            product.price;


        option.textContent =
            `${variant.name} - ${formatPrice(effectivePrice)}`;


        selector.appendChild(
            option
        );
    });


    const quantity =
        document.createElement(
            "input"
        );

    quantity.type = "number";
    quantity.id = "cart-quantity";
    quantity.min = "1";
    quantity.value = "1";


    const addButton =
        document.createElement(
            "button"
        );

    addButton.className =
        "add-cart-button";

    addButton.textContent =
        "Add to Cart";


    const resultMessage =
        document.createElement(
            "p"
        );

    resultMessage.className =
        "cart-result-message";


    addButton.addEventListener(
        "click",
        async () => {
            const variantId =
                Number(
                    selector.value
                );

            const requestedQuantity =
                Number(
                    quantity.value
                );


            if (
                !Number.isInteger(
                    requestedQuantity
                ) ||
                requestedQuantity < 1
            ) {
                resultMessage.textContent =
                    "Enter a valid quantity.";

                return;
            }


            if (
                !getAccessToken() &&
                !getRefreshToken()
            ) {
                const next =
                    encodeURIComponent(
                        window.location.pathname +
                        window.location.search
                    );

                window.location.href =
                    `login.html?next=${next}`;

                return;
            }


            try {
                await addCartItem(
                    variantId,
                    requestedQuantity
                );

                resultMessage.textContent =
                    "Added to cart successfully.";

            } catch (error) {
                resultMessage.textContent =
                    error.message;
            }
        }
    );


    const cartLink =
        document.createElement("a");

    cartLink.href = "cart.html";
    cartLink.className =
        "view-button";

    cartLink.textContent =
        "View Cart";


    variantsContainer.append(
        selector,
        quantity,
        addButton,
        cartLink,
        resultMessage
    );
}


async function loadProductDetail() {
    const productId =
        getProductId();


    if (productId === null) {
        loadingMessage.style.display =
            "none";

        errorMessage.textContent =
            "Invalid product ID.";

        errorMessage.style.display =
            "block";

        return;
    }


    try {
        const [
            product,
            variants,
        ] = await Promise.all([
            getProduct(productId),
            getProductVariants(
                productId
            ),
        ]);


        renderProduct(product);

        renderVariants(
            variants,
            product
        );

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


loadProductDetail();