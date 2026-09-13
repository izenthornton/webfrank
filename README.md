# webfrank

Marketing site for [FRANK Autonomous Systems Inc.](https://frankautonomous.com)

Static HTML/CSS, no build step. One page per nav tab, each showing a single
section. Every page pulls the same `css/site.css` and `js/site.js`; the only
external dependency is Google Fonts.

## Layout

```
index.html           Home: hero, proof chips, contact
what/index.html      What we do, served at /what
team/index.html      The team and the advisory board, at /team
research/index.html  FRANK Research Group, at /research
partners/index.html  Partners, at /partners
sarplan/index.html   SARPlan demo, at /sarplan (self-contained, predates the split)
css/site.css         Every style on the site
js/site.js           Menu toggle, scroll reveal, mailto clipboard fallback
img/brand/           Logo, favicon, OG card, starfield background
img/people/          Team, advisory board and research group headshots
img/partners/        Partner logos
CNAME                Custom domain for GitHub Pages
.nojekyll            Serve files as-is, no Jekyll processing
```

Pages live in subdirectories, so every asset and link is written root-absolute
(`/img/...`, `/css/site.css`, `/team/`). A relative path breaks on every page
but the home one.

There is no templating, so the nav and footer markup is copied into all five
pages. Changing a nav link means changing it in five files; the `active` class
marks the current tab and moves with it.

Images are named after the person or organisation they show, lowercase and
hyphenated, so a card's `src` says who is in it.

Replacing a photo but keeping its filename leaves browsers serving the cached
old one. Bump the `?v=` on that image's `src` when you swap a file in place —
headshots live in `team/index.html` and `research/index.html`.

## Run locally

```sh
python3 -m http.server 5173
# then open http://localhost:5173
```

## Deploy

Static — drop the repo contents on any host (GitHub Pages, Cloudflare Pages,
Netlify, etc.).

## Contact

hello@frankautonomous.com
