"use strict";

const $ = (id) => document.getElementById(id);
const state = { session: null, view: "browse", books: [], catalogue: [], selectedBook: null,
  editBook: null, receiptBook: null, reservationAttempt: null, version: 0, searchVersion: 0, reservationVersion: 0, staffVersion: 0, mutations: 0 };
const moneyNumber = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const money = (cents) => `${moneyNumber.format(Number(cents || 0) / 100)} units`;
const isStaff = () => state.session?.identity?.role === "staff";

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(text, className, handler) {
  const node = el("button", `button ${className}`, text);
  node.type = "button";
  node.addEventListener("click", handler);
  return node;
}

function empty(target, title, description) {
  const box = el("div", "empty-state");
  box.append(el("strong", "", title), el("span", "", description));
  target.replaceChildren(box);
}

function notice(message, error = false) {
  const node = $("notice");
  const dismiss = button("×", "", () => { node.hidden = true; });
  dismiss.setAttribute("aria-label", "Dismiss message");
  node.className = `notice${error ? " error" : ""}`;
  node.replaceChildren(dismiss, document.createTextNode(message));
  node.hidden = false;
}

function formError(id, message = "") {
  $(id).textContent = message;
  $(id).hidden = !message;
}

async function api(path, { method = "GET", body } = {}) {
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (method !== "GET") headers["X-CSRF-Token"] = state.session?.csrf_token || "";
  let response;
  try {
    response = await fetch(path, { method, headers, credentials: "same-origin",
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}) });
  } catch (cause) {
    const error = new Error("The local application could not be reached. Check that it is running, then try again.");
    error.cause = cause;
    error.confirmed = false;
    throw error;
  }
  let data;
  try { data = await response.json(); }
  catch {
    const error = new Error("The application returned an unreadable response. Please try again.");
    error.confirmed = false;
    throw error;
  }
  if (!response.ok) {
    const error = new Error(data.error || `The request failed (${response.status}).`);
    error.status = response.status;
    error.confirmed = true;
    throw error;
  }
  return data;
}

function updateSessionControls() {
  const selector = $("identity-select");
  selector.replaceChildren();
  for (const identity of state.session.identities) {
    const option = el("option", "", `${identity.name} · ${identity.role === "staff" ? "Staff" : "Customer"}`);
    option.value = identity.id;
    selector.append(option);
  }
  selector.value = state.session.identity?.id || "";
  selector.disabled = state.mutations > 0;
  $("tab-staff").hidden = !isStaff();
  const reservationsTitle = isStaff() ? "Staff reservations" : "My reservations";
  $("tab-reservations").textContent = reservationsTitle;
  $("reservations-heading").textContent = reservationsTitle;
  $("reservation-help").textContent = isStaff()
    ? "View reservations for every demo customer. Confirm collection only after the books have been collected in store."
    : "Bring your reservation reference when you collect your books. You can cancel a reservation while it is pending collection.";
  if (!isStaff() && state.view === "staff") showView("browse", false);
}

async function refreshSession() {
  state.session = await api("/api/session");
  updateSessionControls();
}

function showView(view, load = true) {
  if (view === "staff" && !isStaff()) return;
  state.view = view;
  for (const key of ["browse", "reservations", "staff"]) {
    $("view-" + key).hidden = key !== view;
    const tab = $("tab-" + key);
    tab.classList.toggle("active", key === view);
    if (key === view) tab.setAttribute("aria-current", "page");
    else tab.removeAttribute("aria-current");
  }
  if (load) {
    if (view === "browse") loadBooks();
    if (view === "reservations") loadReservations();
    if (view === "staff") loadStaff();
  }
}

function bookCover(book) {
  const art = el("div", "book-art");
  art.setAttribute("aria-hidden", "true");
  const cover = el("div", `book-cover cover-${Math.abs(Number(book.id) || 0) % 6}`);
  cover.append(el("span", "cover-wordmark", "BOOKBRIDGE"), el("span", "cover-title", book.title),
    el("span", "cover-line"), el("span", "cover-author", book.author));
  art.append(cover);
  return art;
}

function renderBooks(books) {
  $("book-count").textContent = `${books.length} ${books.length === 1 ? "title" : "titles"} on the shelf`;
  if (!books.length) {
    empty($("book-grid"), "No books found", "Try a different title, author or category.");
    return;
  }
  $("book-grid").replaceChildren();
  for (const book of books) {
    const card = el("article", "book-card");
    card.append(bookCover(book));
    const info = el("div", "book-info");
    info.append(el("span", "category-label", book.category), el("h3", "", book.title), el("p", "book-author", book.author));
    const bottom = el("div", "book-bottom");
    const priceRow = el("div", "book-price-row");
    const price = el("span", "book-price", moneyNumber.format(book.price_cents / 100) + " ");
    price.append(el("small", "", "units"));
    const inStock = Number(book.available_quantity) > 0;
    priceRow.append(price, el("span", `stock-label${inStock ? "" : " unavailable"}`,
      inStock ? `${book.available_quantity} available` : "Out of stock"));
    const open = button("View book", "outline", () => openBook(book.id));
    const arrow = el("span", "", "↗"); arrow.setAttribute("aria-hidden", "true"); open.append(arrow);
    open.setAttribute("aria-label", `View ${book.title}`);
    bottom.append(priceRow, open); info.append(bottom); card.append(info); $("book-grid").append(card);
  }
}

async function loadBooks() {
  const version = state.version;
  const searchVersion = ++state.searchVersion;
  const params = new URLSearchParams({ q: $("search-input").value.trim(), category: $("category-filter").value,
    sort: $("sort-select").value });
  $("book-grid").setAttribute("aria-busy", "true");
  try {
    const data = await api("/api/books?" + params);
    if (version !== state.version || searchVersion !== state.searchVersion) return;
    state.books = data.books;
    const selectedCategory = $("category-filter").value;
    const all = el("option", "", "All categories"); all.value = "";
    $("category-filter").replaceChildren(all);
    const categories = [...new Set([...(data.categories || []), ...(selectedCategory ? [selectedCategory] : [])])].sort();
    for (const name of categories) { const option = el("option", "", name); option.value = name; $("category-filter").append(option); }
    $("category-filter").value = selectedCategory;
    renderBooks(data.books);
  } catch (error) {
    if (version === state.version && searchVersion === state.searchVersion) {
      empty($("book-grid"), "The collection could not be loaded", error.message);
      $("book-count").textContent = "";
    }
  } finally { if (searchVersion === state.searchVersion) $("book-grid").removeAttribute("aria-busy"); }
}

async function openBook(id) {
  const version = state.version;
  try {
    const data = await api(`/api/books/${id}`);
    if (version !== state.version) return;
    state.selectedBook = data.book || data;
    state.reservationAttempt = null;
    const book = state.selectedBook;
    const content = el("div", "dialog-book-layout");
    const details = el("div", "");
    const title = el("h2", "", book.title); title.id = "book-dialog-title";
    details.append(el("p", "category-label", book.category), title, el("p", "book-author", book.author),
      el("p", "book-price", money(book.price_cents)), el("p", "muted", `${book.available_quantity} copies available`));
    content.append(bookCover(book), details); $("book-dialog-content").replaceChildren(content);
    $("reserve-quantity").value = "1";
    $("reserve-quantity").max = String(book.available_quantity);
    $("reserve-quantity").disabled = false;
    $("reserve-submit").textContent = "Reserve for collection";
    formError("reserve-error");
    const reservable = !isStaff() && book.is_listed && book.available_quantity > 0;
    $("reserve-form").hidden = !reservable;
    $("reserve-unavailable").hidden = reservable;
    $("reserve-unavailable").textContent = isStaff() ? "Switch to a customer demo identity to make a reservation."
      : "This title is currently unavailable for reservation.";
    updateReservationTotal();
    $("book-dialog").showModal();
  } catch (error) { notice(error.message, true); }
}

function updateReservationTotal() {
  const quantity = Number($("reserve-quantity").value);
  $("reserve-total").textContent = Number.isInteger(quantity) && quantity > 0 && state.selectedBook
    ? `Reservation amount: ${money(quantity * state.selectedBook.price_cents)}` : "Enter a positive whole number.";
}

async function withBusy(buttonNode, dialog, operation) {
  if (buttonNode.disabled) return;
  const original = buttonNode.textContent;
  buttonNode.disabled = true; buttonNode.textContent = "Saving…";
  state.mutations += 1; $("identity-select").disabled = true;
  if (dialog) dialog.dataset.busy = "true";
  try { await operation(); }
  finally {
    buttonNode.disabled = false;
    if (buttonNode.textContent === "Saving…") buttonNode.textContent = original;
    state.mutations -= 1; $("identity-select").disabled = state.mutations > 0;
    if (dialog) delete dialog.dataset.busy;
  }
}

async function refreshData() {
  await Promise.all([loadBooks(), loadReservations(), ...(isStaff() ? [loadStaff()] : [])]);
}

async function submitReservation(event) {
  event.preventDefault();
  if (!$("reserve-form").reportValidity() || !state.selectedBook) return;
  const quantity = Number($("reserve-quantity").value);
  if (!Number.isInteger(quantity) || quantity < 1) { formError("reserve-error", "Enter a positive whole number of copies."); return; }
  if (!state.reservationAttempt) state.reservationAttempt = {
    book_id: state.selectedBook.id, quantity, request_key: crypto.randomUUID()
  };
  const attempt = state.reservationAttempt;
  await withBusy($("reserve-submit"), $("book-dialog"), async () => {
    formError("reserve-error");
    try {
      const data = await api("/api/reservations", { method: "POST", body: attempt });
      const reservation = data.reservation || data;
      state.reservationAttempt = null;
      $("book-dialog").close();
      notice(`Reservation ${reservation.reference || "created"} is ready for collection. Pay for your books in store.`);
      showView("reservations", false);
      await refreshData();
    } catch (error) {
      if (error.confirmed) {
        state.reservationAttempt = null;
        $("reserve-quantity").disabled = false;
        $("reserve-submit").textContent = "Reserve for collection";
      } else {
        $("reserve-quantity").disabled = true;
        $("reserve-submit").textContent = "Retry the same reservation";
      }
      formError("reserve-error", error.message + (!error.confirmed ? " The result is uncertain. Retry uses the same request and will not create a duplicate." : ""));
    }
  });
}

function renderReservations(reservations) {
  const list = $("reservation-list");
  if (!reservations.length) { empty(list, "No reservations here yet", $("reservation-filter").value
    ? "No reservations match this status." : isStaff() ? "Customer reservations will appear here." : "Browse the collection to reserve your first book."); return; }
  list.replaceChildren();
  for (const reservation of reservations) {
    const card = el("article", "reservation-card");
    const details = el("div", "");
    details.append(el("p", "reservation-ref", reservation.reference), el("h3", "", reservation.title));
    const meta = `${reservation.quantity} ${reservation.quantity === 1 ? "copy" : "copies"} · ${money(reservation.unit_price_cents)} each`;
    details.append(el("p", "reservation-meta", meta));
    if (isStaff()) details.append(el("p", "reservation-meta", `Customer: ${reservation.customer_name}`));
    if (reservation.created_at) {
      const date = new Date(reservation.created_at);
      const readableDate = Number.isNaN(date.getTime()) ? reservation.created_at : date.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
      details.append(el("p", "reservation-meta", `Reserved ${readableDate}`));
    }
    const amount = el("div", "reservation-amount");
    amount.append(el("strong", "", money(reservation.amount_cents)), el("small", "", "Saved reservation amount"));
    const actions = el("div", "reservation-actions");
    const statusClass = reservation.status === "Completed" ? "completed" : reservation.status === "Cancelled" ? "cancelled" : "pending";
    actions.append(el("span", `badge ${statusClass}`, reservation.status));
    if (reservation.status === "Pending collection") {
      const action = isStaff() ? "complete" : "cancel";
      actions.append(button(isStaff() ? "Confirm collection" : "Cancel reservation", isStaff() ? "primary small" : "danger small",
        (event) => updateReservation(reservation, action, event.currentTarget)));
    }
    card.append(details, amount, actions); list.append(card);
  }
}

async function loadReservations() {
  if (!state.session?.identity) return;
  const version = state.version;
  const requestVersion = ++state.reservationVersion;
  try {
    const params = new URLSearchParams({ status: $("reservation-filter").value });
    const data = await api("/api/reservations?" + params);
    if (version === state.version && requestVersion === state.reservationVersion) renderReservations(data.reservations);
  } catch (error) { if (version === state.version && requestVersion === state.reservationVersion) empty($("reservation-list"), "Reservations could not be loaded", error.message); }
}

function confirmReservationAction(reservation, action) {
  const dialog = $("confirmation-dialog");
  if (dialog.open) return Promise.resolve(false);
  const question = action === "cancel" ? `Cancel reservation ${reservation.reference}? Its copies will become available again.`
    : `Confirm that reservation ${reservation.reference} has been collected? This records collection only.`;
  $("confirmation-heading").textContent = action === "cancel" ? "Cancel this reservation?" : "Confirm collection?";
  $("confirmation-message").textContent = question;
  $("confirmation-submit").textContent = action === "cancel" ? "Cancel reservation" : "Confirm collection";
  $("confirmation-submit").className = `button ${action === "cancel" ? "danger" : "primary"}`;
  // Escape, the close button and "Keep unchanged" all resolve without a request.
  dialog.returnValue = "keep";
  return new Promise((resolve) => {
    dialog.addEventListener("close", () => resolve(dialog.returnValue === "confirm"), { once: true });
    dialog.showModal();
  });
}

async function updateReservation(reservation, action, target) {
  const version = state.version;
  const confirmed = await confirmReservationAction(reservation, action);
  if (!confirmed || version !== state.version) return;
  await withBusy(target, null, async () => {
    try {
      await api(`/api/reservations/${reservation.id}/${action}`, { method: "POST", body: {} });
      notice(action === "cancel" ? "Reservation cancelled. The reserved copies are available again." : "Collection confirmed. The reservation is now completed.");
      await refreshData();
    } catch (error) { notice(error.message, true); }
  });
}

function renderCatalogue(books) {
  const body = $("catalogue-body"); body.replaceChildren();
  if (!books.length) { const row = el("tr", ""); const cell = el("td", "", "No titles yet. Add your first book to begin."); cell.colSpan = 6; row.append(cell); body.append(row); return; }
  for (const book of books) {
    const row = el("tr", "");
    const title = el("td", ""); title.append(el("strong", "", book.title), el("small", "", book.author));
    const status = el("td", ""); status.append(el("span", `badge ${book.is_listed ? "listed" : "unlisted"}`, book.is_listed ? "Listed" : "Unlisted"));
    const actions = el("td", ""); const buttons = el("div", "table-actions");
    buttons.append(button("Edit", "outline small", () => editBook(book)), button("Receive stock", "secondary small", () => receiveStock(book)));
    actions.append(buttons);
    row.append(title, el("td", "", book.category), el("td", "", money(book.price_cents)), el("td", "", book.available_quantity), status, actions);
    body.append(row);
  }
}

async function loadStaff() {
  if (!isStaff()) return;
  const version = state.version;
  const requestVersion = ++state.staffVersion;
  try {
    const [catalogue, summary] = await Promise.all([api("/api/books?show_unlisted=1&sort=title"), api("/api/summary")]);
    if (version !== state.version || requestVersion !== state.staffVersion || !isStaff()) return;
    state.catalogue = catalogue.books;
    renderCatalogue(catalogue.books);
    $("summary-count").textContent = summary.count;
    $("summary-quantity").textContent = summary.completed_quantity;
    $("summary-amount").textContent = money(summary.amount_cents);
  } catch (error) {
    if (version === state.version && requestVersion === state.staffVersion) {
      $("summary-count").textContent = "—"; $("summary-quantity").textContent = "—"; $("summary-amount").textContent = "—";
      $("catalogue-body").replaceChildren();
      notice(error.message, true);
    }
  }
}

function editBook(book = null) {
  state.editBook = book;
  $("book-form").reset();
  $("edit-heading").textContent = book ? "Edit book" : "Add a book";
  $("edit-title").value = book?.title || "";
  $("edit-author").value = book?.author || "";
  $("edit-category").value = book?.category || "";
  $("edit-price").value = book ? (book.price_cents / 100).toFixed(2) : "";
  $("edit-stock").value = "0";
  $("edit-stock").disabled = Boolean(book);
  $("initial-stock-field").hidden = Boolean(book);
  $("edit-stock-note").hidden = !book;
  $("edit-listed").checked = book ? Boolean(book.is_listed) : true;
  formError("book-form-error");
  $("edit-dialog").showModal();
}

async function saveBook(event) {
  event.preventDefault();
  if (!$("book-form").reportValidity()) return;
  const data = { title: $("edit-title").value.trim(), author: $("edit-author").value.trim(), category: $("edit-category").value.trim(),
    price: $("edit-price").value, is_listed: $("edit-listed").checked };
  if (!state.editBook) data.available_quantity = Number($("edit-stock").value);
  await withBusy($("book-save"), $("edit-dialog"), async () => {
    formError("book-form-error");
    try {
      await api(state.editBook ? `/api/books/${state.editBook.id}` : "/api/books", { method: state.editBook ? "PATCH" : "POST", body: data });
      $("edit-dialog").close(); notice(state.editBook ? "Book details updated." : "Book added to the catalogue."); await refreshData();
    } catch (error) { formError("book-form-error", error.message); }
  });
}

function receiveStock(book) {
  state.receiptBook = book;
  $("receipt-title").textContent = book.title;
  $("receipt-current").textContent = `${book.available_quantity} copies are currently available. Received copies will be added to this quantity.`;
  $("receipt-quantity").value = "1";
  formError("receipt-error"); $("receipt-dialog").showModal();
}

async function saveReceipt(event) {
  event.preventDefault();
  if (!$("receipt-form").reportValidity()) return;
  const quantity = Number($("receipt-quantity").value);
  if (!Number.isInteger(quantity) || quantity <= 0) { formError("receipt-error", "Enter a positive whole number of received copies."); return; }
  await withBusy($("receipt-save"), $("receipt-dialog"), async () => {
    formError("receipt-error");
    try {
      await api(`/api/books/${state.receiptBook.id}/receipts`, { method: "POST", body: { quantity } });
      $("receipt-dialog").close(); notice(`${quantity} ${quantity === 1 ? "copy" : "copies"} added to stock.`); await refreshData();
    } catch (error) { formError("receipt-error", error.message); }
  });
}

async function changeIdentity() {
  const identityId = $("identity-select").value;
  $("identity-select").disabled = true;
  state.version += 1;
  $("notice").hidden = true;
  for (const dialog of document.querySelectorAll("dialog")) dialog.close();
  $("reservation-list").replaceChildren(); $("catalogue-body").replaceChildren();
  $("reservation-filter").value = "";
  try {
    await api("/api/session", { method: "POST", body: { identity_id: identityId } });
    await refreshSession();
    await refreshData();
  } catch (error) {
    notice(error.message, true);
    try { await refreshSession(); await refreshData(); } catch { /* Keep the original error visible. */ }
  } finally { $("identity-select").disabled = false; }
}

document.querySelectorAll("[data-view]").forEach((node) => node.addEventListener("click", () => showView(node.dataset.view)));
document.querySelectorAll("[data-close]").forEach((node) => node.addEventListener("click", () => {
  const dialog = $(node.dataset.close); if (dialog.dataset.busy !== "true") dialog.close();
}));
document.querySelectorAll("dialog").forEach((dialog) => dialog.addEventListener("cancel", (event) => {
  if (dialog.dataset.busy === "true") event.preventDefault();
}));
$("book-dialog").addEventListener("close", () => {
  if (state.reservationAttempt) notice("A reservation response was not received. Check My reservations before making another reservation.", true);
});
$("identity-select").addEventListener("change", changeIdentity);
$("search-form").addEventListener("submit", (event) => { event.preventDefault(); loadBooks(); });
$("category-filter").addEventListener("change", loadBooks);
$("sort-select").addEventListener("change", loadBooks);
$("reservation-filter").addEventListener("change", loadReservations);
$("reserve-quantity").addEventListener("input", updateReservationTotal);
$("reserve-form").addEventListener("submit", submitReservation);
$("add-book").addEventListener("click", () => editBook());
$("book-form").addEventListener("submit", saveBook);
$("receipt-form").addEventListener("submit", saveReceipt);

async function start() {
  try {
    await refreshSession();
    if (!state.session.identity) {
      const firstCustomer = state.session.identities.find((identity) => identity.role === "customer");
      if (firstCustomer) {
        await api("/api/session", { method: "POST", body: { identity_id: firstCustomer.id } });
        await refreshSession();
      }
    }
    await refreshData();
  } catch (error) {
    empty($("book-grid"), "BookBridge could not start", "Check that the local application is running, then refresh this page.");
    notice(error.message, true);
  }
}
start();
