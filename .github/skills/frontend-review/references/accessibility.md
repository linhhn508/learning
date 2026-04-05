# Accessibility Checklist

Bootstrap 4 + Jinja2 accessibility best practices.

## Critical (WCAG 2.1 Level A)

- [ ] All images have `alt` attributes — TinyMCE image dialog has an alt field; ensure it's required
- [ ] Form inputs have associated `<label>` elements (not just placeholder text)
- [ ] Color is not the only indicator — badges, buttons, links must have text/icons too
- [ ] Page has exactly one `<h1>` — check each template
- [ ] Heading hierarchy is sequential (`h1` → `h2` → `h3`, no skipping)
- [ ] All interactive elements are keyboard accessible (links, buttons, modals)
- [ ] Skip-to-content link at top of `base.html`: `<a href="#main" class="sr-only sr-only-focusable">Skip to content</a>`
- [ ] Language attribute: `<html lang="en">` ✓ (already present)

## Important (WCAG Level AA)

- [ ] Sufficient color contrast — text (#444) on white (#fff) = 9.7:1 ✓; check dark mode
- [ ] Dark mode contrast — text (#d4d4d4) on dark bg (#1a1d23) = 10.2:1 ✓
- [ ] Focus indicators visible — Bootstrap default outlines; don't override with `outline: none`
- [ ] Touch targets ≥ 44×44px — check mobile nav, scroll-to-top button (currently 44px ✓)
- [ ] Error messages reference the field — flash messages should name the field ("Title is required")
- [ ] Links are distinguishable from surrounding text (underline or icon, not just color)

## ARIA Patterns

```html
<!-- Modal: already correct -->
<div class="modal" role="dialog" aria-labelledby="deleteModalLabel" aria-hidden="true">

<!-- Alert auto-dismiss: add role -->
<div class="alert" role="alert">

<!-- Search form: add role -->
<form role="search" method="GET" action="...">

<!-- Nav: add aria-current -->
<a class="nav-link" aria-current="page" href="...">Home</a>
```

## Dark Mode Accessibility

- Ensure sufficient contrast in both modes for all text, badges, and buttons
- Use `prefers-color-scheme` media query as initial default, then let localStorage override
- Add `aria-label` to the dark mode toggle button describing its current state
