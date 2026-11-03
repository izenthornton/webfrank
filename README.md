# webfrank

Marketing site for [FRANK Autonomous Systems Inc.](https://frank.space)

Static HTML/CSS, no build step. One page per nav tab, each showing a single
section; partners and contact live on the home page. Every page pulls the same
`css/site.css` and `js/site.js`; the only external dependency is Google Fonts.

## Layout

```
index.html           Home: hero, partners, contact
what/index.html      What we do, served at /what
team/index.html      The team and the advisory board, at /team
research/index.html  FRANK Research Group, at /research
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

There is no templating, so the nav and footer markup is copied into all four
pages. Changing a nav link means changing it in four files; the `active` class
marks the current tab and moves with it.

Images are named after the person or organisation they show, lowercase and
hyphenated, so a card's `src` says who is in it.

Replacing a photo but keeping its filename leaves browsers serving the cached
old one. Bump the `?v=` on that image's `src` when you swap a file in place —
headshots live in `team/index.html` and `research/index.html`, partner logos in
`index.html`.

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

Leave these records DNS only (grey cloud) until GitHub has issued the
certificate and "Enforce HTTPS" can be ticked in the repo's Pages settings.
Proxying them later needs Cloudflare SSL/TLS set to Full (strict); Flexible
loops forever against Enforce HTTPS.

`frankautonomous.com` is the old domain. GitHub Pages answers one custom domain
per repo, so the old one lands on a GitHub 404 unless Cloudflare redirects it
first. That takes a Single Redirect rule on the old zone, with its records
proxied (orange cloud):

```
When:    http.host in {"frankautonomous.com" "www.frankautonomous.com"}
Then:    301 to concat("https://frank.space", http.request.uri.path)
         preserve query string
```

## Contact

hello@frankautonomous.com
