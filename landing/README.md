# AgentBrake landing page

The agentbrake.dev landing page. Next.js 16 (App Router) + Tailwind v4 +
TypeScript, **statically exported** — light theme with a 21st.dev aurora hero.

SEO is baked in: pre-rendered HTML, full `metadata`, JSON-LD (SoftwareApplication
+ Organization + FAQPage), semantic markup, `robots.txt`, `sitemap.xml`,
`llms.txt`, and `pricing.md`.

## Develop

```bash
cd landing
npm install
npm run dev        # http://localhost:3000
```

## Build (static export)

```bash
npm run build      # -> out/   (pure static HTML/CSS/JS, deploy anywhere)
```

`next.config.ts` sets `output: "export"`, so `npm run build` writes a fully
static site to `out/`. No server needed.

## Deploy to agentbrake.dev

- **Vercel** (easiest): import the repo, set the project root to `landing/`.
  Vercel detects Next.js and builds automatically; point the `agentbrake.dev`
  domain at it.
- **Any static host** (Netlify, Cloudflare Pages, GitHub Pages): run
  `npm run build` and serve the `out/` folder.

## Structure

- `src/app/layout.tsx` — global metadata, fonts (Inter + JetBrains Mono).
- `src/app/page.tsx` — server component: JSON-LD + renders the landing.
- `src/components/landing.tsx` — the page UI (hero, problem, how-it-works,
  what-it-catches, FAQ, CTA, footer).
- `src/components/ui/aurora-background.tsx` — the 21st.dev aurora hero.
- `public/` — `agentbrake.gif`, `og.png`, `robots.txt`, `sitemap.xml`,
  `llms.txt`, `pricing.md`.

## Note on the `website/` folder

`../website/` holds an earlier static, multi-page SEO build (programmatic
comparison pages `/vs/*` and glossary pages `/glossary/*`). Those pages aren't
in this Next app yet — they can be ported in as routes when you want the full
programmatic-SEO surface. This `landing/` app is the primary homepage.
