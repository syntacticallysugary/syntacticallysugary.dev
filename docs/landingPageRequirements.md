# SyntacticallySugary Landing Page — Requirements

## Domains
- `syntacticallysugary.com` (primary)
- `syntacticallysugary.dev` (tech/portfolio signal)
- Registered at Porkbun

## Purpose
Dual-function site:
1. Portfolio front-end for IT/cloud projects (GitHub: SyntacticallySugary)
2. Future consulting business presence (possible LLC)

## Tech Stack

### Framework: Astro
- Static-first, zero JS by default — fast and SEO-friendly
- Markdown support for project write-ups
- Supports React/Svelte components when interactivity is needed
- Native Tailwind support
- Deploys to GitHub Pages (free, reinforces portfolio identity)

### Styling: Tailwind CSS + shadcn/ui
- Tailwind config and design tokens already exist in the tutor system
- Copy `frontend/tailwind.config.js` and `frontend/src/index.css` directly
- Gives visual consistency between landing page and tutor app out of the box

### Existing Design System (from tutor system)
- **Fonts:** Inter (sans), JetBrains Mono (monospace)
- **Primary palette:** Blue (`#3b82f6` family), full 50–900 scale
- **Semantic scales:** success (green), warning (yellow), error (red), info (sky)
- **CSS custom properties** defined at `:root` — portable across projects
- **Component classes:** `.card`, `.btn`, `.badge`, `.input`
- Apply subset to ERPNext via custom CSS injection to match brand colors

### Hosting: GitHub Pages (initial)
- Free, fits portfolio identity
- Custom domain pointed via CNAME
- Upgrade to VPS later if ERPNext self-hosting is needed

## ERPNext Integration

### Strategy: Separate site → ERPNext via REST API
- Landing page stays fast and clean (static Astro)
- ERPNext runs separately (self-hosted Docker or ERPNext Cloud)
- Astro server-side API routes act as a thin proxy — API keys never exposed client-side

### Initial Integration Flow
```
Contact form (landing page)
  → POST to Astro API route
    → ERPNext REST API
      → Lead DocType created
        → ERPNext CRM workflow
```

### Auth
- ERPNext API key/secret (server-side only)
- JWT or session-based for future authenticated flows

### Educational Value
- Demonstrates live website → CRM pipeline integration
- Most ERPNext deployments are manual-entry black boxes — this is a differentiator
- Serves as a portfolio piece and consulting reference implementation

### Progression
1. ERPNext local dev via Docker
2. Contact form → Lead API call
3. Project/portfolio inquiry → Project DocType
4. Webhooks: ERPNext pushes status updates back to site

## Design Consistency Across Three Surfaces
| Surface | Approach |
|---|---|
| Landing page | Full design system (Tailwind + tokens) |
| Tutor system | Source of design system — already implemented |
| ERPNext | Inject CSS variables via Frappe custom CSS setting |

## Future Considerations
- `.com` is squatted — monitor or negotiate later
- Pre-pay `.dev` for multiple years to lock in pricing before Google registry increases
- ERPNext self-hosting needs a real server (~$6/mo Hetzner/DigitalOcean VPS)
- Cloudflare can be layered in front of GitHub Pages later without changing registrar
