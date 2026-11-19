// VHDLBits edge Worker: serves the static site and guards the cloud grader.
//   POST /api/check/<id>  {"files": {...}, "turnstile": "<token>"}
// Checks the Turnstile token, then forwards {"files"} to Cloud Run with the shared key and
// the visitor's address (the grader rate-limits on it). Everything else is a static asset.
// A passed Turnstile check earns a signed session cookie; while it is valid no token is needed.
// Without either, the answer is 403 {"verify": true} and the page gets a token and retries.
// Secrets (wrangler secret put): GRADER_KEY, GRADER_URL, SESSION_KEY, TURNSTILE_SECRET.

const MAX_BODY = 256 * 1024;
const SESSION_SECONDS = 12 * 3600;
const enc = new TextEncoder();

function sessionKey(env) {
  return crypto.subtle.importKey("raw", enc.encode(env.SESSION_KEY), { name: "HMAC", hash: "SHA-256" },
                                 false, ["sign", "verify"]);
}

// vb_session=<expiry>.<HMAC of expiry>
async function sessionOk(request, env) {
  const m = (request.headers.get("Cookie") || "").match(/(?:^|;\s*)vb_session=(\d+)\.([0-9a-f]{64})/);
  if (!m || Number(m[1]) < Date.now() / 1000) return false;
  const sig = new Uint8Array(m[2].match(/../g).map((h) => parseInt(h, 16)));
  return crypto.subtle.verify("HMAC", await sessionKey(env), sig, enc.encode(m[1]));
}

async function sessionCookie(env) {
  const exp = String(Math.floor(Date.now() / 1000) + SESSION_SECONDS);
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", await sessionKey(env), enc.encode(exp)));
  const hex = [...sig].map((b) => b.toString(16).padStart(2, "0")).join("");
  return `vb_session=${exp}.${hex}; Max-Age=${SESSION_SECONDS}; Path=/api/; Secure; HttpOnly; SameSite=Strict`;
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status, headers: { "Content-Type": "application/json" },
  });
}

async function turnstileOk(token, ip, secret) {
  if (!token) return false;
  const form = new FormData();
  form.append("secret", secret);
  form.append("response", token);
  form.append("remoteip", ip);
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify",
                        { method: "POST", body: form });
  return (await r.json()).success === true;
}

async function check(request, env, id) {
  if (Number(request.headers.get("Content-Length") || 0) > MAX_BODY)
    return json({ error: "submission too large" }, 413);
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "bad request" }, 400);
  }
  const ip = request.headers.get("CF-Connecting-IP") || "";
  const fresh = !(await sessionOk(request, env));
  if (fresh && !body.turnstile) return json({ error: "Verification required.", verify: true }, 403);
  if (fresh && !(await turnstileOk(body.turnstile, ip, env.TURNSTILE_SECRET)))
    return json({ error: "Verification failed. Reload the page and try again." }, 403);
  const headers = { "Content-Type": "application/json" };
  if (fresh) headers["Set-Cookie"] = await sessionCookie(env);
  const r = await fetch(`${env.GRADER_URL}/check/${encodeURIComponent(id)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Grader-Key": env.GRADER_KEY, "X-Client-IP": ip },
    body: JSON.stringify({ files: body.files }),
  });
  if (r.status === 404 && !(r.headers.get("Content-Type") || "").includes("json"))
    return json({ error: "The grader is offline right now." }, 503);
  return new Response(r.body, { status: r.status, headers });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/api\/check\/([\w.-]+)$/);
    if (m && request.method === "POST") return check(request, env, m[1]);
    if (url.pathname.startsWith("/api/")) return json({ error: "not found" }, 404);
    return env.ASSETS.fetch(request);
  },
};
