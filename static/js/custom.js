
document.addEventListener('DOMContentLoaded', function() {
    console.log("Global JS Initializing...");

    // --- Fonctions Utilitaires (Définies Globalement) ---
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function formatNumber(num) {
        const number = parseFloat(num || 0);
        const roundedNum = Math.round(number);
        return roundedNum.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }

    // --- Sélection Éléments Globaux (Modal, Header) ---
    const modalElement = document.getElementById('add-to-cart-modal');
    const modalProductTitle = document.getElementById('add-modal-product-title');
    const modalProductImage = document.getElementById('add-modal-product-image');
    const modalProductQuantity = document.getElementById('modal-product-quantity');
    const modalCartItems = document.getElementById('modal-cart-items');
    const modalCartTotal = document.getElementById('modal-cart-total');
    const closeModalButton = modalElement?.querySelector('.close-modal-button');
    const continueShoppingButton = modalElement?.querySelector('.continue-shopping-button');
    const cartCounterElements = document.querySelectorAll('.dynamic-cart-counter'); // Sélection par classe

    // --- Fonctions pour le Modal (Globales) ---
    function openAddToCartModal(productData) {
        if (!modalElement || !productData) { console.error("Modal element or productData missing for modal."); return; }
        console.log("Opening modal with data:", productData);

        if (modalProductTitle) modalProductTitle.textContent = productData.product_title || 'Товар';
        if (modalProductImage) {
            const defaultImagePath = modalProductImage.dataset.defaultImage || '/static/img/images/default_image.webp'; // Utilise data- ou fallback
            modalProductImage.src = productData.product_image_url || defaultImagePath;
            modalProductImage.alt = productData.product_title || 'Товар';
        }
        if (modalProductQuantity) modalProductQuantity.textContent = productData.new_quantity_in_cart || '?';
        // Met à jour le compteur DANS le modal (utilise la classe partagée)
        if (modalCartItems && productData.cart_total_items !== undefined) {
            modalCartItems.textContent = productData.cart_total_items;
        }
        if (modalCartTotal && productData.cart_total_price !== undefined) {
            modalCartTotal.textContent = formatNumber(productData.cart_total_price);
        }

        modalElement.style.display = 'flex';
        setTimeout(() => modalElement.classList.add('is-visible'), 10);
    }

    function closeAddToCartModal() {
        if (!modalElement) return;
        modalElement.classList.remove('is-visible');
        setTimeout(() => { modalElement.style.display = 'none'; }, 300);
    }

    // --- Écouteurs pour les Boutons du Modal (Globaux) ---
    if (closeModalButton) { closeModalButton.addEventListener('click', closeAddToCartModal); }
    if (continueShoppingButton) { continueShoppingButton.addEventListener('click', closeAddToCartModal); }
    if (modalElement) {
        modalElement.addEventListener('click', (event) => { if (event.target === modalElement) { closeAddToCartModal(); } });
    }

    // --- Fonction AJAX Générique (Globale) ---
    async function makeAjaxRequest(url, data, csrfToken) {
        if (!url || !csrfToken) { console.error(`Missing URL (${url}) or CSRF token.`); return { success: false, error: 'Configuration error' }; }
        console.log(`AJAX -> POST to ${url} with data:`, data);
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrfToken },
                body: JSON.stringify(data)
            });
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                const responseData = await response.json();
                // Vérifie le statut HTTP ET le flag success dans la réponse JSON
                if (!response.ok || !responseData.success) {
                    console.error(`AJAX Error (${url}): Status ${response.status}`, responseData?.error);
                    return { success: false, data: responseData, status: response.status }; // Inclut le statut
                }
                console.log(`AJAX Success (${url}):`, responseData);
                return { success: true, data: responseData };
            } else {
                const text = await response.text();
                console.error(`AJAX Error (${url}): Expected JSON, got ${contentType}. Status: ${response.status}. Resp: ${text.substring(0, 200)}`);
                return { success: false, error: 'Server response not JSON', status: response.status };
            }
        } catch (error) {
            console.error(`AJAX Network Error (${url}):`, error);
            return { success: false, error: 'Network error' };
        }
    }


    // --- Fonction Mise à Jour Compteurs Panier (Globale) ---
    function updateAllCartCounters(count) {
        if (count === undefined || count === null) return;
        const countStr = String(count); // Convertit en chaîne
        console.log(`Updating ALL cart counters to: ${countStr}`);
        cartCounterElements.forEach(element => {
            element.textContent = countStr;
        });
    }

    // --- Écouteur Global "Ajouter au Panier" ---
    document.body.addEventListener('click', async function(event) {
        const addButton = event.target.closest('.add-to-cart-button');
        if (!addButton) return;

        event.preventDefault();
        const productId = addButton.dataset.productId;
        const addUrl = addButton.dataset.addUrl;
        // --- Récupérer le token CSRF au moment du clic (plus sûr) ---
        const currentCsrfToken = document.querySelector('input[name=csrfmiddlewaretoken]')?.value;

        if (!productId || !addUrl) { console.error("Add to cart button missing product ID or add URL."); return; }
        if (!currentCsrfToken) { console.error("CSRF token not found for add to cart action!"); alert("Ошибка безопасности. Пожалуйста, обновите страницу."); return; }

        // Logique pour trouver l'input quantité associé
        let quantity = 1; // Défaut
        const form = addButton.closest('form');
        const specificQuantityInput = document.getElementById(`product-quantity-${productId}`); // Pour page détail
        const generalQuantityInput = form?.querySelector('.quantity-input-small'); // Pour carte produit

        if (specificQuantityInput) {
            quantity = parseInt(specificQuantityInput.value, 10);
            console.log("Quantity from specific input:", quantity);
        } else if (generalQuantityInput) {
            quantity = parseInt(generalQuantityInput.value, 10);
            console.log("Quantity from general input:", quantity);
        }

        if (isNaN(quantity) || quantity < 1) {
            quantity = 1; // Assure au moins 1
        }
        console.log(`Final quantity to add for ${productId}: ${quantity}`);

        addButton.disabled = true;
        const spinner = addButton.parentElement?.querySelector('.add-to-cart-spinner');
        if (spinner) spinner.style.display = 'inline-block';

        const result = await makeAjaxRequest(addUrl, { quantity: quantity }, currentCsrfToken);

        if (result?.success) {
            const data = result.data;
            updateAllCartCounters(data.cart_total_items); // Met à jour tous les compteurs
            openAddToCartModal(data);
        } else {
            alert(`Не удалось добавить товар: ${result?.data?.error || result?.error || 'Ошибка сервера'}`);
        }

        addButton.disabled = false;
        if (spinner) spinner.style.display = 'none';
    });


    // ==================================================
    // --- CODE SPÉCIFIQUE À LA PAGE CHECKOUT ---
    // ==================================================
    const cartContentContainer = document.getElementById('cart-content-container');
    if (cartContentContainer) {
        console.log("Checkout page specific JS running...");

        // --- Éléments spécifiques Checkout ---
        const cartTableBody = document.getElementById('cart-table-body');
        const cartSubtotalDisplayElement = document.getElementById('cart-subtotal-display');
        const cartSubtotalElement = document.getElementById('cart-subtotal');
        const shippingCostElement = document.getElementById('shipping-cost');
        const grandTotalElement = document.getElementById('grand-total');
        const shippingSelect = document.getElementById('shipping_method_select');
        const kmInputContainer = document.getElementById('km-input-container');
        const kmInput = document.getElementById('shipping_distance_km_display');
        const shippingCostLine = document.getElementById('shipping-cost-line');
        const shippingRussiaNote = document.getElementById('shipping-russia-note');
        // const grandTotalRussiaNote = document.getElementById('grand-total-russia-note');
        const cartEmptyMessage = document.getElementById('cart-empty-message');
        const checkoutForm = document.getElementById('checkout-form');
        const emailInput = document.getElementById('id_email');
        const phoneInput = document.getElementById('id_phone');
        const agreementCheckbox = document.getElementById('id_agreement');
        const csrfToken = checkoutForm?.querySelector('[name=csrfmiddlewaretoken]')?.value; // Token DANS le formulaire checkout
        const updateShippingSessionUrl = cartContentContainer.dataset.updateShippingUrl;

        // --- Constantes de Coût ---
        const DELIVERY_RUSSIA = document.getElementById('shipping-russia-value')?.value;
        const DELIVERY_MKAD_OUTSIDE = document.getElementById('shipping-mkad-outside-value')?.value;
        const DELIVERY_MKAD_INSIDE = document.getElementById('shipping-mkad-inside-value')?.value;
        const SUBTOTAL_THRESHOLD = parseFloat(document.getElementById('subtotal-threshold')?.value || 10000);
        const MKAD_INSIDE_LOW_COST = parseFloat(document.getElementById('mkad-inside-low-cost')?.value || 500);
        const MKAD_OUTSIDE_RATE_PER_KM = parseFloat(document.getElementById('mkad-outside-rate')?.value || 50);
        const MAX_QUANTITY_PER_ITEM = 1000;
        const MAX_FILE_SIZE_MB = 5;
        const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
        const ALLOWED_FILE_TYPES = [ 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png', 'image/webp', 'image/gif'];

        let isUpdatingQuantity = false;

        // --- Vérification Initiale (Checkout) ---
        if (!csrfToken) { console.error("CSRF token not found ON CHECKOUT PAGE!"); }
        if (!updateShippingSessionUrl) { console.warn("Update shipping URL missing on checkout!"); }

        // --- Définition debounce (locale ou utilise globale) ---
        const debouncedSaveShipping = debounce(async (method, distance = null) => {
            await makeAjaxRequest(updateShippingSessionUrl, { shipping_method: method || null, shipping_distance_km: distance }, csrfToken);
        }, 400);

        // --- Fonctions de Validation JS (Spécifiques Checkout) ---
        function validateEmailFormat(email) { /* ... Votre logique (exemple simple ci-dessous) ... */
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; return emailRegex.test(String(email).toLowerCase());
        }
        function validateRussianPhoneNumber(phone) { /* ... Votre logique (exemple simple ci-dessous) ... */
            if (!phone) return false; const cleaned = String(phone).replace(/\D/g,''); const phoneRegex = /^[78]\d{10}$/; return phoneRegex.test(cleaned);
        }
        function displayValidationError(inputElement, message) { /* ... Logique pour afficher erreur ... */
            if (!inputElement) return; inputElement.classList.add('is-invalid'); inputElement.classList.remove('is-valid');
            let errorContainer = inputElement.closest('.form-group')?.querySelector('.invalid-feedback.js-error'); if (!errorContainer) { errorContainer = inputElement.closest('.form-group')?.querySelector('.invalid-feedback.error');}
            if (errorContainer) { errorContainer.textContent = message; errorContainer.style.display = 'block'; }
            console.warn(`Validation Error for ${inputElement.name || inputElement.id}: ${message}`);
        }
        function clearValidationError(inputElement) { /* ... Logique pour cacher erreur ... */
            if (!inputElement) return; inputElement.classList.remove('is-invalid');
            const errorContainer = inputElement.closest('.form-group')?.querySelector('.invalid-feedback.js-error'); if (errorContainer) { errorContainer.textContent = ''; errorContainer.style.display = 'none'; }
        }

        // --- Fonctions Calcul/Affichage (Spécifiques Checkout) ---
        function calculateShippingCostCheckout(currentSubtotal) { /* ... (code inchangé) ... */
            let sc = 0; const st = parseFloat(currentSubtotal||0); const method = shippingSelect?.value; const needsKm = method === DELIVERY_MKAD_OUTSIDE; let dist = needsKm ? parseInt(kmInput?.value||0,10) : 0;
            if(kmInputContainer){ kmInputContainer.style.display = needsKm ? 'block':'none'; if(kmInput) kmInput.required = (needsKm && dist > 0); } // required seulement si km > 0
            if(!method){ sc=0; } else if(method===DELIVERY_MKAD_INSIDE){ sc=(st>=SUBTOTAL_THRESHOLD)?0:MKAD_INSIDE_LOW_COST; } else if(method===DELIVERY_MKAD_OUTSIDE){ sc=(dist>0)?(dist*MKAD_OUTSIDE_RATE_PER_KM):0; } else if(method===DELIVERY_RUSSIA){ sc=0; } else { sc=0;}
            return sc;
        }
        function updateTotalsUICheckout(subtotal, shippingCost) { /* ... (code inchangé, utilise formatNumber global) ... */
            const sNum=parseFloat(subtotal||0); const shNum=parseFloat(shippingCost||0); const gTotal=sNum+shNum;
            if(cartSubtotalDisplayElement) cartSubtotalDisplayElement.textContent=formatNumber(sNum); if(shippingCostElement) shippingCostElement.textContent=formatNumber(shNum); if(grandTotalElement) grandTotalElement.textContent=formatNumber(gTotal);
            const isRussia=shippingSelect?.value===DELIVERY_RUSSIA; if(shippingRussiaNote) shippingRussiaNote.style.display=isRussia?'inline':'none'; if(shippingCostLine){ shippingCostLine.style.display=shippingSelect?.value?'flex':'none';}
        }

        // --- Gestionnaires d'événements (Checkout) ---
        async function handleQuantityChangeCheckout(productId, newQuantity, inputElement) {
            if (isUpdatingQuantity) { return; } isUpdatingQuantity = true;
            const row = inputElement.closest('.cart-item'); const updateUrl = inputElement.dataset.updateUrl;
            if (!updateUrl) { console.error("Missing update URL"); isUpdatingQuantity = false; return; }
            if (row) row.style.opacity = '0.5';

            const result = await makeAjaxRequest(updateUrl, { quantity: newQuantity }, csrfToken); // Utilise AJAX globale

            if (result?.success) {
                const data = result.data;
                updateAllCartCounters(data.cart_total_items); // Met à jour TOUS les compteurs

                const serverSubtotal = parseFloat(data.cart_total_price || 0);
                if (cartSubtotalDisplayElement) { cartSubtotalDisplayElement.textContent = formatNumber(serverSubtotal); cartSubtotalElement.textContent = formatNumber(serverSubtotal); }

                if (data.action === 'removed' || data.cart_total_items === 0) {
                    if (row) row.remove();
                    const remainingItems = cartTableBody?.querySelectorAll('.cart-item');
                    if (!remainingItems || remainingItems.length === 0) {
                        if (cartContentContainer) cartContentContainer.style.display = 'none'; if (cartEmptyMessage) cartEmptyMessage.style.display = 'block'; if (shippingSelect) shippingSelect.value = ''; if (kmInput) kmInput.value = '';
                        updateTotalsUICheckout(0, 0); debouncedSaveShipping(null, null);
                    } else { handleShippingChangeCheckout(); }
                } else if (data.action === 'updated') {
                    if(row) {
                        inputElement.value = data.new_quantity;
                        const itemTotalEl = row.querySelector('.product-subtotal .item-total-price'); if (itemTotalEl) itemTotalEl.textContent = formatNumber(data.item_total_price);
                        const minusBtn = row.querySelector('.quantity-minus'); const plusBtn = row.querySelector('.quantity-plus'); const maxQty = parseInt(inputElement.dataset.maxQuantity || MAX_QUANTITY_PER_ITEM);
                        if(minusBtn) minusBtn.disabled = (data.new_quantity <= 0); if(plusBtn) plusBtn.disabled = (data.new_quantity >= maxQty);
                    }
                    handleShippingChangeCheckout();
                }
            } else { console.error("Qty update failed (Checkout):", result?.error); }

            if (row) row.style.opacity = '1'; isUpdatingQuantity = false;
        }

        function handleShippingChangeCheckout() {
            const currentSubtotalText = cartSubtotalDisplayElement?.textContent || '0';
            const currentSubtotal = parseFloat(currentSubtotalText.replace(/\s/g, '')) || 0;
            const newShippingCost = calculateShippingCostCheckout(currentSubtotal);
            updateTotalsUICheckout(currentSubtotal, newShippingCost);
            const selectedMethod = shippingSelect?.value; const needsKm = selectedMethod === DELIVERY_MKAD_OUTSIDE;
            let distanceKm = parseInt(kmInput?.value || 0, 10); let distanceToSend = (needsKm && distanceKm > 0) ? distanceKm : null;
            debouncedSaveShipping(selectedMethod || null, distanceToSend);
        }

        // --- Écouteurs d'événements (Checkout) ---
        if (cartTableBody) {
            console.log("Attaching listeners to checkout cart table.");
            cartTableBody.addEventListener('click', (event) => {
                const target = event.target;
                const amountControl = target.closest('.amount-controls');
                const removeButton = target.closest('.remove-button');

                if (amountControl) {
                    const input = amountControl.parentElement.querySelector('.quantity-input'); if (!input) return; const productId = input.dataset.productId; let currentVal = parseInt(input.value, 10); if(isNaN(currentVal)) currentVal=0; let newVal = currentVal;
                    if (amountControl.classList.contains('quantity-minus')) { newVal = Math.max(0, currentVal - 1); } else if (amountControl.classList.contains('quantity-plus')) { newVal = Math.min(MAX_QUANTITY_PER_ITEM, currentVal + 1); }
                    if (newVal !== currentVal) { input.value = newVal; handleQuantityChangeCheckout(productId, newVal, input); }
                } else if (removeButton) {
                    const productId = removeButton.dataset.productId; const row = removeButton.closest('.cart-item'); const input = row?.querySelector('.quantity-input'); const title = row?.querySelector('.product-name a')?.textContent || 'товар'; if (!productId || !input) { console.error("Missing data for remove"); return;}
                    console.log(`Remove button clicked for product ${productId}`); // Log pour debug
                    // alert(`Товар "${title}" удален из корзины.`); // Retiré l'alerte de confirmation
                    handleQuantityChangeCheckout(productId, 0, input); // Quantité 0 pour supprimer
                }
            });

            const debouncedInputHandler = debounce((inputElement) => {
                const productId = inputElement.dataset.productId; let quantity = parseInt(inputElement.value, 10); if (isNaN(quantity) || quantity < 0) quantity = 0; if (quantity > MAX_QUANTITY_PER_ITEM) quantity = MAX_QUANTITY_PER_ITEM; if (parseInt(inputElement.value, 10) !== quantity) { inputElement.value = quantity; } handleQuantityChangeCheckout(productId, quantity, inputElement);
            }, 500);
            cartTableBody.addEventListener('input', (event) => { if (event.target.classList.contains('quantity-input')) { debouncedInputHandler(event.target); } });
        }

        if (shippingSelect) { shippingSelect.addEventListener('change', handleShippingChangeCheckout); }
        if (kmInput) {
            const debouncedKmHandler = debounce(handleShippingChangeCheckout, 400);
            kmInput.addEventListener('input', () => { if (shippingSelect?.value === DELIVERY_MKAD_OUTSIDE) { debouncedKmHandler(); } });
        }

        // --- Validation Client avant Soumission (Checkout) ---
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', function(event) { /* ... (logique validation inchangée) ... */
                console.log("Checkout form submit attempt."); let formIsValid = true;
                checkoutForm.querySelectorAll('.invalid-feedback.js-error').forEach(el => { el.textContent = ''; el.style.display = 'none'; });
                checkoutForm.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                if (emailInput && !validateEmailFormat(emailInput.value)) { displayValidationError(emailInput, 'Введите действительный email.'); formIsValid = false; } else if (emailInput) { clearValidationError(emailInput); }
                if (phoneInput && !validateRussianPhoneNumber(phoneInput.value)) { displayValidationError(phoneInput, 'Введите действительный номер (+7 XXX XXX-XX-XX).'); formIsValid = false; } else if (phoneInput) { clearValidationError(phoneInput); }
                if (agreementCheckbox && !agreementCheckbox.checked) { displayValidationError(agreementCheckbox, 'Необходимо согласие.'); formIsValid = false; } else if (agreementCheckbox) { clearValidationError(agreementCheckbox); }
                const fileInput = document.getElementById('id_file');
                if (fileInput?.files && fileInput.files.length > 0) {
                    const file = fileInput.files[0]; const fileErrorContainer = fileInput.closest('.form-group').querySelector('.invalid-feedback'); // Cible l'erreur associée
                    if (file.size > MAX_FILE_SIZE_BYTES) { displayValidationError(fileInput, `Файл слишком большой (Макс: ${MAX_FILE_SIZE_MB} МБ).`); formIsValid = false; }
                    else if (!ALLOWED_FILE_TYPES.includes(file.type.toLowerCase())) { displayValidationError(fileInput, `Недопустимый тип файла.`); formIsValid = false; }
                    else { clearValidationError(fileInput); }
                } else if (fileInput) { clearValidationError(fileInput); }
                if (!formIsValid) { 
                    console.log("Client-side validation failed."); 
                    event.preventDefault(); 
                    const firstError = checkoutForm.querySelector('.is-invalid'); 
                    if(firstError) { 
                        firstError.focus(); 
                    } 
                }
                else { console.log("Client-side validation passed."); }

            });
        }

         // --- Gestion Affichage Description Paiement (Spécifique Checkout) ---
        const paymentRadios = document.querySelectorAll('.payment-method-radio');
        const paymentDescriptions = document.querySelectorAll('.payment-description');
        function handlePaymentMethodChangeDisplay() { /* ... (code inchangé) ... */ }
        paymentRadios.forEach(radio => radio.addEventListener('change', handlePaymentMethodChangeDisplay));
        handlePaymentMethodChangeDisplay();


        // --- Initialisation (Checkout) ---
        const initialCartItemsCheckout = cartTableBody ? cartTableBody.querySelectorAll('.cart-item') : [];
        if (initialCartItemsCheckout.length > 0 || (cartEmptyMessage && cartEmptyMessage.style.display === 'none') ) {
            console.log("Performing initial calculation for checkout page.");
            handleShippingChangeCheckout(); // Lance le calcul ET l'affichage initial
        } else { /* ... gestion panier vide initial ... */ }

    } else {
        console.log("Not on checkout page. Skipping checkout specific JS.");
    }

    console.log("Global JS initialization complete.");
});

// --- Logique pour la page détail produit (si séparée ou dans le même fichier global) ---
document.addEventListener('DOMContentLoaded', function() {
    const productDetailContainer = document.querySelector('.card__characteristics'); // Cherche un élément parent unique à la page détail
    if (productDetailContainer) {
        console.log("Product Detail Page JS Initializing...");

        const amountDiv = productDetailContainer.querySelector('.product-detail-amount');
        if (amountDiv) {
            const minusBtn = amountDiv.querySelector('.quantity-minus');
            const plusBtn = amountDiv.querySelector('.quantity-plus');
            const input = amountDiv.querySelector('.quantity-input-detail');
            // Lire la limite max depuis un data-attribute si vous en ajoutez un, sinon utilise la constante globale
            const maxQuantity = parseInt(input?.dataset.maxQuantity || '1000', 10) || 1000;

            if (minusBtn && plusBtn && input) {
                console.log("Attaching +/- listeners on product detail page.");
                minusBtn.addEventListener('click', () => {
                    let currentVal = parseInt(input.value, 10);
                    if (isNaN(currentVal)) currentVal = 1;
                    // --- Assure un minimum de 1 sur la page détail ---
                    input.value = Math.max(1, currentVal - 1);
                });

                plusBtn.addEventListener('click', () => {
                    let currentVal = parseInt(input.value, 10);
                    if (isNaN(currentVal)) currentVal = 0; // Commence à 0 pour l'incrément
                    input.value = Math.min(maxQuantity, currentVal + 1);
                });

                // Validation de la saisie directe
                input.addEventListener('input', () => {
                    let quantity = parseInt(input.value, 10);
                    // --- Assure un minimum de 1 sur la page détail ---
                    if (isNaN(quantity) || quantity < 1) {
                        quantity = 1;
                    }
                    if (quantity > maxQuantity) {
                        quantity = maxQuantity;
                    }
                    // Met à jour seulement si la valeur change pour éviter boucle infinie
                    if (parseInt(input.value, 10) !== quantity) {
                        input.value = quantity;
                    }
                });
            } else {
                console.warn("Could not find all +/-/input elements on product detail page.");
            }
        } else {
            console.warn("Amount div (.product-detail-amount) not found on product detail page.");
        }

    }
});



//::::::::::: CHECK FORM VALIDATION PHONE AND EMAIL:::::::::::::::: 
// Custom function to format phone number as user types
window.addEventListener("DOMContentLoaded", function() {
    [].forEach.call(document.querySelectorAll('input[data-phone]'), function(input) {
        input.addEventListener("input", mask);
        input.addEventListener("focus", mask);
        input.addEventListener("blur", mask);

        function mask(event) {
            var blank = "+_ (___) ___-__-__";
            var i = 0;
            var val = this.value.replace(/\D/g, ""); // Remove non-digit characters

            // Allow user to type before replacing
            if (val.length > 0) {
                // Replace the prefix with '7' if the number starts with '8'
                if (val.startsWith('8')) {
                    val = '7' + val.slice(1); // Replace '8' with '7'
                } else if (!val.startsWith('7')) {
                    val = '7' + val; // Replace any other starting digit with '7'
                }
            }

            this.value = blank.replace(/./g, function(char) {
                if (/[_\d]/.test(char) && i < val.length) return val.charAt(i++);
                return i >= val.length ? "" : char;
            });

            if (event.type == "blur") {
                if (this.value.length == 2) this.value = "";

                var pattern = /^(\+7)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
                if (pattern.test(this.value)) {
                    this.classList.add('input-ok');
                    this.classList.remove('input-error');
                    this.parentNode.classList.remove('error-input');
                    this.parentNode.classList.add('ok-input');
                } else {
                    this.classList.add('input-error');
                    this.classList.remove('input-ok');
                    this.parentNode.classList.add('error-input');
                    this.parentNode.classList.remove('ok-input');
                }
            } else {
                setCursorPosition(this, this.value.length);
            }
        };

        function setCursorPosition(elem, pos) {
            elem.focus();
            
            if (elem.setSelectionRange) {    
                elem.setSelectionRange(pos, pos);
                return;
            }
            
            if (elem.createTextRange) {    
                var range = elem.createTextRange();
                range.collapse(true);
                range.moveEnd("character", pos);
                range.moveStart("character", pos);
                range.select();      
                return;
            }
        }
    });
});



// ==================================================
// ------------- CODE SEND ORDER FORM --------------
// ==================================================

// Handle AJAX error response
function handleError(xhr, status, error) {
    console.log('Error:', xhr.responseText);
}
// Get cookie value by name
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// Check if the method requires CSRF protection
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
// Check if the URL is same-origin
function sameOrigin(url) {
    const host = document.location.host;
    const protocol = document.location.protocol;
    const sr_origin = '//' + host;
    const origin = protocol + sr_origin;

    return (url === origin || url.slice(0, origin.length + 1) === origin + '/') ||
            (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') ||
            !(/^(\/\/|http:|https:).*/.test(url));
}


function send_form_order(form_name) {
    const form = document.getElementById(form_name);
    
    const csrftoken = getCookie('csrftoken');

    if (!validatePhoneNumber(form) || !validateEmailInput(form)) {
        return false;
    }

    action_url = form.getAttribute('action')
    const submitButton = form.querySelector('.submit-form-btn');

    if(submitButton) submitButton.disabled = true;
    
    const form_data = new FormData(form);

    $.ajax({
        url: form.getAttribute('action'),
        type: 'POST',
        contentType: false,
        processData: false,
        data: form_data,
        dataType: 'json',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function(data) {
            OrderHandleSuccess(data);
        },
        error: function(xhr, status, error) {
            handleError(xhr, status, error);
        },
        complete: function() {
                if(submitButton) submitButton.disabled = false;
                console.log("jQuery AJAX complete.");
        }
    });

    return false;
}




// // Validate phone number format
function validatePhoneNumber(form) {
    const phoneInput = form.querySelector('input[name="phone"]');
    if (!phoneInput) {
        console.warn("validatePhoneNumber: phone input not found in form", form.id);
        return true;
    }
    const phoneError = form.querySelector('.phone-error');
    const phoneValue = phoneInput.value;
    const pattern = /^(\+7)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;

    if (!pattern.test(phoneValue)) {
        if(phoneError) {
            phoneError.textContent = 'Неверный формат номера.';
            phoneError.style.display = 'block';
        }
        phoneInput.classList.add('invalid');
        console.log("Phone validation failed (client-side)");
        return false;
    } else {
        if(phoneError) phoneError.style.display = 'none';
        phoneInput.classList.remove('invalid');
        console.log("Phone validation passed (client-side)");
        return true;
    }
}



// Validate email format
function validateEmailInput(form) {
    const emailInput = form.querySelector('input[name="email"]');
    const emailError = form.querySelector('.email-error');

    if (!emailInput) {
        console.warn("validateEmailInput: email input not found in form", form.id);
        return true;
    }

    const emailValue = emailInput.value.trim();

    if (emailInput.required && !emailValue) {
        if (emailError) emailError.textContent = 'Это поле обязательно.';
        if (emailError) emailError.style.display = 'block';
        emailInput.classList.add('invalid');
        return false;
    }

    if (emailValue) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(emailValue)) {
            if (emailError) emailError.textContent = 'Неверный адрес электронной почты.';
            if (emailError) emailError.style.display = 'block';
            emailInput.classList.add('invalid');
            return false;
        }
    }

    if (emailError) emailError.style.display = 'none';
    emailInput.classList.remove('invalid');
    return true;
}


function formatNumber(num) {
    const number = parseFloat(num || 0); const roundedNum = Math.round(number); return roundedNum.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

// Handle successful AJAX response
function OrderHandleSuccess(data) {
    if (data.success) {
        console.log('Redirecting to thank you page...');
        window.location.href = data.thank_you_url;
        closeModal();
    } else {
        closeModal();
        
    }
}

// FUNCTION TO CLOSE ALL MODAL
function closeModal() {
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.style.display = 'none';
    });
}




// ========================================
// MODAL ORDER PRODUCT
// ========================================
// --- Logique exécutée au chargement ---
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing product modal triggers...");

    const productOrderModal = document.getElementById('product-order-modal');

    // Fonction pour ouvrir et peupler le modal unique
    function openAndPopulateProductModal(orderType, productData) {
        if (!productOrderModal || !productData) {
            console.error("Modal element or product data missing.");
            return;
        }

        const modalTitleEl = document.getElementById('product-order-modal-title');
        const imgEl = document.getElementById('modal-product-image');
        const nameEl = document.getElementById('modal-product-name');
        const skuEl = document.getElementById('modal-product-sku');
        const priceEl = document.getElementById('modal-product-price');
        const quantityEl = document.getElementById('modal-product-quantity');
        const form = document.getElementById('product-order-modal-form');

        if (!form) { console.error("Modal form not found!"); return; }

        // Peupler affichage
        if(modalTitleEl) modalTitleEl.textContent = orderType;
        if(nameEl) nameEl.textContent = productData.title || 'N/A';
        if(skuEl) skuEl.textContent = productData.sku || 'N/A';
        if(priceEl) priceEl.textContent = formatNumber(productData.price || 0);
        if(quantityEl) quantityEl.textContent = productData.quantity || '1';
        if(imgEl) {
            const defaultImagePath = imgEl.dataset.defaultImage || '/static/img/images/default_image.webp';
            imgEl.src = productData.image || defaultImagePath;
            imgEl.alt = productData.title || 'Product';
        }

        // Peupler champs cachés du formulaire
        form.querySelector('input[name="type"]').value = orderType;
        form.querySelector('input[name="product_id"]').value = productData.id || '';
        form.querySelector('input[name="product_sku"]').value = productData.sku || '';
        form.querySelector('input[name="product_title"]').value = productData.title || '';
        form.querySelector('input[name="product_price"]').value = productData.price || '';
        form.querySelector('input[name="product_quantity"]').value = productData.quantity || '1';

        // Construit le commentaire
        form.querySelector('input[name="comment"]').value = `Заказ товара: ${productData.title || 'N/A'} (Sku: ${productData.sku || 'N/A'}) | Кол-во: ${productData.quantity || '1'}`;

        // Nettoyer les erreurs précédentes
        form.querySelectorAll('.invalid-feedback.error').forEach(el => el.style.display = 'none');
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        // Optionnel : Vider les champs visibles ?
        form.querySelector('input[name="name"]').value = '';
        form.querySelector('input[name="phone"]').value = '';
    }

    // Écouteur pour les boutons déclencheurs
    document.body.addEventListener('click', function(event) {
        const triggerButton = event.target.closest('.btn-open-product-modal'); // Utilise la classe commune
        if (!triggerButton) return;

        event.preventDefault();

        const modalTargetSelector = triggerButton.dataset.modalTarget; // Doit être #product-order-modal
        const orderType = triggerButton.dataset.orderType; // Быстрый заказ ou Под заказ

        // console.log("Modal target",modalTargetSelector);
        // console.log("Order type ",orderType);


        if (modalTargetSelector !== '#product-order-modal' || !orderType) {
            console.error("Button missing correct modal target or order type data.");
            return;
        }

        // Récupère les données produit
        const productData = {
            id: triggerButton.dataset.productId,
            sku: triggerButton.dataset.productSku,
            title: triggerButton.dataset.productTitle,
            price: triggerButton.dataset.productPrice,
            image: triggerButton.dataset.productImage,
            quantity: '1' // Défaut
        };

        // Lit la quantité depuis l'input si sur la page détail
        const quantityInputId = triggerButton.dataset.quantityInputId;
        if (quantityInputId) {
            const quantityInput = document.getElementById(quantityInputId);
            if (quantityInput) {
                let qty = parseInt(quantityInput.value, 10);
                if (isNaN(qty) || qty < 1) qty = 1;
                productData.quantity = qty;
            }
        }

        // Ouvre et peuple le modal
        openAndPopulateProductModal(orderType, productData);
    });

});



// ========================================
// MODAL ORDER SERVICE
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing service modal triggers...");

    const serviceOrderModal = document.getElementById('service-order-modal');

    // Fonction pour ouvrir et peupler le modal unique
    function openAndPopulateServiceModal(orderType, serviceData) {
        if (!serviceOrderModal || !serviceData) {
            console.error("Modal element or service data missing.");
            return;
        }

        const modalTitleEl = document.getElementById('service-order-modal-title');
        const imgEl = document.getElementById('modal-service-image');
        const nameEl = document.getElementById('modal-service-name');
        const form = document.getElementById('service-order-modal-form');

        if (!form) { console.error("Modal form not found!"); return; }

        // Peupler affichage
        if(modalTitleEl) modalTitleEl.textContent = orderType;
        if(nameEl) nameEl.textContent = serviceData.title || 'N/A';
        if(imgEl) {
            const defaultImagePath = imgEl.dataset.defaultImage || '/static/img/images/default_image.webp';
            imgEl.src = serviceData.image || defaultImagePath;
            imgEl.alt = serviceData.title || 'Service';
        }

        // Peupler champs cachés du formulaire
        form.querySelector('input[name="type"]').value = orderType;
        form.querySelector('input[name="service_id"]').value = serviceData.id || '';
        form.querySelector('input[name="service_title"]').value = serviceData.title || '';

        // Construit le commentaire
        form.querySelector('input[name="comment"]').value = `Заказ Услуги: ${serviceData.title || 'N/A'}`;

        // Nettoyer les erreurs précédentes
        form.querySelectorAll('.invalid-feedback.error').forEach(el => el.style.display = 'none');
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        // Optionnel : Vider les champs visibles ?
        form.querySelector('input[name="name"]').value = '';
        form.querySelector('input[name="phone"]').value = '';
    }

    // Écouteur pour les boutons déclencheurs
    document.body.addEventListener('click', function(event) {
        const triggerButton = event.target.closest('.btn-open-service-modal'); // Utilise la classe commune
        if (!triggerButton) return;

        event.preventDefault();

        const modalTargetSelector = triggerButton.dataset.modalTarget; // Doit être #product-order-modal
        const orderType = triggerButton.dataset.orderType; // Быстрый заказ ou Под заказ

        // console.log("Modal target",modalTargetSelector);
        // console.log("Order type ",orderType);


        if (modalTargetSelector !== '#service-order-modal' || !orderType) {
            console.error("Button missing correct modal target or order type data.");
            return;
        }

        // Récupère les données produit
        const serviceData = {
            id: triggerButton.dataset.serviceId,
            title: triggerButton.dataset.serviceTitle,
            image: triggerButton.dataset.serviceImage,
        };

        // Ouvre et peuple le modal
        openAndPopulateServiceModal(orderType, serviceData);
    });

});

// ==========================================================
// Gère le filtrage dynamique AJAX, le tri et le Load More
// ==========================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log("Filter, Sort & Load JS Initializing...");

    // --- Sélection des Éléments DOM ---
    const productListContainer = document.getElementById('product-list-container');
    if (productListContainer) {
        console.log("Product Listing page detected. Initializing filters, sort, load more...");    
        // Conteneurs principaux pour les filtres et produits
        const filterContainerDesktop = document.getElementById('filters-container-desktop');
        const filterContainerMobileContent = document.getElementById('filters-container-mobile'); // Le div INTERNE mobile
        // const productListContainer = document.getElementById('product-list-container');

        // Éléments liés aux filtres mobiles
        const mobileToggleTrigger = document.getElementById('mobile-toggle-filter'); // Le div cliquable
        const mobileOpenContainer = document.querySelector('.category__mobile'); // Le parent qui reçoit la classe 'open'

        // Éléments pour le tri et le chargement/pagination
        const sortSelect = document.getElementById('sort-select');
        const showMoreContainer = document.getElementById('show-more-container');
        const loadMoreButton = document.getElementById('load-more-button');
        const loadingIndicator = document.getElementById('loading-indicator'); // Pour AJAX général
        const paginationContainer = document.getElementById('pagination-container'); // Pour pagination numérotée
        const productCountDisplay = document.getElementById('product-count-display'); // Span pour le compte
        const pageTitleH1 = document.querySelector('.category-list h1'); // Titre H1

        // Utilise le conteneur desktop comme source principale pour les data-attributes, fallback sur mobile
        const mainFilterDataSource = filterContainerDesktop || filterContainerMobileContent;

        // --- URLs et Données de base ---
        const filterAjaxUrl = mainFilterDataSource?.dataset.filterAjaxUrl;
        const baseCategoryUrl = mainFilterDataSource?.dataset.baseCategoryUrl; // URL catégorie sans /f/ ou query params
        const currentCategorySlug = mainFilterDataSource?.dataset.currentCategorySlug;
        // URL pour le "Load More" (différente de l'URL de filtrage)
        const loadMoreBaseUrl = loadMoreButton?.dataset.ajaxUrl; // Ex: /ajax/load-products/slug/

        // --- Variables d'état ---
        let isAjaxInProgress = false; // Flag global pour éviter requêtes AJAX concurrentes

        // --- Vérification Initiale des Éléments Essentiels ---
        if (!productListContainer) {
            console.error("Product list container (#product-list-container) not found. Aborting JS.");
            return;
        }
        if (!mainFilterDataSource || !filterAjaxUrl || !baseCategoryUrl || !currentCategorySlug) {
            console.error("Core filter elements or data attributes missing (filter container, URLs, slug). Aborting filter JS.");
            // On arrête ici car le filtrage est essentiel
            return;
        }
        // Le token CSRF n'est pas nécessaire pour les requêtes GET (filtrage, load more)
        console.log("Filter/Sort/Load config loaded:", { filterAjaxUrl, baseCategoryUrl, currentCategorySlug, loadMoreBaseUrl });

        // --- Fonctions Utilitaires ---
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => { clearTimeout(timeout); func(...args); };
                clearTimeout(timeout); timeout = setTimeout(later, wait);
            };
        }

        function formatNumber(num) {
            const number = parseFloat(num || 0);
            const roundedNum = Math.round(number);
            return roundedNum.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        }

        function escapeHtml(unsafe) {
            if (unsafe === null || unsafe === undefined) return '';
            return String(unsafe).replace(/&/g, "&").replace(/</g, "<").replace(/>/g, ">").replace(/"/g, '"').replace(/'/g, "'");
        }

        // Récupère les filtres actifs depuis N'IMPORTE QUEL conteneur fourni
        function getActiveFilters(container) {
            const activeFilters = {};
            if (!container) return activeFilters;
            container.querySelectorAll('.filter-checkbox:checked').forEach(cb => {
                if (!activeFilters[cb.name]) { activeFilters[cb.name] = []; }
                activeFilters[cb.name].push(cb.value);
            });
            return activeFilters;
        }

        // Récupère la valeur de tri
        function getCurrentSort() {
            return sortSelect?.value || '';
        }

        // Construit le segment /f/... pour l'URL pushState
        function buildFilterUrlSegmentForBrowser(activeFilters) {
            if (!activeFilters || Object.keys(activeFilters).length === 0) return "";
            const parts = [];
            for (const key in activeFilters) { parts.push(`${key}=${activeFilters[key].sort().join(',')}`); }
            return 'f/' + parts.sort().join('/') + '/';
        }

        // --- Fonction Principale de Mise à Jour AJAX (Filtre/Tri/Pagination) ---
        async function updateProductList(page = 1, append = false, triggerSource = 'unknown') {
            if (isAjaxInProgress) {
                console.warn("AJAX request already in progress. Skipping trigger:", triggerSource);
                return;
            }
            if (!currentCategorySlug) { console.error("Category slug missing."); return; }

            isAjaxInProgress = true;

            // 1. Collecter filtres actifs (depuis le panneau visible ou desktop par défaut)
            const currentFilterPanel = (filterContainerMobileContent && mobileOpenContainer?.classList.contains('open')) ? filterContainerMobileContent : filterContainerDesktop;
            const activeFilters = getActiveFilters(currentFilterPanel);

            // 2. Récupérer le tri actuel
            const currentSort = getCurrentSort();

            console.log(`updateProductList: Page=${page}, Append=${append}, Sort='${currentSort}', Trigger='${triggerSource}', Filters:`, activeFilters);

            // 3. Construire les paramètres GET pour l'URL AJAX
            const params = new URLSearchParams();
            params.append('category_slug', currentCategorySlug); // Toujours nécessaire pour la vue AJAX
            params.append('page', page);
            if (currentSort) params.append('sort', currentSort);
            for (const key in activeFilters) {
                activeFilters[key].forEach(value => params.append(key, value));
            }

            // Utilise l'URL spécifique pour le filtrage (FilterProductsView)
            const url = `${filterAjaxUrl}?${params.toString()}`;
            console.log("AJAX Request URL:", url);

            // Feedback visuel
            if (loadingIndicator) loadingIndicator.style.display = 'inline-block';
            if (loadMoreButton && append) loadMoreButton.disabled = true; // Désactive seulement pour load more
            if (!append && productListContainer) productListContainer.style.opacity = '0.5'; // Grise si remplace

            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });

                const contentType = response.headers.get("content-type");
                if (!response.ok) {
                    let errorText = `HTTP error ${response.status}`;
                    if(contentType && contentType.includes("application/json")) { try { const d=await response.json(); errorText=d.error||errorText;} catch(e){} }
                    else { try { errorText=await response.text(); } catch(e){} }
                    throw new Error(errorText);
                }
                if (!contentType || !contentType.includes("application/json")) { throw new Error("Invalid server response type"); }

                const data = await response.json();
                console.log("AJAX Response Data:", data);

                // --- Mettre à jour le DOM ---
                if (productListContainer && data.html_products !== undefined) {
                    if (append) {
                        productListContainer.insertAdjacentHTML('beforeend', data.html_products);
                    } else {
                        productListContainer.innerHTML = data.html_products;
                        // Scroll seulement si on remplace et si on n'est pas déjà en haut
                        const listTop = productListContainer.getBoundingClientRect().top + window.scrollY;
                        if (window.scrollY > listTop - 50) window.scrollTo({ top: listTop - 80, behavior: 'smooth' });
                    }
                }

                // Met à jour les DEUX panneaux de filtres si le HTML est reçu
                if (data.html_filters !== undefined) {
                    // Utilise un préfixe pour rendre les IDs uniques dans le partiel
                    const filterHtmlDesktop = data.html_filters.replace(/id="/g, 'id="desktop-').replace(/for="/g, 'for="desktop-');
                    const filterHtmlMobile = data.html_filters.replace(/id="/g, 'id="mobile-').replace(/for="/g, 'for="mobile-');

                    if (filterContainerDesktop) {
                        filterContainerDesktop.innerHTML = filterHtmlDesktop;
                        attachFilterListeners(filterContainerDesktop);
                        attachClearFilterListener(filterContainerDesktop);
                    }
                    if (filterContainerMobileContent) {
                        filterContainerMobileContent.innerHTML = filterHtmlMobile;
                        attachFilterListeners(filterContainerMobileContent);
                        attachClearFilterListener(filterContainerMobileContent);
                    }
                }

                // Met à jour la pagination si le HTML est reçu
                if (paginationContainer && data.html_pagination !== undefined) {
                    paginationContainer.innerHTML = data.html_pagination;
                    attachPaginationListeners(); // Ré-attache aux nouveaux liens
                }


                if (productCountDisplay && data.product_count !== undefined) {
                    productCountDisplay.textContent = ` (${data.product_count}) `;
                }

                // Met à jour le Titre H1
                if (pageTitleH1) {
                    const baseTitle = pageTitleH1.dataset.baseTitle || (pageTitleH1.textContent.split('(')[0].split(' - Страница')[0].trim()) || "Результаты";
                    let titleContent = escapeHtml(baseTitle);
                    if (data.active_filters_display) { titleContent += ` <span class="page-number-indicator">${escapeHtml(data.active_filters_display)}</span>`; }
                    let countSpan = pageTitleH1.querySelector('#product-count-display-h1'); if (!countSpan) { countSpan = document.createElement('span'); countSpan.id = 'product-count-display-h1'; }
                    if (data.product_count !== undefined) { countSpan.textContent = ` (${data.product_count})`; } else { countSpan.textContent = ''; }
                    let pageSpan = pageTitleH1.querySelector('.page-number-indicator-num'); if (!pageSpan) { pageSpan = document.createElement('span'); pageSpan.className = 'page-number-indicator-num'; }
                    if (data.current_page_number > 1 && data.total_pages > 1) { pageSpan.textContent = ` - Страница ${data.current_page_number}`; } else { pageSpan.textContent = ''; }
                    pageTitleH1.innerHTML = titleContent + countSpan.outerHTML + pageSpan.outerHTML;
                }


                // Met à jour le bouton "Load More"
                if (showMoreContainer && loadMoreButton) {
                    if (data.has_next_page) { // Utilise la clé correcte de la réponse JSON
                        showMoreContainer.style.display = 'block';
                        loadMoreButton.dataset.currentPage = data.current_page_number; // Page actuelle chargée
                        loadMoreButton.dataset.nextPageNumber = data.next_page_number;
                    } else {
                        showMoreContainer.style.display = 'none';
                    }
                }

                // Mettre à jour l'URL du navigateur
                if (window.history.pushState && data.new_url) {
                    window.history.pushState({path: data.new_url}, '', data.new_url);
                    console.log("Browser URL updated to:", data.new_url);
                }

            } catch (error) {
                console.error('Error during AJAX product update:', error);
                alert("Произошла ошибка при обновлении списка продуктов.");
            } finally {
                if (loadingIndicator) loadingIndicator.style.display = 'none';
                if (loadMoreButton) loadMoreButton.disabled = false; // Réactive toujours
                if (productListContainer) productListContainer.style.opacity = '1';
                isAjaxInProgress = false; // Libère le flag
            }
        }

        // --- Fonctions pour attacher les écouteurs (pourraient être combinées) ---
        const debouncedFilterUpdate = debounce(() => updateProductList(1, false, 'filter_change'), 800); // Délai augmenté

        function attachFilterListeners(container) {
            if (!container) return;
            const filterCheckboxes = container.querySelectorAll('.filter-checkbox');
            console.log(`Attaching 'change' listeners to ${filterCheckboxes.length} checkboxes in`, container.id || container);
            filterCheckboxes.forEach(cb => {
                cb.removeEventListener('change', debouncedFilterUpdate);
                cb.addEventListener('change', debouncedFilterUpdate);
            });
        }

        function attachClearFilterListener(container) {
            if (!container) return;
            const clearButton = container.querySelector('.clear-filters-link'); // Trouve DANS le conteneur
            if (clearButton) {
                clearButton.removeEventListener('click', handleClearFilters);
                clearButton.addEventListener('click', handleClearFilters);
            }
        }

        function handleClearFilters(event) {
            event.preventDefault();
            console.log("Clear filters clicked.");
            // Décoche dans les DEUX panneaux pour synchro
            filterContainerDesktop?.querySelectorAll('.filter-checkbox:checked').forEach(cb => cb.checked = false);
            filterContainerMobileContent?.querySelectorAll('.filter-checkbox:checked').forEach(cb => cb.checked = false);
            if(sortSelect) sortSelect.value = ''; // Réinitialise aussi le tri
            updateProductList(1, false, 'clear_filters'); // Met à jour la liste
        }

        function attachPaginationListeners() {
            if (!paginationContainer) return;
            // Nettoie les anciens listeners avant d'ajouter les nouveaux
            paginationContainer.querySelectorAll('.ajax-page-link').forEach(link => {
                link.removeEventListener('click', handlePaginationClick); // Enlève l'ancien
                link.addEventListener('click', handlePaginationClick);    // Ajoute le nouveau
            });
            console.log("Attached listeners to pagination links.");
        }

        function handlePaginationClick(event) {
            const pageLink = event.target.closest('.ajax-page-link');
            if (pageLink) {
                event.preventDefault();
                const pageNum = parseInt(pageLink.dataset.page, 10);
                if (!isNaN(pageNum)) {
                    console.log(`Pagination link clicked, fetching page ${pageNum}.`);
                    updateProductList(pageNum, false, 'pagination_click'); // Remplace contenu
                }
            }
        }

        // --- Gestion Toggle Filtres Mobile ---
        if (mobileToggleTrigger && mobileOpenContainer) {
            console.log("Attaching listener for mobile filter toggle.");
            mobileToggleTrigger.addEventListener('click', (event) => {
                if (event.target !== mobileToggleTrigger && !event.target.closest('.category__mobile-caption')) return;
                mobileOpenContainer.classList.toggle('open');
                console.log("Toggled mobile filter visibility. Parent has 'open':", mobileOpenContainer.classList.contains('open'));
            });
        } else { console.warn("Mobile filter elements not found."); }

        // --- Écouteur pour le tri ---
        if (sortSelect) {
            sortSelect.addEventListener('change', () => {
                console.log("Sort selection changed.");
                updateProductList(1, false, 'sort_change'); // Recharge page 1 avec nouveau tri
            });
        }

        // --- Écouteur pour "Load More" ---
        if (loadMoreButton) {
            loadMoreButton.addEventListener('click', () => {
                if (isAjaxInProgress) return; // Empêche double-clic rapide
                const nextPage = parseInt(loadMoreButton.dataset.nextPageNumber || '2');
                console.log(`Load more clicked, fetching page ${nextPage}`);
                updateProductList(nextPage, true, 'load_more'); // Page suivante, AJOUTE (append=true)
            });
        } else { console.warn("Load more button not found."); }

        // --- Initialisation ---
        attachFilterListeners(filterContainerDesktop);
        attachFilterListeners(filterContainerMobileContent);
        attachClearFilterListener(filterContainerDesktop);
        attachClearFilterListener(filterContainerMobileContent);
        attachPaginationListeners(); // Attache aux liens de pagination initiaux

        console.log("Filter, Sort & Load JS Initialized.");
    }
});
//==========================================================
// Gère le filtrage dynamique AJAX, le tri et le Load More
// ==========================================================


