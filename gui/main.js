/* ============================================================
   MPG SPORTIFY v2.1 – Interactive JavaScript
   Particle effects, splash animation, ripples, settings,
   light mode, sound, and all original backend functionality.
   ============================================================ */

/* ---------- BACKEND / STATE ---------- */
let backend = null;
let backendReady = false;
let notifCount = 0;
let particlesRunning = true;
let particleAnimFrame = null;

/* ---------- SETTINGS STATE ---------- */
const settings = {
    lightMode: false,
    animations: true,
    sounds: true,
    particles: true,
};

// Load saved settings from localStorage
(function loadSettings() {
    try {
        const saved = localStorage.getItem('sportify_settings');
        if (saved) {
            const parsed = JSON.parse(saved);
            Object.assign(settings, parsed);
        }
    } catch (e) { /* ignore */ }
})();

function saveSettings() {
    try {
        localStorage.setItem('sportify_settings', JSON.stringify(settings));
    } catch (e) { /* ignore */ }
}

/* ---------- DOM REFERENCES ---------- */
const statusChip    = document.getElementById("statusChip");
const assignBtn     = document.getElementById("assignBtn");
const uploadBtn     = document.getElementById("uploadBtn");
const notifList     = document.getElementById("notifList");
const notifCounter  = document.getElementById("notifCounter");
const notifEmpty    = document.getElementById("notifEmpty");
const modal         = document.getElementById("modal");
const modalTitle    = document.getElementById("modalTitle");
const modalBody     = document.getElementById("modalBody");
const modalClose    = document.getElementById("modalClose");
const titlebar      = document.getElementById("titlebar");
const minBtn        = document.getElementById("minBtn");
const closeBtn      = document.getElementById("closeBtn");
const externalBtn   = document.getElementById("externalBtn");
const externalMenu  = document.getElementById("externalMenu");
const externalDropdown = document.getElementById("externalDropdown");
const externalItems = document.querySelectorAll(".external-item");
const splash        = document.getElementById("splash");
const splashBar     = document.getElementById("splashBar");
const splashStatus  = document.getElementById("splashStatus");
const app           = document.getElementById("app");
const navBar        = document.getElementById("navBar");
const navIndicator  = document.getElementById("navIndicator");
const jingleSound   = document.getElementById("jingleSound");

/* Settings panel elements */
const settingsBtn    = document.getElementById("settingsBtn");
const settingsPanel  = document.getElementById("settingsPanel");
const toggleTheme    = document.getElementById("toggleTheme");
const toggleAnimations = document.getElementById("toggleAnimations");
const toggleSounds   = document.getElementById("toggleSounds");
const toggleParticles = document.getElementById("toggleParticles");

/* ============================================================
   APPLY SAVED SETTINGS ON LOAD
   ============================================================ */
(function applyInitialSettings() {
    if (settings.lightMode) {
        document.documentElement.classList.add('light');
        toggleTheme.classList.add('active');
    }
    if (!settings.animations) {
        document.documentElement.classList.add('no-animations');
        toggleAnimations.classList.remove('active');
    }
    if (!settings.particles) {
        document.documentElement.classList.add('no-particles');
        toggleParticles.classList.remove('active');
    }
    if (!settings.sounds) {
        toggleSounds.classList.remove('active');
    }
})();

/* ============================================================
   SETTINGS PANEL
   ============================================================ */
settingsBtn.addEventListener("click", function(e) {
    e.stopPropagation();
    const isOpen = settingsPanel.classList.contains("open");
    // Close other dropdowns
    externalDropdown.classList.remove("open");

    if (isOpen) {
        settingsPanel.classList.remove("open");
        settingsBtn.classList.remove("active");
    } else {
        settingsPanel.classList.add("open");
        settingsBtn.classList.add("active");
    }
});

// Prevent settings panel clicks from closing it
settingsPanel.addEventListener("click", function(e) {
    e.stopPropagation();
});

/* --- Toggle: Light Mode --- */
toggleTheme.addEventListener("click", function() {
    settings.lightMode = !settings.lightMode;
    toggleTheme.classList.toggle("active", settings.lightMode);
    document.documentElement.classList.toggle("light", settings.lightMode);
    saveSettings();
});

/* --- Toggle: Animations --- */
toggleAnimations.addEventListener("click", function() {
    settings.animations = !settings.animations;
    toggleAnimations.classList.toggle("active", settings.animations);
    document.documentElement.classList.toggle("no-animations", !settings.animations);
    saveSettings();
});

/* --- Toggle: Sounds --- */
toggleSounds.addEventListener("click", function() {
    settings.sounds = !settings.sounds;
    toggleSounds.classList.toggle("active", settings.sounds);
    saveSettings();
});

/* --- Toggle: Particles --- */
toggleParticles.addEventListener("click", function() {
    settings.particles = !settings.particles;
    toggleParticles.classList.toggle("active", settings.particles);
    document.documentElement.classList.toggle("no-particles", !settings.particles);
    saveSettings();
});

/* ============================================================
   SPLASH SCREEN
   ============================================================ */
(function initSplash() {
    // If animations disabled, skip splash entirely
    if (!settings.animations) {
        if (splash) splash.style.display = 'none';
        app.classList.add("visible");
        setTimeout(function() {
            if (settings.particles) initParticleBackground();
            updateNavIndicator();
            triggerLogoPulse();
        }, 50);
        return;
    }

    const canvas = document.getElementById("splashCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let w, h;
    const particles = [];
    const PARTICLE_COUNT = 60;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    // Create particles
    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
            x: Math.random() * w,
            y: Math.random() * h,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            r: Math.random() * 2 + 0.5,
            alpha: Math.random() * 0.3 + 0.1,
        });
    }

    let running = true;

    function draw() {
        if (!running) return;
        ctx.clearRect(0, 0, w, h);

        // Draw connecting lines
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 229, 255, ${0.06 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }

        // Draw particles
        particles.forEach((p) => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0 || p.x > w) p.vx *= -1;
            if (p.y < 0 || p.y > h) p.vy *= -1;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 229, 255, ${p.alpha})`;
            ctx.fill();
        });

        requestAnimationFrame(draw);
    }
    draw();

    // Animate splash progress
    const stages = [
        { pct: 20, text: "Lade Module...", delay: 400 },
        { pct: 45, text: "Initialisiere UI...", delay: 600 },
        { pct: 70, text: "Verbinde Backend...", delay: 500 },
        { pct: 90, text: "Fast fertig...", delay: 400 },
        { pct: 100, text: "Bereit!", delay: 300 },
    ];

    let currentStage = 0;

    function advanceSplash() {
        if (currentStage >= stages.length) {
            // Finished – transition out
            setTimeout(() => {
                splash.classList.add("fade-out");
                app.classList.add("visible");
                setTimeout(() => {
                    splash.classList.add("hidden");
                    running = false;
                    if (settings.particles) initParticleBackground();
                    updateNavIndicator();
                    triggerLogoPulse();
                }, 700);
            }, 300);
            return;
        }

        const stage = stages[currentStage];
        splashBar.style.width = stage.pct + "%";
        splashStatus.textContent = stage.text;
        currentStage++;
        setTimeout(advanceSplash, stage.delay);
    }

    setTimeout(advanceSplash, 600);
})();

/* ============================================================
   LOGO INTRO PULSE (3 times then stop)
   ============================================================ */
function triggerLogoPulse() {
    var pulse = document.querySelector(".logo-pulse");
    if (!pulse || !settings.animations) return;
    pulse.classList.add("intro-pulse");
    pulse.addEventListener("animationend", function handler() {
        pulse.classList.remove("intro-pulse");
        pulse.removeEventListener("animationend", handler);
    });
}

/* ============================================================
   PARTICLE BACKGROUND (Main App)
   ============================================================ */
function initParticleBackground() {
    const canvas = document.getElementById("particleCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let w, h;
    const particles = [];
    const PARTICLE_COUNT = 40;

    function resize() {
        w = canvas.width = canvas.parentElement.offsetWidth;
        h = canvas.height = canvas.parentElement.offsetHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
            x: Math.random() * (w || 800),
            y: Math.random() * (h || 600),
            vx: (Math.random() - 0.5) * 0.25,
            vy: (Math.random() - 0.5) * 0.25,
            r: Math.random() * 1.5 + 0.5,
            alpha: Math.random() * 0.15 + 0.05,
        });
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);

        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 229, 255, ${0.03 * (1 - dist / 150)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }

        particles.forEach((p) => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0 || p.x > w) p.vx *= -1;
            if (p.y < 0 || p.y > h) p.vy *= -1;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 229, 255, ${p.alpha})`;
            ctx.fill();
        });

        requestAnimationFrame(draw);
    }
    draw();
}

/* ============================================================
   NAV INDICATOR (pill that slides behind active tab)
   ============================================================ */
function updateNavIndicator() {
    const activeBtn = navBar.querySelector(".nav-btn.active");
    if (!activeBtn || !navIndicator) return;
    const navRect = navBar.getBoundingClientRect();
    const btnRect = activeBtn.getBoundingClientRect();
    navIndicator.style.width = btnRect.width + "px";
    navIndicator.style.left = (btnRect.left - navRect.left) + "px";
    navIndicator.style.top = (btnRect.top - navRect.top) + "px";
}

navBar.querySelectorAll(".nav-btn:not(.dropdown-trigger)").forEach((btn) => {
    btn.addEventListener("click", () => {
        navBar.querySelectorAll(".nav-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        updateNavIndicator();
    });
});

window.addEventListener("resize", () => {
    requestAnimationFrame(updateNavIndicator);
});

/* ============================================================
   RIPPLE EFFECT on Buttons
   ============================================================ */
document.querySelectorAll(".btn").forEach((btn) => {
    btn.addEventListener("click", function (e) {
        if (btn.disabled) return;
        const rippleContainer = btn.querySelector(".btn-ripple");
        if (!rippleContainer) return;

        const circle = document.createElement("span");
        circle.className = "ripple-circle";

        const rect = btn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 2;
        circle.style.width = circle.style.height = size + "px";
        circle.style.left = (e.clientX - rect.left - size / 2) + "px";
        circle.style.top = (e.clientY - rect.top - size / 2) + "px";

        rippleContainer.appendChild(circle);
        circle.addEventListener("animationend", () => circle.remove());
    });
});

/* ============================================================
   BACKEND CONNECTIVITY (preserved from original)
   ============================================================ */
function setReady(ready) {
    backendReady = ready;
    assignBtn.disabled = !ready;
    uploadBtn.disabled = !ready;

    const chip = statusChip;
    const textEl = chip.querySelector(".status-text");

    if (ready) {
        chip.classList.add("ready");
        textEl.textContent = "Backend: bereit";
    } else {
        chip.classList.remove("ready");
        textEl.textContent = "Backend: wartet...";
    }
}

/* ---------- Notifications ---------- */
function addNotification(message, level) {
    level = level || "info";

    // Remove empty state
    if (notifEmpty) notifEmpty.style.display = "none";

    const item = document.createElement("div");
    item.className = "notif " + level;

    const text = document.createElement("div");
    text.className = "notif-text";
    text.textContent = message;

    const del = document.createElement("button");
    del.className = "notif-delete";
    del.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12"><path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
    del.addEventListener("click", function (event) {
        event.stopPropagation();
        item.classList.add("removing");
        item.addEventListener("animationend", function () {
            item.remove();
            notifCount = Math.max(0, notifCount - 1);
            updateNotifCounter();
            if (notifList.children.length === 0 || (notifList.children.length === 1 && notifList.contains(notifEmpty))) {
                if (notifEmpty) notifEmpty.style.display = "";
            }
        });
    });

    item.appendChild(text);
    item.appendChild(del);
    notifList.prepend(item);

    notifCount++;
    updateNotifCounter();
}

function updateNotifCounter() {
    if (!notifCounter) return;
    notifCounter.textContent = notifCount;
    notifCounter.classList.remove("pop");
    void notifCounter.offsetWidth; // force reflow
    notifCounter.classList.add("pop");
}

/* ---------- Modal ---------- */
function showModal(title, message) {
    modalTitle.textContent = title;
    modalBody.textContent = message;
    modal.classList.add("active");

    // Play jingle sound if sounds are enabled
    if (settings.sounds && jingleSound) {
        jingleSound.currentTime = 0;
        jingleSound.play().catch(function() { /* autoplay may be blocked */ });
    }
}

modalClose.addEventListener("click", function () {
    modal.classList.remove("active");
});

// Close modal on overlay click
modal.addEventListener("click", function (e) {
    if (e.target === modal) {
        modal.classList.remove("active");
    }
});

/* ---------- External Dropdown ---------- */
externalBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    // Close settings when opening external dropdown
    settingsPanel.classList.remove("open");
    settingsBtn.classList.remove("active");
    externalDropdown.classList.toggle("open");
});

externalItems.forEach(function (it) {
    it.addEventListener("click", function () {
        var key = it.dataset.key;
        if (!backendReady) {
            addNotification("Backend nicht bereit.", "warning");
            return;
        }
        backend.openWindow(key);
        externalDropdown.classList.remove("open");
    });
});

// Close dropdown and settings on outside click
document.addEventListener("click", function () {
    externalDropdown.classList.remove("open");
    settingsPanel.classList.remove("open");
    settingsBtn.classList.remove("active");
});

/* ---------- Action Buttons ---------- */
assignBtn.addEventListener("click", function () {
    if (!backendReady) {
        addNotification("Backend nicht bereit.", "warning");
        return;
    }
    backend.startAssignmentDemo();
});

uploadBtn.addEventListener("click", function () {
    if (!backendReady) {
        addNotification("Backend nicht bereit.", "warning");
        return;
    }
    backend.importFile();
});

/* ---------- Window Controls ---------- */
titlebar.addEventListener("mousedown", function (event) {
    if (!backendReady || event.button !== 0) return;
    if (event.target.closest(".window-btn")) return;
    backend.windowStartDrag();
});

minBtn.addEventListener("click", function () {
    if (backendReady) backend.windowMinimize();
});

closeBtn.addEventListener("click", function () {
    if (backendReady) backend.windowClose();
});

/* ---------- Prevent Ctrl+A and Right Click ---------- */
document.addEventListener("keydown", function (event) {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "a") {
        event.preventDefault();
    }
});

document.addEventListener("contextmenu", function (event) {
    event.preventDefault();
});

/* ---------- Python callback ---------- */
window.__notifyFromPython = function (message, level) {
    if (level === "modal") {
        showModal("Zuteilung abgeschlossen", message);
        addNotification(message, "success");
        return;
    }
    addNotification(message, level || "info");
};

/* ---------- Qt WebChannel ---------- */
if (typeof qt !== "undefined") {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend = channel.objects.backend;
        if (backend) {
            setReady(true);
            addNotification("Backend verbunden.", "success");
        } else {
            addNotification("Backend-Objekt nicht gefunden.", "error");
        }
    });
} else {
    addNotification("Qt WebChannel nicht verfuegbar. Bitte ueber die App starten.", "error");
}
