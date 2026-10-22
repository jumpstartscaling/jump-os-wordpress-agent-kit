# Page builders plugins and themes

This guide tells a site owner or a tenant-scoped agent how to identify the system that owns a WordPress page, find the right product documentation, and make a bounded change without accidentally replacing the site’s layout, theme, license, security, or commerce configuration.

It is an operating guide, not a compatibility certification. The installed version, active theme, enabled add-ons, WordPress role, and hosting policy remain authoritative for each site.

## First rule identify the owner of the page

Before editing, answer these questions and record the result in the private handoff or change request:

| Question | Why it matters |
| --- | --- |
| What is the exact page URL, page ID, and requested outcome? | Prevents an edit to a lookalike page, template, or staging site. |
| Which editor opens this page: Block Editor, Elementor, Divi, Beaver Builder, Bricks, or another builder? | A page must be edited in the system that created its layout. |
| Is the page using a reusable template, global section, theme template, pattern, or dynamic field? | A local-looking change can affect many pages. |
| What active theme, child theme, and builder/plugin versions are involved? | Documentation and migration steps are version-sensitive. |
| Is a staging site, revision, provider backup, or export available? | Required before a destructive, global, commerce, security, or update action. |

Do not convert a page from one builder to another, replace builder markup with block content, import a demo, regenerate global styles, change a theme template, or edit theme/plugin files simply because an agent cannot find a familiar editor. Stop and ask the owner.

## Safe discovery workflow

1. Confirm the canonical site and page URL from the private package or the owner.
2. Open the page from **Pages** or **Posts** in WordPress and use the editor label or edit action shown there. Do not infer the builder from the front-end design alone.
3. Ask an administrator to record the active theme, child theme, installed builder/plugin names, versions, active state, and any must-use or network-active plugins. A standard Editor role may not be able to see this inventory; that is intentional.
4. Find the product’s official documentation using the exact product name, publisher, and installed version. Prefer the product’s Help, Docs, Knowledge Base, Changelog, or release notes over a search-result snippet, random tutorial, or copied code.
5. Work on a revision, draft, staging copy, or one named page. Preview on desktop and mobile before publication.
6. Record the changed URL, editor used, reusable/global objects touched, screenshot or preview result, and rollback method. For a public page, have the owner name the acceptance URL.

WordPress itself provides the baseline for [editing pages and blocks](https://wordpress.org/documentation/), [managing plugins](https://wordpress.org/documentation/article/manage-plugins/), and [themes](https://wordpress.org/documentation/article/work-with-themes/). The WordPress plugin and theme handbooks are reference material for custom development, not a reason to edit production files directly.

## Major page builders

The table identifies common builders and the safest way to approach them. It is intentionally organized by ownership boundary instead of claiming that one editor can safely manipulate another editor’s content.

| Builder or system | How to recognize it | Bounded page work | Owner approval required before | Official starting point |
| --- | --- | --- | --- | --- |
| **WordPress Block Editor and Site Editor** | Standard WordPress editor, blocks, patterns, `theme.json`, or Appearance/Editor screens | Edit the named page’s blocks, content, media, and page-level settings | Site styles, templates, template parts, navigation, synced patterns, `theme.json`, or a block/theme conversion | [WordPress documentation](https://wordpress.org/documentation/) and [Theme Handbook](https://developer.wordpress.org/themes/) |
| **Elementor** | Elementor edit action, Elementor plugin, or Elementor templates | Edit the named page in Elementor; preserve containers, widgets, responsive settings, and existing global tokens | Theme Builder templates, Site Settings, global fonts/colors, kits, popups, Forms integrations, custom code, migration, or plugin update | [Elementor Knowledge Hub](https://elementor.com/help/) and [developer docs](https://developers.elementor.com/docs/) |
| **Divi** | Divi theme/Divi Builder edit action, Divi Library, or Visual Builder | Edit a named page/module while preserving the existing section-row-module hierarchy | Divi Library globals, Theme Builder, presets, role editor, global variables, Divi 4-to-5 migration, or template-wide styling | [Elegant Themes Help Center](https://help.elegantthemes.com/en/) |
| **Beaver Builder** | Launch Beaver Builder action, `fl-builder` layouts, saved modules/rows/templates | Use the builder for the named layout and prefer its preview/revision path | Global rows/modules, saved templates, Themer layouts, global styles, custom CSS/JS, cache/output settings, or plugin updates | [Beaver Builder documentation](https://docs.wpbeaverbuilder.com/) |
| **Bricks** | Bricks theme, Bricks builder action, templates, global classes, or query loops | Edit the named page with its existing elements and classes | Templates, global classes, theme styles, conditions, dynamic queries, code elements, builder access, or global settings | [Bricks Academy](https://academy.bricksbuilder.io/) |
| **Oxygen** | Oxygen editor, templates, selectors, components, or dynamic data | Make narrow content/style changes in the existing Oxygen page or component only when the owner identifies scope | Reusable selectors, components, templates, conditions, dynamic data, custom code, framework migration, or global settings | [Oxygen documentation](https://oxygenbuilder.com/documentation/) |
| **Breakdance** | Breakdance editor, design presets, selectors, templates, or global settings | Edit the named page with existing elements and verify responsive behavior | Design presets, selectors, templates, WooCommerce templates, forms/integrations, global settings, or code | [Breakdance documentation](https://breakdance.com/documentation/) |
| **WPBakery Page Builder** | WPBakery backend/front-end editor or shortcode-heavy content | Use the existing WPBakery editor for a named page; keep shortcode structure intact | Template library, grid builder, custom CSS/JS, role manager, add-ons, bundled-plugin update, or migration to another builder | [WPBakery Knowledge Base](https://kb.wpbakery.com/docs/) |
| **Visual Composer Website Builder** | Visual Composer editor and its hub/templates | Edit only the named page in Visual Composer and preserve existing elements | Global design options, templates, role/access controls, integrations, custom CSS/JS, or migration | [Visual Composer Help Center](https://help.visualcomposer.com/) |
| **SeedProd** | SeedProd landing/coming-soon/maintenance or theme templates | Edit the named landing page or mode page after confirming it is not live site-wide routing | Coming Soon/Maintenance mode, custom login/404, theme templates, WooCommerce templates, email integrations, domain mapping, or bypass settings | [SeedProd documentation](https://www.seedprod.com/docs/) |
| **Spectra and other block suites** | Spectra/Kadence/GenerateBlocks-style blocks in the Block Editor | Edit the named block content and preserve responsive/global settings | Global styles, design libraries, reusable patterns, dynamic content, custom CSS, or a plugin suite update | [Spectra documentation](https://wpspectra.com/docs/) and the exact vendor’s docs |

### Builder-specific safety notes

- **One page, one primary editor.** A page may contain shortcodes, blocks, and embedded builder content, but an agent must not replace the primary layout system to make editing easier.
- **Templates are multipliers.** Headers, footers, archive/single templates, popups, reusable sections, synced patterns, libraries, global modules, global classes, and global styles need an explicit site-wide scope from the owner.
- **Dynamic data needs source approval.** ACF, Meta Box, Pods, WooCommerce fields, custom post types, and query loops can display data across many pages. Change the field or query only with a named test case and rollback.
- **Use the builder’s own revision or history feature when available.** A WordPress revision, staging backup, or provider restore point is still the recovery authority; an editor history panel alone is not a backup.
- **Do not solve a preview problem by changing cache, permalinks, security rules, server PHP, or licenses.** Collect the exact error and escalate through the owner’s approved path.

## Common installed plugin families

No guide can safely enumerate every WordPress plugin. These categories cover common footprints and explain the permission boundary an agent should observe.

| Plugin family and examples | Read or page-level work may be appropriate when granted | Treat as owner-only or separately approved |
| --- | --- | --- |
| **Commerce** — WooCommerce and store extensions | Product copy, images, a named product/page draft, or a clearly scoped content attribute | Payments, tax, shipping, subscriptions, refunds, order status, inventory, checkout templates, webhooks, customer data, extensions, or API keys |
| **Forms** — Contact Form 7, WPForms, Gravity Forms, Ninja Forms, Fluent Forms | Copy or layout of a named embedded form only after identifying the form owner | Recipients, notifications, confirmations, spam/CAPTCHA, webhooks, payment forms, conditional routing, exports, entries, or integrations |
| **SEO** — Yoast, Rank Math, All in One SEO, SEOPress | Page title, description, and content metadata for one named page when the owner requests it | Global schema, robots, sitemap, canonical policy, redirects, search-console links, bulk changes, or indexing controls |
| **Security** — Wordfence, Solid Security, Sucuri, firewall/WAF plugins | Read a documented alert or status only if the role permits it | Firewall mode, allow/block lists, login policy, scan remediation, file repair, two-factor settings, API keys, or plugin updates |
| **Performance and cache** — WP Rocket, LiteSpeed Cache, W3 Total Cache, Autoptimize, Perfmatters | Observe cache state and use a named, approved cache purge if the site owner exposes it | Minification, delay/defer, critical CSS, CDN, object cache, image rewrite, database cleanup, server cache, or global performance presets |
| **Backup and migration** — UpdraftPlus, Duplicator, WPvivid, All-in-One WP Migration | Verify that an owner-provided backup receipt or staging path exists | Backup destination credentials, restore, clone, migration, search/replace, archive download, or update without a verified restorable backup |
| **Custom fields and content models** — ACF, Meta Box, Pods, CPT UI | Populate an owner-named field on an owner-named record | Field-group schema, post type/taxonomy definitions, options pages, relationships, PHP render callbacks, migrations, or imports |
| **Membership, LMS, booking** — MemberPress, LearnDash, LifterLMS, booking plugins | Public copy, lesson/page draft, or non-sensitive content explicitly requested | Access rules, pricing, subscriptions, learner/member data, appointments, payment, reminders, emails, webhooks, or exports |
| **Multilingual** — WPML, Polylang, TranslatePress, Weglot | Draft/translate an owner-named page in its existing translation workflow | Language URL structure, locale/domain mapping, string-wide translation, automatic translation credentials, synchronization policy, or bulk translation |
| **Analytics and marketing** — Site Kit, GTM plugins, PixelYourSite, MonsterInsights | Review an owner-provided status or edit copy on a named landing page | Measurement IDs, consent mode, tags, pixels, conversion events, ad accounts, API/OAuth credentials, audiences, or server-side tracking |
| **Media and optimization** — image compression, gallery, slider, CDN media plugins | Replace media on one named page after checking alt text, licensing, dimensions, and mobile display | Bulk optimization, destructive media cleanup, CDN rewrites, remote storage, gallery-wide template changes, or watermark policy |

For an unfamiliar plugin, do not classify it by its icon or name alone. Capture the exact plugin name, publisher, version, plugin directory/slug if available, active state, and the requested operation; then use the documentation workflow below.

## Find trustworthy product documentation

### Public WordPress.org plugins and themes

1. In WordPress, note the product name, version, author, and active state. The administrator can also inspect the plugin/theme details screen; an Editor should not try to bypass that boundary.
2. For a directory product, start at its [WordPress.org plugin page](https://wordpress.org/plugins/) or theme page. Use the product’s **Details**, **Support**, **Changelog**, and linked vendor site.
3. Prefer the publisher’s current Help/Docs/Knowledge Base and release notes for the detected major version. Check whether an add-on, premium edition, or companion theme changes the answer.
4. Preserve a short evidence record: product/version, official URL, exact task, constraints, test page, result, and rollback route.

### Premium, bundled, and ThemeForest assets

ThemeForest themes often bundle a builder or premium plugin, a child theme, demo content, and an author-specific updater. The buyer’s installation is the authority; a similarly named plugin from the WordPress.org directory may not be the same licensed bundle.

1. Identify the active theme and child theme from **Appearance → Themes** or an administrator-provided inventory. Record the theme name, author, version, theme URI, and text domain. For a classic theme, `style.css` normally carries these headers; do not edit it on production just to inspect it.
2. Ask the owner for the exact ThemeForest item URL or item ID. Start with the item page, then the author’s linked documentation, changelog, support route, and included `documentation`, `docs`, `readme`, or `changelog` files in the purchased download.
3. Use the owner’s Envato/ThemeForest account only through its normal UI. Never paste a purchase code, license key, download archive, or account credential into an agent prompt, repository, ticket, or public discussion.
4. Treat demo importers, bundled-plugin installers, theme updaters, “reset” tools, and sample data as destructive/site-wide actions. Run them only on staging with the owner’s written scope and a proven restore path.
5. Keep custom changes in the project’s approved child theme, custom-CSS area, builder child template, or a custom plugin. Do not patch vendor theme/plugin files: an update will overwrite them and complicate support.

Envato’s buyer/author help, licensing, and support policies change over time; begin from [Envato Help](https://help.market.envato.com/hc/en-us) and the exact item’s support documentation rather than relying on a copied purchase-code workflow.

## Change gates for humans and agents

| Requested action | Minimum evidence before action | Who may perform it |
| --- | --- | --- |
| Edit copy, image, or layout on one identified page | Page/editor identified; preview path; owner’s requested outcome | Editor or scoped agent |
| Change a reusable component, template, global style, or dynamic field | Named downstream pages; staging/revision; rollback; owner approves site-wide scope | Owner or explicitly authorized operator |
| Purge a named cache | Owner confirms the cache layer and requested scope | Named capability or human owner |
| Update/activate/deactivate plugin or theme | Exact artifact/version; verified restorable backup; provider/maintenance capability; post-change acceptance route | Owner or Host Gateway capability only |
| Change security, payments, email, analytics, licenses, domains, or hosting | Product-specific plan and owner approval; never infer from an Editor account | Owner / specialist, not the recipient package |

An agent receiving this kit may read documentation, prepare a change plan, and perform only the narrow WordPress or gateway capabilities in its private package. Documentation never creates a new permission.

## Copyable discovery record

Use this in a private request, not in the public repository:

```text
Tenant and canonical URL:
Requested page or object:
Detected primary editor:
Active theme and child theme:
Relevant product name, publisher, version, and active state:
Reusable/global/dynamic objects affected:
Official documentation and changelog URL:
Allowed action and named acceptance URL:
Recovery path (revision, staging, provider backup, or restore receipt):
Result and verification:
```

If a field cannot be established, the next step is to ask the owner—not to broaden access, install another plugin, or guess.
