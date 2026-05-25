---
name: webapp
description: Use when building a web application — landing pages, MVPs, dashboards, internal tools, lead magnets, single-page apps, or full-stack web products. Triggers on "build me a webapp", "landing page", "ship a website", "MVP", "dashboard", "internal tool", "Next.js", "Vite", "Bun", "Tailwind", "single-page app", "lead magnet site".
---

# Web app builder

You are operating as a web app engineer. Default to **ship fast, iterate live**. Choose the smallest stack that meets the requirement.

## Stack decision (in order, pick first that fits)

| If the requirement is… | Use | Why |
|---|---|---|
| 1-page brochure, form capture, no SSR needed | **Single-file HTML + Tailwind CDN** | Ship in 10 min, deploy via `python3 -m http.server` or Vercel static |
| SPA with state, routing, multi-page | **Vite + React + TypeScript + Tailwind** | Fast HMR, zero config, no SSR overhead |
| SEO/SSR/RSC/auth/db needed | **Next.js 15 (app router) + Tailwind + shadcn/ui** | Industry default for production web apps |
| Internal tool with auth + DB out of the box | **Next.js + Supabase** | You have supabase cloned; auth + Postgres free tier |
| Real-time multiplayer, low latency | **Next.js + Supabase Realtime** or **Bun + WebSockets** | Both have first-class real-time |

Bun is preferred over Node for the runtime. Tailwind is the default style system. shadcn/ui is the default component library for Next.js/React.

## Project init — copy and run

### 1-pager (no build step)
```bash
mkdir mylanding && cd mylanding
cat > index.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Your Headline · Your Brand</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap" rel="stylesheet">
  <style>body{font-family:'Inter',system-ui,sans-serif}</style>
</head>
<body class="bg-zinc-950 text-zinc-100">
  <!-- hero / value / cta / proof goes here -->
</body>
</html>
HTML
python3 -m http.server 8000
```

### Vite + React + TS (SPA)
```bash
bun create vite@latest myapp -- --template react-ts
cd myapp
bun add -D tailwindcss postcss autoprefixer
bunx tailwindcss init -p
bun add lucide-react clsx
# add Tailwind directives to src/index.css, configure tailwind.config.js content paths
bun run dev   # → http://localhost:5173
```

### Next.js 15 (app router) with shadcn/ui
```bash
bunx create-next-app@latest myapp --typescript --tailwind --app --import-alias "@/*"
cd myapp
bunx shadcn@latest init -d
bunx shadcn@latest add button card input form table dialog
bun run dev   # → http://localhost:3000
```

## Deploy (pick by stack)

| Stack | Deploy path | Time |
|---|---|---|
| Single HTML | Drag-drop to Vercel / Netlify / Cloudflare Pages | 60 sec |
| Vite SPA | `vercel` CLI or `wrangler pages deploy dist` | 2 min |
| Next.js | `vercel` (zero-config) | 3 min |
| Self-hosted | **Coolify** on a $5 Hetzner VPS (you have coolify cloned) | 30 min one-time setup, then push-to-deploy |

## Design defaults (so it doesn't look generic)

- **Color**: pick 1 primary + 1 accent + a neutral scale. Don't use Tailwind's default `blue-500` — looks like every CRUD app. Pull from your brand: orange `#ff7a18`, concrete `#f4f7ff`, ink `#0a0604`.
- **Type**: Inter (200, 400, 600, 800) for body; Teko for display/numbers. Load via Google Fonts `<link>` with `display=swap`.
- **Spacing rhythm**: stick to Tailwind's 4/8/12/16/24/48 ladder. Mixing arbitrary values (`mt-7`, `gap-13`) makes layouts feel off.
- **Border radius**: `rounded-lg` (8px) for cards, `rounded-2xl` for hero/modal. Avoid `rounded-full` on buttons unless it's a pill CTA.
- **Shadow**: `shadow-lg shadow-black/30` on cards. Default Tailwind shadows look weak.
- **Mobile-first**: write base styles for mobile, add `md:`/`lg:` overrides. Build at 375px width and scale up.
- **One CTA above the fold**. Repeated CTAs in the same color = decision fatigue.

## Form capture (lead magnets / waitlist)

Cheapest pattern: HTML form → Formspree/Basin/Resend → email or Slack.

```html
<form action="https://formspree.io/f/YOUR_ID" method="POST"
      class="flex gap-2 max-w-md mx-auto">
  <input type="email" name="email" required placeholder="you@domain.com"
         class="flex-1 rounded-lg bg-zinc-900 border border-zinc-700 px-4 py-3 text-white focus:border-orange-500 outline-none">
  <button class="rounded-lg bg-orange-500 hover:bg-orange-400 px-6 py-3 font-bold text-zinc-950 transition">
    Get it →
  </button>
</form>
```

For self-hosted lead capture, hit Supabase directly from the browser:
```js
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
const sb = createClient("https://YOUR.supabase.co", "YOUR_ANON_KEY")
await sb.from("leads").insert({ email, source: "landing-v1", referrer: document.referrer })
```

## Auth (Next.js)

Default to Supabase Auth (email magic links + OAuth). Skip building auth from scratch — burn budget.

```ts
// app/login/page.tsx
"use client"
import { createBrowserClient } from "@supabase/ssr"
const sb = createBrowserClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)
await sb.auth.signInWithOtp({ email })
```

## Performance defaults

- **Images**: use `next/image` (Next.js) or `<img loading="lazy" decoding="async">` everywhere else. Serve `.webp`/`.avif`.
- **Fonts**: `font-display: swap` always. Preconnect to googleapis & gstatic.
- **JS**: dynamic-import heavy components. `<Script strategy="lazyOnload">` for analytics.
- **CSS**: PurgeCSS is on by default with Tailwind in production — don't import full Tailwind in static HTML for prod (use CDN only for prototypes).

## Testing (when the user actually wants it)

- Unit: `vitest`
- E2E: `playwright` (also for visual regression)
- Component: `@testing-library/react`

For "ship fast" mode, skip tests. Add them when you have ≥1 paying user or the codebase is past ~500 LoC.

## Gotchas

- **Tailwind CDN ≠ Tailwind in production**. CDN is fine for prototypes but doesn't tree-shake; use the build pipeline for shipped sites.
- **shadcn/ui isn't a package** — it's source code copied into your project via the CLI. You own and can edit every component. Don't try to `bun add shadcn`.
- **Next.js app router server components can't use `useState`/`useEffect`** — add `"use client"` at top of files that need interactivity.
- **Hydration errors** in Next.js usually mean server-rendered HTML ≠ client-rendered HTML. Common cause: `Date.now()`, `Math.random()`, or `localStorage` reads outside `useEffect`.
- **Vite dev server is HTTP**; some APIs (camera, clipboard) require HTTPS — use `localhost` (whitelisted) or `mkcert` for LAN testing.
- **`process.env.NEXT_PUBLIC_*`** vars are baked at build time. If you change them, rebuild.

## Anti-patterns

- ❌ Building a CRUD admin panel from scratch when **Retool / Appsmith / Refine** would ship it in an hour.
- ❌ Spinning up a Node backend just to proxy one API call → use Next.js API routes or Cloudflare Workers.
- ❌ Webpack from scratch in 2026 → always Vite or Next.
- ❌ jQuery in new code → Alpine.js if you need sprinkles, React if you need state.
- ❌ Hand-rolled forms with `useState` everywhere → use **react-hook-form** + `zod` schemas. Free validation, error states, server-action support.
