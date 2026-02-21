/* erklärt sich selber*/
let backend = null;
let backendReady = false;
// html elemente getten
const statusChip = document.getElementById("statusChip");
const assignBtn = document.getElementById("assignBtn");
const uploadBtn = document.getElementById("uploadBtn");
const notifList = document.getElementById("notifList");
const modal = document.getElementById("modal");
const modalTitle = document.getElementById("modalTitle");
const modalBody = document.getElementById("modalBody");
const modalClose = document.getElementById("modalClose");
const titlebar = document.getElementById("titlebar");
const minBtn = document.getElementById("minBtn");
const maxBtn = document.getElementById("maxBtn");
const closeBtn = document.getElementById("closeBtn");
const externalBtn = document.getElementById("externalBtn");
const externalMenu = document.getElementById("externalMenu");
const externalItems = document.querySelectorAll(".external-item");

// verbindung für Python bestätigen
function setReady(ready) {
    backendReady = ready;
    assignBtn.disabled = !ready;
    uploadBtn.disabled = !ready;
    statusChip.textContent = ready ? "Backend: bereit" : "Backend: wartet…";
}
// addieren von NAchrichten
function addNotification(message, level = "info") {
    const item = document.createElement("div");
    item.className = `notif ${level}`;
    const text = document.createElement("div");
    text.className = "notif-text";
    text.textContent = message;
    const del = document.createElement("button");
    del.className = "notif-delete";
    del.textContent = "x";
    del.addEventListener("click", (event) => {
        event.stopPropagation();
        item.remove();
    });
    item.appendChild(text);
    item.appendChild(del);
    notifList.prepend(item);
}
// wenn wichtig Nchricht dann Modal
function showModal(title, message) {
    modalTitle.textContent = title;
    modalBody.textContent = message;
    modal.classList.add("active");
}

modalClose.addEventListener("click", () => modal.classList.remove("active"));

externalBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    document.querySelectorAll('.external-dropdown').forEach(d=>d.classList.toggle('open'));
});

externalItems.forEach((it) => {
    it.addEventListener("click", (e) => {
        const key = it.dataset.key;
        if (!backendReady) {
            addNotification("Backend nicht bereit.", "warning");
            return;
        }
        backend.openWindow(key);
        document.querySelectorAll('.external-dropdown').forEach(d=>d.classList.remove('open'));
    });
});

// close dropdown on outside click
document.addEventListener('click', () => {
    document.querySelectorAll('.external-dropdown').forEach(d=>d.classList.remove('open'));
});

assignBtn.addEventListener("click", () => {
    if (!backendReady) {
        addNotification("Backend nicht bereit.", "warning");
        return;
    }
    backend.startAssignmentDemo();
});

uploadBtn.addEventListener("click", () => {
    if (!backendReady) {
        addNotification("Backend nicht bereit.", "warning");
        return;
    }
    backend.importFile();
});
// window controlls wieder
titlebar.addEventListener("mousedown", (event) => {
    if (!backendReady || event.button !== 0) {
        return;
    }
    if (event.target.closest(".window-btn")) {
        return;
    }
    backend.windowStartDrag();
});
// doppelklick fuer Fenster vollbild/kleinbild
titlebar.addEventListener("dblclick", () => {
    if (!backendReady) {
        return;
    }
    backend.windowToggleMaximize();
});

minBtn.addEventListener("click", () => {
    if (backendReady) {
        backend.windowMinimize();
    }
});

maxBtn.addEventListener("click", () => {
    if (backendReady) {
        backend.windowToggleMaximize();
    }
});

closeBtn.addEventListener("click", () => {
    if (backendReady) {
        backend.windowClose();
    }
});
/* Window Controls ende
Verhindern von strg a damit es nciht wie goofy webview ausseieht*/
document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "a") {
        event.preventDefault();
    }
});

// Verhindern von rechtsklick damit es nciht wie goofy webview ausseieht
document.addEventListener("contextmenu", (event) => {
    event.preventDefault();
});
// benutzen modal für zuteilung fertig (akt. demo knopf)
window.__notifyFromPython = function (message, level) {
    if (level === "modal") {
        showModal("Zuteilung abgeschlossen", message);
        addNotification(message, "success");
        return;
    }
    addNotification(message, level || "info");
};
// bestaetigung von qt kanal sehr gut

if (typeof qt !== "undefined") {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend = channel.objects.backend;
        if (backend) {
            setReady(true);
            addNotification("Backend verbunden.", "success");
            // no dropdown checkmarks needed
        } else {
            addNotification("Backend-Objekt nicht gefunden.", "error");
        }
    });
} else {
    addNotification("Qt WebChannel nicht verfügbar. Bitte über die App starten.", "error");
}