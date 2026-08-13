import { initializeApp } from "https://www.gstatic.com/firebasejs/12.17.1/firebase-app.js";
import {
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from "https://www.gstatic.com/firebasejs/12.17.1/firebase-auth.js";

const signedOutEl = document.getElementById("signed-out");
const signedInEl = document.getElementById("signed-in");
const bootErrorEl = document.getElementById("boot-error");
const authErrorEl = document.getElementById("auth-error");
const userLineEl = document.getElementById("user-line");
const holdingMsgEl = document.getElementById("holding-msg");
const holdingErrorEl = document.getElementById("holding-error");
const analyzeErrorEl = document.getElementById("analyze-error");
const noteEl = document.getElementById("note");
const noteTitleEl = document.getElementById("note-title");
const noteSummaryEl = document.getElementById("note-summary");
const noteRatingEl = document.getElementById("note-rating");
const noteCitationsEl = document.getElementById("note-citations");
const noteDisclaimerEl = document.getElementById("note-disclaimer");

const signinBtn = document.getElementById("signin");
const signoutBtn = document.getElementById("signout");
const holdingForm = document.getElementById("holding-form");
const analyzeForm = document.getElementById("analyze-form");

let auth = null;

function show(el, on) {
  el.classList.toggle("hidden", !on);
}

function setText(el, text, isError) {
  el.textContent = text || "";
  show(el, Boolean(text));
  if (isError !== undefined) {
    el.classList.toggle("error", isError);
    el.classList.toggle("ok", !isError);
  }
}

async function api(path, options = {}) {
  const user = auth && auth.currentUser;
  if (!user) {
    throw new Error("not signed in");
  }
  const token = await user.getIdToken();
  const headers = {
    Authorization: `Bearer ${token}`,
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers || {}),
  };
  const response = await fetch(path, { ...options, headers });
  const text = await response.text();
  let body = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  if (!response.ok) {
    const detail = body && body.detail ? JSON.stringify(body.detail) : text;
    throw new Error(`${response.status} ${path}: ${detail || response.statusText}`);
  }
  return body;
}

function renderNote(note) {
  noteTitleEl.textContent = `Cited note — ${note.ticker}`;
  noteSummaryEl.textContent = note.summary || "";
  noteRatingEl.textContent = note.rating ? `Rating: ${note.rating}` : "";
  noteCitationsEl.replaceChildren();
  for (const citation of note.citations || []) {
    const row = document.createElement("tr");
    for (const value of [citation.source, citation.as_of, citation.detail]) {
      const cell = document.createElement("td");
      cell.textContent = value || "";
      row.appendChild(cell);
    }
    noteCitationsEl.appendChild(row);
  }
  noteDisclaimerEl.textContent = note.disclaimer || "";
  show(noteEl, true);
}

async function showSignedIn() {
  show(signedOutEl, false);
  show(signedInEl, true);
  setText(authErrorEl, "");
  const me = await api("/me");
  const email = me.email || "(no email)";
  userLineEl.textContent = `${email} · ${me.user_id}`;
}

function showSignedOut() {
  show(signedInEl, false);
  show(signedOutEl, true);
  userLineEl.textContent = "";
  show(noteEl, false);
}

async function boot() {
  const response = await fetch("/config");
  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      `GET /config failed (${response.status}). Set PCOPILOT_FIREBASE_API_KEY, ` +
        `PCOPILOT_FIREBASE_AUTH_DOMAIN, PCOPILOT_FIREBASE_PROJECT_ID. ${body}`,
    );
  }
  const cfg = await response.json();
  const app = initializeApp({
    apiKey: cfg.apiKey,
    authDomain: cfg.authDomain,
    projectId: cfg.projectId,
  });
  auth = getAuth(app);

  onAuthStateChanged(auth, async (user) => {
    try {
      if (user) {
        await showSignedIn();
      } else {
        showSignedOut();
      }
    } catch (err) {
      setText(authErrorEl, String(err.message || err));
      showSignedOut();
    }
  });

  signinBtn.addEventListener("click", async () => {
    setText(authErrorEl, "");
    try {
      await signInWithPopup(auth, new GoogleAuthProvider());
    } catch (err) {
      const code = err && err.code ? `${err.code}: ` : "";
      setText(authErrorEl, `${code}${err.message || err}`);
    }
  });

  signoutBtn.addEventListener("click", async () => {
    await signOut(auth);
  });

  holdingForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setText(holdingMsgEl, "");
    setText(holdingErrorEl, "");
    const data = new FormData(holdingForm);
    try {
      const portfolio = await api("/portfolios", {
        method: "POST",
        body: JSON.stringify({
          type: data.get("type"),
          market: data.get("market"),
          cash: Number(data.get("cash") || 0),
        }),
      });
      const position = await api(`/portfolios/${portfolio.id}/positions`, {
        method: "POST",
        body: JSON.stringify({
          ticker: String(data.get("ticker") || "").trim().toUpperCase(),
          quantity: Number(data.get("quantity")),
          cost_basis: Number(data.get("cost_basis")),
          acquired: data.get("acquired"),
        }),
      });
      setText(
        holdingMsgEl,
        `Saved ${position.ticker} in ${portfolio.id} (${portfolio.type}, ${portfolio.market}).`,
        false,
      );
    } catch (err) {
      setText(holdingErrorEl, String(err.message || err));
    }
  });

  analyzeForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setText(analyzeErrorEl, "");
    show(noteEl, false);
    const ticker = document.getElementById("analyze-ticker").value.trim().toUpperCase();
    try {
      const note = await api("/analyze", {
        method: "POST",
        body: JSON.stringify({ ticker }),
      });
      renderNote(note);
    } catch (err) {
      setText(analyzeErrorEl, String(err.message || err));
    }
  });
}

boot().catch((err) => {
  setText(bootErrorEl, String(err.message || err));
});
