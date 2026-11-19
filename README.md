# webfrank

Marketing site for [FRANK Autonomous Systems Inc.](https://frank.space)

Static HTML/CSS, no build step. One page per nav tab, each showing a single
section; partners and contact live on the home page. Every page pulls the same
`css/site.css` and `js/site.js`; the only external dependency is Google Fonts.

The look follows the pitch deck: Deep Space, Russo One caps for titles and
labels, Signal Red as the only accent, and the lunar point mesh. The home hero
is the deck's title slide (the wordmark over the mesh, a rover setting out along
a red route to a flag), and every page ends on the same ground behind its
footer.

## Layout

```
index.html           Home: hero, partners, contact
what/index.html      What we do, served at /what
team/index.html      The team and the advisory board, at /team
research/index.html  FRANK Research Group, at /research
sarplan/index.html   SARPlan demo, at /sarplan (self-contained, predates the split)
css/site.css         Every style on the site
js/site.js           Menu toggle, scroll reveal, mailto clipboard fallback
img/brand/           Logo, favicon, OG card, star tile, mesh scenes
img/people/          Team, advisory board and research group headshots
img/partners/        Partner logos
img/what/            The pictures on the What we do page, taken from the deck
tools/               render_scenes.py, which draws the mesh scenes
CNAME                Custom domain for GitHub Pages
.nojekyll            Serve files as-is, no Jekyll processing
```

Pages live in subdirectories, so every asset and link is written root-absolute
(`/img/...`, `/css/site.css`, `/team/`). A relative path breaks on every page
but the home one.

There is no templating, so the nav and footer markup is copied into all four
pages. Changing a nav link means changing it in four files; the `active` class
marks the current tab and moves with it.

Images are named after the person or organisation they show, lowercase and
hyphenated, so a card's `src` says who is in it.

Replacing a photo but keeping its filename leaves browsers serving the cached
old one. Bump the `?v=` on that image's `src` when you swap a file in place —
headshots live in `team/index.html` and `research/index.html`, partner logos in
`index.html`.

`css/site.css` is cached the same way; bump its `?v=` in all four pages when
the stylesheet changes.

## Mesh scenes

`img/brand/scene-hero.webp`, `scene-ground.webp` and `stars.png` are drawn in
code, with no source artwork:

```sh
python3 tools/render_scenes.py     # needs numpy and Pillow
```

Seeds and waypoints are fixed, so a re-run reproduces the same landscape. The
hero's flag is an HTML element pinned to the end of the route; the script prints
that pin's position, and if the hero route changes those two percentages go into
`.flag` in `css/site.css`. `og-card.jpg` is a 1200 x 630 capture of the hero.

## Run locally

```sh
python3 -m http.server 5173
# then open http://localhost:5173
```

## Deploy

GitHub Pages builds `main` and serves it at the domain in `CNAME`
(`frank.space`). DNS for the domain lives in Cloudflare:

```
frank.space      A      185.199.108.153
frank.space      A      185.199.109.153
frank.space      A      185.199.110.153
frank.space      A      185.199.111.153
www.frank.space  CNAME  izenthornton.github.io
```

All five are proxied (orange cloud), so visitors get Cloudflare's certificate
and GitHub never issues its own; "Enforce HTTPS" in the repo's Pages settings
stays unavailable and that is expected. Cloudflare handles HTTPS instead:
SSL/TLS mode is Full and Always Use HTTPS is on. Keep the mode at Full;
Flexible can loop, and Full (strict) rejects GitHub's certificate. The MX and
TXT records beside them are Google Workspace mail for frank.space; leave them
alone.

`frankautonomous.com` is the old domain. GitHub Pages answers one custom domain
per repo, so Cloudflare redirects the old one before it reaches GitHub. Its zone
in the FRANK Cloudflare account carries proxied (orange cloud) A and `www`
records, its Google Workspace mail records (MX, SPF, DKIM, DMARC; DNS only),
and this Single Redirect rule:

```
When:    http.host in {"frankautonomous.com" "www.frankautonomous.com"}
Then:    301 to concat("https://frank.space", http.request.uri.path)
         preserve query string
```

## Contact

hello@frank.space
