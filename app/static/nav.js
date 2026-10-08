/* Navigation partagée de Dofus Cockpit — injectée par toutes les pages via
 * <script src="/ui/nav.js" defer></script>.
 *
 * Fournit, sans toucher au layout des pages :
 *  1) une BARRE STICKY : sélecteur de page + "chips" de sections (panneaux) de
 *     la page courante, avec surlignage de la section active (scrollspy) ;
 *  2) un TIROIR latéral listant toutes les pages et, pour la page courante,
 *     ses sections (clic = saut direct) ;
 *  3) une PALETTE de commande (Ctrl/⌘ + K) pour sauter à n'importe quelle page
 *     ou section en tapant quelques lettres.
 *
 * Les sections sont découvertes automatiquement à partir des <section class="panel">
 * et de leur titre <h2> — rien à déclarer par page.
 */
(function () {
    if (window.__appnav) return;
    window.__appnav = true;

    const PAGES = [
        {file: "steps.html", label: "Démarrage", icon: "🚀"},
        {file: "index.html", label: "Persos & Stuff", icon: "🧙"},
        {file: "bank.html", label: "Banque", icon: "🏦"},
        {file: "build.html", label: "Suivi ressources", icon: "🛠️"},
        {file: "board.html", label: "Comptes", icon: "👥"},
        {file: "live.html", label: "Repop live", icon: "⏱️"},
        {file: "turn.html", label: "Qui joue", icon: "⚔️"},
        {file: "dungeon.html", label: "Donjons", icon: "🗝️"},
    ];

    const NAV_H = 46;           // hauteur de la barre sticky (px)
    const here = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    const curFile = PAGES.some(p => p.file === here) ? here : "index.html";
    const curPage = PAGES.find(p => p.file === curFile);

    const norm = s => (s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
    const slug = s => norm(s).replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "sec";

    // --- Découverte des sections (panneaux) de la page courante ----------------
    function sectionLabel(panel) {
        const h = panel.querySelector(":scope > h2, :scope > h3") || panel.querySelector("h2, h3");
        if (!h) return null;
        let txt = "";
        for (const n of h.childNodes) {               // 1er noeud texte = l'intitulé
            if (n.nodeType === 3 && n.textContent.trim()) {
                txt = n.textContent;
                break;
            }
        }
        if (!txt) txt = h.textContent;
        return txt.replace(/\s+/g, " ").split(/[—–]|:\s/)[0].trim();
    }

    function collectSections() {
        const out = [];
        document.querySelectorAll("section.panel, section.kpis").forEach((panel, i) => {
            let label = panel.classList.contains("kpis") ? "Résumé" : sectionLabel(panel);
            if (!label) return;
            if (!panel.id) panel.id = "sec-" + slug(label) + "-" + i;
            panel.style.scrollMarginTop = (NAV_H + 12) + "px";
            out.push({id: panel.id, label, el: panel});
        });
        return out;
    }

    const SECTIONS = collectSections();

    function jumpTo(id) {
        const el = document.getElementById(id);
        if (!el) return;
        const y = el.getBoundingClientRect().top + window.scrollY - NAV_H - 10;
        window.scrollTo({top: y, behavior: "smooth"});
        el.style.transition = "box-shadow .25s";
        el.style.boxShadow = "0 0 0 2px var(--accent, #2a78d6)";
        setTimeout(() => (el.style.boxShadow = ""), 900);
    }

    // --- Styles ----------------------------------------------------------------
    const css = `
  .an-bar{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:8px;
    height:${NAV_H}px;padding:0 10px;background:var(--surface,#fff);
    border-bottom:1px solid var(--border,rgba(0,0,0,.1));backdrop-filter:blur(6px)}
  .an-bar button{background:transparent;border:1px solid var(--border,rgba(0,0,0,.12));
    color:var(--ink2,#444);border-radius:8px;padding:5px 9px;cursor:pointer;font-size:13px;white-space:nowrap}
  .an-bar button:hover{border-color:var(--accent,#2a78d6);color:var(--accent,#2a78d6)}
  .an-here{font-weight:650;color:var(--ink,#111);display:flex;gap:6px;align-items:center;white-space:nowrap}
  .an-chips{display:flex;gap:6px;overflow-x:auto;flex:1;scrollbar-width:thin;padding:3px 2px}
  .an-chips::-webkit-scrollbar{height:6px}
  .an-chip{font-size:12.5px;color:var(--ink2,#555);border:1px solid var(--border,rgba(0,0,0,.12));
    background:var(--chip,#f0efec);border-radius:999px;padding:3px 10px;cursor:pointer;white-space:nowrap}
  .an-chip.active{background:var(--accent,#2a78d6);color:#fff;border-color:var(--accent,#2a78d6)}
  .an-k{font-variant-numeric:tabular-nums;opacity:.85}
  .an-sep{opacity:.4}
  /* overlay (tiroir + palette) */
  .an-ov{position:fixed;inset:0;z-index:60;background:rgba(0,0,0,.42);display:none}
  .an-ov.open{display:block}
  .an-drawer{position:fixed;top:0;left:0;bottom:0;width:290px;max-width:85vw;z-index:61;
    background:var(--plane,#f9f9f7);border-right:1px solid var(--border,rgba(0,0,0,.12));
    transform:translateX(-100%);transition:transform .18s ease;overflow-y:auto;padding:14px 12px}
  .an-drawer.open{transform:none}
  .an-drawer h4{margin:14px 8px 6px;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted,#888)}
  .an-link{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:9px;
    color:var(--ink,#111);text-decoration:none;font-size:14px;cursor:pointer}
  .an-link:hover{background:color-mix(in srgb,var(--accent,#2a78d6) 12%,transparent)}
  .an-link.cur{background:var(--accent-soft,#cde2fb);color:var(--ink,#111);font-weight:650}
  .an-sub{display:flex;gap:8px;padding:6px 10px 6px 30px;border-radius:8px;color:var(--ink2,#555);
    text-decoration:none;font-size:13px;cursor:pointer}
  .an-sub:hover{background:color-mix(in srgb,var(--accent,#2a78d6) 10%,transparent)}
  .an-brand{display:flex;align-items:center;gap:8px;font-weight:700;font-size:15px;color:var(--ink,#111);padding:4px 8px 10px}
  /* palette */
  .an-pal{position:fixed;top:12vh;left:50%;transform:translateX(-50%);z-index:62;width:560px;max-width:92vw;
    background:var(--surface,#fff);border:1px solid var(--border,rgba(0,0,0,.14));border-radius:14px;
    box-shadow:0 18px 60px rgba(0,0,0,.35);display:none;overflow:hidden}
  .an-pal.open{display:block}
  .an-pal input{width:100%;box-sizing:border-box;border:none;border-bottom:1px solid var(--grid,#e1e0d9);
    background:transparent;color:var(--ink,#111);font-size:16px;padding:14px 16px;outline:none;font-family:inherit}
  .an-res{max-height:52vh;overflow-y:auto;padding:6px}
  .an-item{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:9px;cursor:pointer;font-size:14px;color:var(--ink,#111)}
  .an-item .t{opacity:.55;font-size:11px;margin-left:auto;text-transform:uppercase;letter-spacing:.04em}
  .an-item.sel{background:var(--accent,#2a78d6);color:#fff}
  .an-item.sel .t{opacity:.85}
  .an-empty{padding:16px;color:var(--muted,#888);font-size:13px;text-align:center}
  @media(max-width:640px){.an-here span.lbl{display:none}}
  `;
    const style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);

    // --- Barre sticky ----------------------------------------------------------
    const bar = document.createElement("nav");
    bar.className = "an-bar";
    bar.innerHTML =
        `<button class="an-menu" title="Toutes les pages (menu)">☰</button>` +
        `<span class="an-here">${curPage.icon}<span class="lbl">${curPage.label}</span></span>` +
        `<span class="an-sep">›</span>` +
        `<div class="an-chips"></div>` +
        `<button class="an-cmd" title="Recherche rapide">🔎 <span class="an-k">Ctrl K</span></button>`;
    (document.body).insertBefore(bar, document.body.firstChild);

    const chipsBox = bar.querySelector(".an-chips");
    const chipById = {};
    SECTIONS.forEach(s => {
        const c = document.createElement("button");
        c.className = "an-chip";
        c.textContent = s.label;
        c.onclick = () => jumpTo(s.id);
        chipsBox.appendChild(c);
        chipById[s.id] = c;
    });
    if (!SECTIONS.length) chipsBox.innerHTML = `<span class="an-sep" style="font-size:12px">Pas de sections</span>`;

    // scrollspy : surligne la section active
    let spyRAF = 0;

    function spy() {
        spyRAF = 0;
        let activeId = SECTIONS.length ? SECTIONS[0].id : null;
        for (const s of SECTIONS) {
            if (s.el.getBoundingClientRect().top <= NAV_H + 24) activeId = s.id;
        }
        for (const id in chipById) chipById[id].classList.toggle("active", id === activeId);
        const act = activeId && chipById[activeId];
        if (act) act.scrollIntoView({block: "nearest", inline: "nearest"});
    }

    if (SECTIONS.length) {
        addEventListener("scroll", () => {
            if (!spyRAF) spyRAF = requestAnimationFrame(spy);
        }, {passive: true});
        spy();
    }

    // --- Overlay partagé (tiroir + palette) ------------------------------------
    const ov = document.createElement("div");
    ov.className = "an-ov";
    document.body.appendChild(ov);

    // Tiroir
    const drawer = document.createElement("aside");
    drawer.className = "an-drawer";
    let dh = `<div class="an-brand">🎛️ Dofus Cockpit</div><h4>Pages</h4>`;
    for (const p of PAGES) {
        dh += `<a class="an-link ${p.file === curFile ? "cur" : ""}" href="${p.file}">${p.icon}<span>${p.label}</span></a>`;
    }
    if (SECTIONS.length) {
        dh += `<h4>Sections de « ${curPage.label} »</h4>`;
        for (const s of SECTIONS) dh += `<a class="an-sub" data-sec="${s.id}">▸ ${s.label}</a>`;
    }
    drawer.innerHTML = dh;
    document.body.appendChild(drawer);
    drawer.querySelectorAll(".an-sub").forEach(a =>
        a.onclick = () => {
            closeOverlay();
            jumpTo(a.getAttribute("data-sec"));
        });

    function openDrawer() {
        ov.classList.add("open");
        drawer.classList.add("open");
    }

    function closeOverlay() {
        ov.classList.remove("open");
        drawer.classList.remove("open");
        pal.classList.remove("open");
    }

    ov.onclick = closeOverlay;
    bar.querySelector(".an-menu").onclick = openDrawer;

    // --- Palette de commande ---------------------------------------------------
    const INDEX = [
        ...PAGES.filter(p => p.file !== curFile).map(p => ({
            kind: "Page",
            label: p.label,
            icon: p.icon,
            go: () => (location.href = p.file)
        })),
        ...SECTIONS.map(s => ({kind: "Section", label: s.label, icon: "▸", go: () => jumpTo(s.id)})),
    ];
    const pal = document.createElement("div");
    pal.className = "an-pal";
    pal.innerHTML = `<input type="text" placeholder="Aller à une page ou une section…" autocomplete="off"><div class="an-res"></div>`;
    document.body.appendChild(pal);
    const palInput = pal.querySelector("input");
    const palRes = pal.querySelector(".an-res");
    let filtered = [], sel = 0;

    function renderPal() {
        const q = norm(palInput.value.trim());
        filtered = q ? INDEX.filter(x => norm(x.label).includes(q) || norm(x.kind).includes(q)) : INDEX;
        sel = 0;
        palRes.innerHTML = filtered.length
            ? filtered.map((x, i) => `<div class="an-item ${i === 0 ? "sel" : ""}" data-i="${i}"><span>${x.icon}</span><span>${x.label}</span><span class="t">${x.kind}</span></div>`).join("")
            : `<div class="an-empty">Aucun résultat</div>`;
        palRes.querySelectorAll(".an-item").forEach(el => {
            el.onclick = () => choose(+el.dataset.i);
            el.onmousemove = () => setSel(+el.dataset.i);
        });
    }

    function setSel(i) {
        sel = i;
        palRes.querySelectorAll(".an-item").forEach((el, k) => el.classList.toggle("sel", k === i));
        const cur = palRes.querySelector(".an-item.sel");
        if (cur) cur.scrollIntoView({block: "nearest"});
    }

    function choose(i) {
        const x = filtered[i];
        if (x) {
            closeOverlay();
            x.go();
        }
    }

    function openPal() {
        ov.classList.add("open");
        pal.classList.add("open");
        palInput.value = "";
        renderPal();
        palInput.focus();
    }

    bar.querySelector(".an-cmd").onclick = openPal;
    palInput.addEventListener("input", renderPal);
    palInput.addEventListener("keydown", e => {
        if (e.key === "ArrowDown") {
            e.preventDefault();
            setSel(Math.min(sel + 1, filtered.length - 1));
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setSel(Math.max(sel - 1, 0));
        } else if (e.key === "Enter") {
            e.preventDefault();
            choose(sel);
        } else if (e.key === "Escape") {
            closeOverlay();
        }
    });

    // Raccourcis globaux : Ctrl/⌘+K = palette, Échap = fermer.
    addEventListener("keydown", e => {
        if ((e.ctrlKey || e.metaKey) && (e.key === "k" || e.key === "K")) {
            e.preventDefault();
            openPal();
        } else if (e.key === "Escape") {
            closeOverlay();
        }
    });
})();
