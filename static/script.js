
"use strict";

// --------------------------------------------------
// DOM ELEMENTS
// --------------------------------------------------

const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const mobileMenu = document.getElementById("mobile-menu");
const mobileOverlay = document.getElementById("mobile-overlay");

const themeToggle = document.getElementById("theme-toggle");
const themeIcon = document.getElementById("theme-icon");

const currentSection = document.getElementById("current-section");
const navigationButtons = document.querySelectorAll("[data-view]");
const views = document.querySelectorAll(".view");

const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-query");
const searchStatus = document.getElementById("search-status");
const searchResults = document.getElementById("search-results");
const searchEmpty = document.getElementById("search-empty");

const documentForm = document.getElementById("document-form");
const documentIdInput = document.getElementById("document-id");
const documentTitleInput = document.getElementById("document-title");
const documentContentInput = document.getElementById("document-content");
const documentStatus = document.getElementById("document-status");
const saveSuccessPanel = document.getElementById("save-success-panel");
const successDocTitle = document.getElementById("success-doc-title");
const successDocId = document.getElementById("success-doc-id");
const goToSearchBtn = document.getElementById("go-to-search-btn");
const addAnotherBtn = document.getElementById("add-another-btn");

const manageStatus = document.getElementById("manage-status");
const documentList = document.getElementById("document-list");

// --------------------------------------------------
// HELPERS
// --------------------------------------------------

function setStatus(element, message) {
    if (element) {
        element.textContent = message;
    }
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);

    let data = {};
    try {
        data = await response.json();
    } catch {
        // Some error responses may not contain JSON.
    }

    if (!response.ok) {
        const detail = data.detail;
        const message =
            typeof detail === "string"
                ? detail
                : detail
                    ? JSON.stringify(detail)
                    : `Request failed (${response.status})`;

        throw new Error(message);
    }

    return data;
}

/**
 * Build a short excerpt from document content, centering on the query term
 * when possible. Uses plain text — never innerHTML.
 */
function makeExcerpt(content, query = "", maxLength = 190) {
    if (!content) {
        return "No document content available.";
    }

    const text = content.trim();
    const normalizedText = text.toLowerCase();
    const normalizedQuery = query.trim().toLowerCase();

    let start = 0;

    if (normalizedQuery) {
        const matchIndex = normalizedText.indexOf(normalizedQuery);

        if (matchIndex > 55) {
            start = matchIndex - 55;
        }
    }

    let excerpt = text.slice(start, start + maxLength).trim();

    if (start > 0) {
        excerpt = "\u2026" + excerpt;
    }

    if (start + maxLength < text.length) {
        excerpt += "\u2026";
    }

    return excerpt;
}

// --------------------------------------------------
// THEME
// --------------------------------------------------

function applyTheme(theme) {
    const selectedTheme = theme === "dark" ? "dark" : "light";

    document.documentElement.dataset.theme = selectedTheme;

    if (themeIcon) {
        themeIcon.textContent = selectedTheme === "dark" ? "\u2600" : "\u263e";
    }

    if (themeToggle) {
        const nextTheme = selectedTheme === "dark" ? "light" : "dark";

        themeToggle.setAttribute(
            "aria-label",
            `Switch to ${nextTheme} theme`
        );

        themeToggle.setAttribute("title", `Switch to ${nextTheme} theme`);
    }

    const themeColorMeta = document.querySelector('meta[name="theme-color"]');
    if (themeColorMeta) {
        themeColorMeta.setAttribute(
            "content",
            selectedTheme === "dark" ? "#202923" : "#f5f3ec"
        );
    }
}

function initializeTheme() {
    let savedTheme = "light";

    try {
        savedTheme = localStorage.getItem("minisearch-theme") || "light";
    } catch {
        // Continue with the default theme if storage is unavailable.
    }

    applyTheme(savedTheme);
}

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const nextTheme =
            document.documentElement.dataset.theme === "dark"
                ? "light"
                : "dark";

        applyTheme(nextTheme);

        try {
            localStorage.setItem("minisearch-theme", nextTheme);
        } catch {
            // Theme still works for the current page.
        }
    });
}

// --------------------------------------------------
// SIDEBAR AND MOBILE NAVIGATION
// --------------------------------------------------

function isMobileLayout() {
    return window.matchMedia("(max-width: 760px)").matches;
}

function closeMobileNavigation() {
    document.body.classList.remove("mobile-nav-open");

    if (mobileMenu) {
        mobileMenu.setAttribute("aria-expanded", "false");
    }
}

function toggleSidebar() {
    if (isMobileLayout()) {
        const isOpen = document.body.classList.toggle("mobile-nav-open");

        if (mobileMenu) {
            mobileMenu.setAttribute("aria-expanded", String(isOpen));
        }

        return;
    }

    document.body.classList.toggle("sidebar-collapsed");

    const isExpanded =
        !document.body.classList.contains("sidebar-collapsed");

    if (sidebarToggle) {
        sidebarToggle.setAttribute("aria-expanded", String(isExpanded));
        sidebarToggle.setAttribute(
            "aria-label",
            isExpanded ? "Collapse sidebar" : "Expand sidebar"
        );
    }

    try {
        localStorage.setItem(
            "minisearch-sidebar-collapsed",
            String(!isExpanded)
        );
    } catch {
        // Sidebar remains functional for this session.
    }
}

if (sidebarToggle) {
    sidebarToggle.addEventListener("click", toggleSidebar);
}

if (mobileMenu) {
    mobileMenu.addEventListener("click", toggleSidebar);
}

if (mobileOverlay) {
    mobileOverlay.addEventListener("click", closeMobileNavigation);
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeMobileNavigation();
    }
});

function initializeSidebar() {
    if (isMobileLayout()) {
        closeMobileNavigation();
        return;
    }

    let collapsed = false;

    try {
        collapsed =
            localStorage.getItem("minisearch-sidebar-collapsed") === "true";
    } catch {
        // Use the expanded sidebar by default.
    }

    document.body.classList.toggle("sidebar-collapsed", collapsed);

    if (sidebarToggle) {
        sidebarToggle.setAttribute("aria-expanded", String(!collapsed));
        sidebarToggle.setAttribute(
            "aria-label",
            collapsed ? "Expand sidebar" : "Collapse sidebar"
        );
    }
}

window.addEventListener("resize", () => {
    if (!isMobileLayout()) {
        closeMobileNavigation();
        initializeSidebar();
    }
});

// --------------------------------------------------
// VIEW NAVIGATION
// --------------------------------------------------

const viewNames = {
    search: "Search",
    add: "Add Documents",
    manage: "Manage Documents"
};

async function showView(viewName) {
    if (!viewNames[viewName]) {
        return;
    }

    views.forEach((view) => {
        const isActive = view.id === `${viewName}-view`;
        view.hidden = !isActive;
        view.classList.toggle("active", isActive);
    });

    navigationButtons.forEach((button) => {
        const isActive = button.dataset.view === viewName;

        button.classList.toggle("active", isActive);

        if (isActive) {
            button.setAttribute("aria-current", "page");
        } else {
            button.removeAttribute("aria-current");
        }
    });

    if (currentSection) {
        currentSection.textContent = viewNames[viewName];
    }

    closeMobileNavigation();

    if (viewName === "manage") {
        await loadDocuments();
    }

    if (viewName === "search" && searchInput) {
        searchInput.focus({ preventScroll: true });
    }

    if (viewName === "add") {
        // Ensure form is visible and success panel is hidden when navigating
        // to the Add view from another section.
        hideSaveSuccessPanel();
    }
}

navigationButtons.forEach((button) => {
    button.addEventListener("click", () => {
        showView(button.dataset.view);
    });
});

// --------------------------------------------------
// SEARCH
// --------------------------------------------------

function showSearchEmptyState(message, description = "") {
    if (!searchEmpty) {
        return;
    }

    searchEmpty.hidden = false;

    const heading = searchEmpty.querySelector("h2, h3");
    const paragraph = searchEmpty.querySelector("p");

    if (heading && message) {
        heading.textContent = message;
    }

    if (paragraph && description) {
        paragraph.textContent = description;
    }
}

function hideSearchEmptyState() {
    if (searchEmpty) {
        searchEmpty.hidden = true;
    }
}

/**
 * Build a search result card.
 *
 * The API now returns a `snippet` field directly, so we no longer need
 * per-result /documents/{id} requests (eliminating the N+1 problem).
 * We fall back to makeExcerpt on the snippet itself if needed.
 */
function createSearchResult(result, query) {
    const card = document.createElement("article");
    card.className = "result-card";
    card.setAttribute("aria-label", result.title || `Document ${result.id}`);

    // Icon column
    const symbol = document.createElement("div");
    symbol.className = "document-symbol";
    symbol.setAttribute("aria-hidden", "true");
    symbol.textContent = "\u2399";

    // Text column
    const copy = document.createElement("div");
    copy.className = "result-copy";

    const title = document.createElement("h3");
    title.textContent = result.title || `Document ${result.id}`;

    const excerpt = document.createElement("p");
    excerpt.className = "result-excerpt";
    // Use snippet from API; center it on the query term for better context
    const snippetText = result.snippet || "";
    excerpt.textContent = makeExcerpt(snippetText, query, 190);

    const meta = document.createElement("p");
    meta.className = "result-meta";
    meta.textContent = `ID: ${result.id}`;

    copy.append(title, excerpt, meta);
    card.append(symbol, copy);

    return card;
}

if (searchForm) {
    searchForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const query = searchInput.value.trim();

        if (!query) {
            setStatus(searchStatus, "Enter a search query first.");
            searchInput.focus();
            return;
        }

        setStatus(searchStatus, "Searching documents\u2026");
        searchResults.replaceChildren();
        hideSearchEmptyState();

        try {
            const params = new URLSearchParams({
                q: query,
                k: "10"
            });

            const data = await apiRequest(`/search?${params}`);

            if (!Array.isArray(data.results) || data.results.length === 0) {
                setStatus(searchStatus, "No matching documents found.");

                showSearchEmptyState(
                    "No results found",
                    "Try different keywords, or add a document to your collection."
                );

                return;
            }

            // Build result cards from the search response directly.
            // The API includes a `snippet` field, so no per-result fetch needed.
            const cards = data.results.map((result) =>
                createSearchResult(result, query)
            );

            searchResults.replaceChildren(...cards);

            setStatus(
                searchStatus,
                `Found ${data.count ?? data.results.length} matching document(s).`
            );
        } catch (error) {
            console.error("Search error:", error);

            setStatus(
                searchStatus,
                `Unable to search: ${error.message}`
            );

            showSearchEmptyState(
                "Search unavailable",
                "An error occurred while searching. Please try again."
            );
        }
    });
}

// --------------------------------------------------
// ADD DOCUMENTS — save-success panel
// --------------------------------------------------

function showSaveSuccessPanel(title, id) {
    if (!saveSuccessPanel || !documentForm) {
        return;
    }

    if (successDocTitle) {
        successDocTitle.textContent = title;
    }
    if (successDocId) {
        successDocId.textContent = `ID: ${id}`;
    }

    documentForm.hidden = true;
    saveSuccessPanel.hidden = false;

    // Move focus to the panel heading for screen reader announcement
    const heading = saveSuccessPanel.querySelector("h2, h3");
    if (heading) {
        heading.focus();
    }
}

function hideSaveSuccessPanel() {
    if (!saveSuccessPanel || !documentForm) {
        return;
    }

    saveSuccessPanel.hidden = true;
    documentForm.hidden = false;
}

if (goToSearchBtn) {
    goToSearchBtn.addEventListener("click", () => {
        hideSaveSuccessPanel();
        showView("search");
    });
}

if (addAnotherBtn) {
    addAnotherBtn.addEventListener("click", () => {
        hideSaveSuccessPanel();
        if (documentForm) {
            documentForm.reset();
        }
        setStatus(documentStatus, "");
        if (documentIdInput) {
            documentIdInput.focus();
        }
    });
}

if (documentForm) {
    documentForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const rawId = documentIdInput.value.trim();
        const title = documentTitleInput.value.trim();
        const content = documentContentInput.value.trim();

        if (!rawId || !title || !content) {
            setStatus(documentStatus, "Complete all fields before saving.");
            return;
        }

        const id = Number(rawId);

        if (!Number.isSafeInteger(id)) {
            setStatus(documentStatus, "Document ID must be a valid integer.");
            documentIdInput.focus();
            return;
        }

        if (id < 1) {
            setStatus(documentStatus, "Document ID must be a positive integer.");
            documentIdInput.focus();
            return;
        }

        setStatus(documentStatus, "Saving document\u2026");

        const submitButton = documentForm.querySelector(
            'button[type="submit"], button:not([type])'
        );

        if (submitButton) {
            submitButton.disabled = true;
        }

        try {
            const data = await apiRequest("/documents", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ id, title, content })
            });

            // Show the polished success panel instead of a plain text message.
            showSaveSuccessPanel(data.title, data.id);

        } catch (error) {
            console.error("Add document error:", error);

            setStatus(
                documentStatus,
                `Could not save document: ${error.message}`
            );
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });
}

// --------------------------------------------------
// MANAGE DOCUMENTS
// --------------------------------------------------

/**
 * Build one document row for the Manage view.
 *
 * NOTE: The loop variable is named `doc` (not `document`) to avoid
 * shadowing the global `window.document` object, which would break
 * all DOM API calls inside this function.
 */
function createDocumentRow(doc) {
    const row = document.createElement("article");
    row.className = "document-row";
    row.setAttribute(
        "aria-label",
        `Document: ${doc.title || `ID ${doc.id}`}`
    );

    // Icon column
    const symbol = document.createElement("div");
    symbol.className = "document-symbol";
    symbol.setAttribute("aria-hidden", "true");
    symbol.textContent = "\u2399";

    // Text column
    const copy = document.createElement("div");
    copy.className = "document-copy";

    const title = document.createElement("h3");
    title.textContent = doc.title || `Document ${doc.id}`;

    const excerpt = document.createElement("p");
    excerpt.textContent = makeExcerpt(doc.content || "");

    const idLabel = document.createElement("p");
    idLabel.className = "document-meta";
    idLabel.textContent = `ID: ${doc.id}`;

    copy.append(title, excerpt, idLabel);

    // Delete button
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-button";
    deleteButton.setAttribute("aria-hidden", "true");
    // Use the × character as the icon; screen-reader label is set separately
    deleteButton.textContent = "\u00d7";
    deleteButton.setAttribute(
        "aria-label",
        `Delete "${doc.title || `Document ${doc.id}`}"`
    );
    deleteButton.setAttribute("aria-hidden", "false");

    deleteButton.addEventListener("click", async () => {
        const confirmed = window.confirm(
            `Delete "${doc.title || `Document ${doc.id}`}"?\n\nThis action cannot be undone.`
        );

        if (!confirmed) {
            return;
        }

        deleteButton.disabled = true;
        setStatus(manageStatus, "Deleting document\u2026");

        try {
            await apiRequest(
                `/documents/${encodeURIComponent(doc.id)}`,
                { method: "DELETE" }
            );

            // Refresh the full list after a successful deletion.
            await loadDocuments();
        } catch (error) {
            console.error("Delete document error:", error);

            setStatus(
                manageStatus,
                `Could not delete document: ${error.message}`
            );

            deleteButton.disabled = false;
        }
    });

    row.append(symbol, copy, deleteButton);
    return row;
}

async function loadDocuments() {
    if (!documentList || !manageStatus) {
        return;
    }

    documentList.replaceChildren();
    setStatus(manageStatus, "Loading documents\u2026");

    try {
        const data = await apiRequest("/documents");

        // API returns { count: N, documents: [...] }
        const documents = Array.isArray(data)
            ? data
            : Array.isArray(data.documents)
                ? data.documents
                : [];

        if (documents.length === 0) {
            setStatus(manageStatus, "No documents have been added yet.");
            return;
        }

        documents.sort((a, b) => a.id - b.id);

        const rows = documents.map((doc) => createDocumentRow(doc));
        documentList.replaceChildren(...rows);

        setStatus(
            manageStatus,
            `${documents.length} document(s) in your collection.`
        );
    } catch (error) {
        console.error("Load documents error:", error);

        setStatus(
            manageStatus,
            `Could not load documents: ${error.message}`
        );

        // Provide a retry action — append to documentList, not manageStatus
        const retryButton = document.createElement("button");
        retryButton.type = "button";
        retryButton.className = "secondary-button";
        retryButton.textContent = "Retry";
        retryButton.addEventListener("click", loadDocuments);

        documentList.replaceChildren(retryButton);
    }
}

// --------------------------------------------------
// INITIALIZE
// --------------------------------------------------

initializeTheme();
initializeSidebar();

if (sidebar) {
    sidebar.setAttribute("aria-label", "Main navigation");
}

showView("search");

console.log("MiniSearch interface initialized.");
