# PR Review Skill — Sail With Us Stack

Use this guide when conducting a PR review for this project. The stack is:
- **Backend:** Django (Python 3.12+), PostgreSQL, allauth, Wagtail (CMS only)
- **Frontend:** Django templates, vanilla JS, CSS custom properties (no build step)
- **Tests:** Playwright E2E (see `.ai-instructions/playwright-skill/`)
- **Infra:** AWS ECS Fargate, Terraform, Cloudflare DNS, S3, SES

---

## Four-Phase Review Process

### 1. Context (1–2 min)
- What is the PR trying to accomplish?
- Is there a related issue or user story?
- Check CI status — do not approve a PR with failing checks.

### 2. High-Level (3–5 min)
- Does the approach make sense for this codebase?
- Are new migrations reversible? Do they include a `reverse` function?
- Any new dependencies added? Are they well-maintained libraries?
- SEO regression: do new/modified pages have `<title>`, meta description, canonical, OG tags?

### 3. Line-by-Line (10–20 min)
Focus on the areas below. Delegate formatting/style to ruff/the linter.

### 4. Summary & Decision
Use severity labels:
- 🔴 `[blocking]` — must fix before merge (security, data loss, broken functionality)
- 🟡 `[important]` — should fix; discuss if you disagree
- 🟢 `[nit]` — minor style or clarity, not blocking
- 💡 `[suggestion]` — alternative worth considering
- 🎉 `[praise]` — good pattern worth calling out

---

## Django-Specific Checklist

### Models & Migrations
- [ ] New `ForeignKey` fields have `on_delete` set intentionally (not just `CASCADE` by default)
- [ ] `UUIDField` used for primary keys on new models (project standard)
- [ ] No raw SQL strings — use ORM or `RawSQL` with parameterized queries
- [ ] `select_related` / `prefetch_related` used when accessing related objects in views
- [ ] No N+1 queries hidden in templates (watch for `{{ entry.crew_members.all }}` in loops)
- [ ] New migrations have a sensible name and do not include accidental field changes

### Views
- [ ] Function-based views preferred over class-based views (project standard)
- [ ] No direct `request.GET`/`request.POST` access without validation at system boundaries
- [ ] Redirect after POST (PRG pattern) to prevent double-submit
- [ ] `next` redirect parameters validated with `next_url.startswith('/')` (no open redirects)
- [ ] Sensitive operations gated on `request.user.is_authenticated` and role checks
- [ ] `get_object_or_404` used instead of bare `.get()` in views

### Security
- [ ] No user-controlled data passed to `shell()`, `exec()`, `os.system()`, or `subprocess`
- [ ] No `mark_safe()` on user-supplied content
- [ ] CSRF tokens present on all state-changing forms
- [ ] File uploads validated (type, size) before saving
- [ ] No secrets or API keys hardcoded — environment variables only
- [ ] `request.POST.get('next')` always validated before redirect

### Templates
- [ ] No `{% autoescape off %}` or `|safe` on user-controlled data
- [ ] New pages extend `base.html` and fill `{% block title %}` and `{% block meta_description %}`
- [ ] Admin-only UI gated on `{% if request.user.is_site_admin %}` or appropriate role check
- [ ] No emoji — use inline SVG icons (Heroicons stroke-width 1.5/1.8)
- [ ] `ENABLE_EMAIL_SENDING` is not hardcoded — flag is environment-driven

---

## AWS / Infrastructure Checklist (Terraform)

- [ ] New ECS task definition env vars use `name`/`value` pairs, not secrets exposed in plaintext
- [ ] S3 bucket policies do not grant public read unless intentional (static assets only)
- [ ] IAM policies follow least privilege — no `*` actions on sensitive resources
- [ ] New Terraform resources tagged with `Project` and `Environment`
- [ ] ALB security group changes reviewed: inbound rules should only allow 80/443 from internet
- [ ] ECS task CPU/memory limits set appropriately — check against existing tasks
- [ ] Cloudflare DNS changes reviewed: proxied vs unproxied is intentional
- [ ] No `terraform destroy` commands or resource deletions without confirmation in PR description

---

## Playwright Test Checklist

- [ ] New UI features have corresponding Playwright tests
- [ ] Tests use `getByRole()` / `getByLabel()` — no CSS selectors or XPath
- [ ] No `page.waitForTimeout()` — use web-first assertions
- [ ] New test users added to `global-setup.js` with verified `EmailAddress` records
- [ ] State accumulated by tests is reset in `global-setup.js` (see crew membership reset pattern)
- [ ] Tests are deterministic — no reliance on ordering or shared mutable state

---

## Feedback Language

Prefer questions and suggestions over imperatives:
- "Consider using `select_related` here to avoid an N+1 query" not "Use select_related"
- "Could this redirect be exploited with an external URL?" not "This is an open redirect"
- Praise good patterns explicitly — it reinforces them for future contributors

Do not comment on formatting, import order, or whitespace — ruff handles those.
