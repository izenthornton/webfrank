# webfrank

Marketing site for [FRANK Autonomous Systems Inc.](https://frankautonomous.com)

Static HTML/CSS, no build step. `index.html` is self-contained — all styles
and scripts are inline; the only external dependency is Google Fonts.

## Layout

```
index.html          Main site (nav, hero, what we do, team, advisory board,
                    research group, partners, contact)
sarplan/index.html  SARPlan demo, served at /sarplan
img/brand/          Logo, favicon, OG card, starfield background
img/people/         Team, advisory board and research group headshots
img/partners/       Partner logos
CNAME               Custom domain for GitHub Pages
.nojekyll           Serve files as-is, no Jekyll processing
```

Images are named after the person or organisation they show, lowercase and
hyphenated, so a card's `src` says who is in it.

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
