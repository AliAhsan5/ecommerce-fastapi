let chatHistory = [];


const chatToggleButton =
    document.getElementById(
        "chat-toggle-button"
    );

const chatWindow =
    document.getElementById(
        "chat-window"
    );

const chatCloseButton =
    document.getElementById(
        "chat-close-button"
    );

const chatForm =
    document.getElementById(
        "chat-form"
    );

const chatInput =
    document.getElementById(
        "chat-input"
    );

const chatMessages =
    document.getElementById(
        "chat-messages"
    );

const chatSendButton =
    document.getElementById(
        "chat-send-button"
    );

function isOrderIntent(
    message
) {
    const normalized =
        message
            .trim()
            .toLowerCase();

    return /\borders?\b/.test(
        normalized
    );
}

function addMessage(
    text,
    type
) {

    const message =
        document.createElement(
            "div"
        );

    message.className =
        `chat-message ${type}`;

    message.textContent =
        text;

    chatMessages.appendChild(
        message
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function addToChatHistory(
    role,
    content
) {

    chatHistory.push({
        role: role,
        content: content,
    });


    if (
        chatHistory.length > 6
    ) {

        chatHistory =
            chatHistory.slice(-6);
    }
}


function formatPrice(
    value
) {

    return Number(
        value
    ).toLocaleString(
        "en-PK",
        {
            style: "currency",
            currency: "PKR",
            maximumFractionDigits: 0,
        }
    );
}


function renderChatProducts(
    products
) {

    if (
        !products ||
        products.length === 0
    ) {
        return;
    }


    const container =
        document.createElement(
            "div"
        );

    container.className =
        "chat-product-list";


    products.forEach(
        product => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "chat-product-card";


            if (
                product.image_url
            ) {

                const image =
                    document.createElement(
                        "img"
                    );

                image.src =
                    product.image_url;

                image.alt =
                    product.name;

                card.appendChild(
                    image
                );
            }


            const content =
                document.createElement(
                    "div"
                );

            content.className =
                "chat-product-content";


            const name =
                document.createElement(
                    "strong"
                );

            name.textContent =
                product.name;


            const variant =
                document.createElement(
                    "span"
                );

            variant.textContent =
                `Variant: ${product.variant_name}`;


            const price =
                document.createElement(
                    "span"
                );

            price.textContent =
                formatPrice(
                    product.effective_price
                );


            const stock =
                document.createElement(
                    "span"
                );

            stock.textContent =
                product.stock_quantity > 0
                    ? (
                        `In stock: ` +
                        `${product.stock_quantity}`
                    )
                    : "Out of stock";


            const link =
                document.createElement(
                    "a"
                );

            link.href =
                `product.html?id=${product.id}`;

            link.textContent =
                "View Product";

            link.className =
                "chat-product-link";


            content.append(
                name,
                variant,
                price,
                stock,
                link
            );


            card.appendChild(
                content
            );

            container.appendChild(
                card
            );
        }
    );


    chatMessages.appendChild(
        container
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function setSendingState(
    isSending
) {

    chatInput.disabled =
        isSending;

    chatSendButton.disabled =
        isSending;

    chatSendButton.textContent =
        isSending
            ? "..."
            : "Send";
}


function getChatErrorMessage(
    error
) {

    const message =
        String(
            error?.message || ""
        ).toLowerCase();


    if (
        message.includes("401")
        ||
        message.includes(
            "not authenticated"
        )
        ||
        message.includes(
            "authentication"
        )
        ||
        message.includes(
            "login required"
        )
        ||
        message.includes("please login first")
    ) {

        return (
            "Please log in first to access " +
            "your private order information."
        );
    }


    if (
        message.includes("429")
        ||
        message.includes(
            "too many chat requests"
        )
    ) {

        return (
            "You're sending messages too quickly. " +
            "Please wait a moment and try again."
        );
    }


    if (
        message.includes("503")
        ||
        message.includes(
            "temporarily unavailable"
        )
        ||
        message.includes("busy")
    ) {

        return (
            "Our AI assistant is temporarily busy. " +
            "Please try again in a moment."
        );
    }


    if (
        message.includes(
            "failed to fetch"
        )
        ||
        message.includes(
            "network"
        )
    ) {

        return (
            "Unable to connect to the server. " +
            "Please check your connection and try again."
        );
    }


    return (
        "Sorry, something went wrong. " +
        "Please try again."
    );
}


chatToggleButton.addEventListener(
    "click",
    () => {

        chatWindow.classList.toggle(
            "chat-open"
        );


        if (
            chatWindow.classList.contains(
                "chat-open"
            )
        ) {

            chatInput.focus();
        }
    }
);


chatCloseButton.addEventListener(
    "click",
    () => {

        chatWindow.classList.remove(
            "chat-open"
        );
    }
);


chatForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();


        const message =
            chatInput.value.trim();


        if (!message) {
            return;
        }


        addMessage(
            message,
            "user-message"
        );


        const requestHistory =
            [...chatHistory];


        chatInput.value = "";


        setSendingState(
            true
        );


        const typingMessage =
            document.createElement(
                "div"
            );

        typingMessage.className =
            "chat-message assistant-message";

        typingMessage.textContent =
            "Thinking...";


        chatMessages.appendChild(
            typingMessage
        );


        chatMessages.scrollTop =
            chatMessages.scrollHeight;


        try {

            let response;


            if (
                isOrderIntent(
                    message
                )
            ) {

                response =
                    await sendOrderChatMessage(
                        message,
                        requestHistory
                    );

            } else {

                response =
                    await sendChatMessage(
                        message,
                        requestHistory
                    );
            }


            typingMessage.remove();


            addMessage(
                response.reply,
                "assistant-message"
            );


            addToChatHistory(
                "user",
                message
            );


            addToChatHistory(
                "assistant",
                response.reply
            );


            renderChatProducts(
                response.products
            );


        } catch (error) {

            typingMessage.remove();


            console.error(
                "Chat request failed:",
                error
            );


            addMessage(
                getChatErrorMessage(
                    error
                ),
                "assistant-message error-message"
            );


        } finally {

            setSendingState(
                false
            );

            chatInput.focus();
        }
    }
);