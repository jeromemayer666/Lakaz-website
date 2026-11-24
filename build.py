"""Convert the Lakaz website design pages (.dc.html) into a plain static site.

python3 build.py [--preview]   -> writes ./out/  (preview adds numbered spot badges)
"""
import re, sys, os, html

PREVIEW = "--preview" in sys.argv
OUT = "out-preview" if PREVIEW else "out"
os.makedirs(OUT, exist_ok=True)

PAGES = {"Home": "index.html", "Houses": "houses.html", "Filao": "filao.html",
         "Coco": "coco.html", "Story": "story.html", "Contact": "contact.html"}

# focus point per photo (object-position), so the subject stays in frame on wide laptops and tall phones
FOCUS = {38: "50% 38%", 37: "60% 62%", 12: "62% 62%", 1: "52% 34%", 34: "50% 45%", 5: "38% 55%", 17: "48% 36%", 31: "50% 72%", 14: "50% 55%", 19: "50% 50%"}

def srcset(pid):
    return ", ".join(f"{u(pid, w)} {w}w" for w in (800, 1400, 2000, 2600))

def u(pid, w=2000):
    return f"https://images.unsplash.com/photo-{pid}?w={w}&q=80&auto=format&fit=crop"

# Unsplash photos picked (number = the contact-sheet number shown to Jérôme)
PHOTO = {
    38: ("1506059837806-7de0cf7d4dc6", "A pirogue resting on the rocks at sunrise"),
    31: ("1529852572069-2fcbe7599434", "A thatched beach parasol at sunset"),
    12: ("1589745659208-9bdc6fb0ef23", "White sand, shade trees and a turquoise lagoon"),
    1:  ("1513415277900-a62401e19be4", "Le Morne and the lagoon seen from above"),
    36: ("1791386628431-f10b20bc3d80", "Coconuts and lemons at a market stall"),
    14: ("1662039071109-001778325956", "Boats moored in a turquoise bay"),
    19: ("1686740297492-7ab8937a2548", "The red-roofed church at Cap Malheureux"),
    5:  ("1686739996006-7c2cdff5d34c", "A white sandbar curving into a turquoise lagoon"),
    37: ("1593692930150-37bbe001a9b6", "Palm trees silhouetted against the lagoon at dusk"),
    34: ("1768734836337-fa47d15984b3", "Fresh fruit piled high at a market stall"),
    17: ("1653940509310-e07dcedb1933", "A small boat on a calm green lagoon, seen from above"),
}

# Per page, in the order the <img> tags appear: ("photo", spot, number) or ("ph", label)
SLOTS = {
    "Home":    [("photo", 1, 38), ("ph", "Lakaz Filao · living room"), ("ph", "Lakaz Coco · kitchen"), ("photo", 2, 37)],
    "Houses":  [("ph", "Lakaz Filao · best wide shot"), ("ph", "Lakaz Coco · best wide shot")],
    "Filao":   [("ph", "Lakaz Filao · living room"), ("ph", "Lakaz Filao · bedroom"), ("ph", "Lakaz Filao · terrace"), ("ph", "Lakaz Filao · kitchen")],
    "Coco":    [("ph", "Lakaz Coco · kitchen"), ("ph", "Lakaz Coco · bedroom"), ("ph", "Lakaz Coco · living room"), ("photo", 3, 12)],
    "Story":   [("photo", 4, 1), ("ph", "An interior with character · arched window or detail"), ("photo", 5, 12), ("photo", 6, 34)],
    "Contact": [("photo", 7, 5)],
}

BADGE_CSS = """
.spot{position:absolute;bottom:14px;left:14px;z-index:5;background:#B4633A;color:#fff;font:600 15px/1.2 Jost,sans-serif;padding:8px 14px;border-radius:999px;box-shadow:0 4px 14px rgba(0,0,0,.35);letter-spacing:.02em}
.spot.ph{background:#1F3B2D}
"""

LOGO_SVG = ('<svg width="34" height="42" viewBox="0 0 120 150" aria-hidden="true"><path d="M10 146 V60 A50 50 0 0 1 110 60 V146" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>'
            '<circle cx="60" cy="44" r="9" fill="#E0A47E"/><path d="M28 92 L60 64 L92 92 Z" fill="currentColor" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/>'
            '<path d="M36 98 V124 M50 98 V124 M70 98 V124 M84 98 V124" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><path d="M26 124 H94" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>'
            '<path d="M30 136 q7.5 -5 15 0 t15 0 t15 0 t15 0" fill="none" stroke="#E0A47E" stroke-width="3" stroke-linecap="round"/></svg>')

HEADER_CSS = """
.site-head{position:absolute;top:0;left:0;right:0;z-index:30;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px clamp(16px,3vw,40px);box-sizing:border-box;color:#FFFBF2}
.site-head.over::before{content:"";position:absolute;inset:0 0 -50px;background:linear-gradient(rgba(10,20,14,.38),rgba(10,20,14,0));pointer-events:none;z-index:-1}
.site-head.ink{position:relative;color:#1F3B2D}
.site-head .brand{display:flex;align-items:center;gap:10px;color:inherit;text-decoration:none;font-family:"Cormorant Garamond",serif;font-weight:600;font-size:1.6rem;letter-spacing:.08em}
.site-head.over .brand,.site-head.over .burger{filter:drop-shadow(0 1px 3px rgba(0,0,0,.35))}
.burger{margin-left:auto;display:inline-flex;align-items:center;justify-content:center;width:52px;height:52px;background:none;border:0;border-radius:999px;color:inherit;cursor:pointer;transition:background .2s}
.burger:hover,.burger:focus-visible{background:rgba(255,255,255,.14)}
.site-head.ink .burger:hover,.site-head.ink .burger:focus-visible{background:rgba(31,59,45,.08)}
.menu-backdrop{position:fixed;inset:0;z-index:40;background:rgba(14,28,20,.38);backdrop-filter:blur(7px);-webkit-backdrop-filter:blur(7px);opacity:0;visibility:hidden;transition:opacity .3s,visibility .3s}
.menu-panel{position:fixed;top:14px;right:14px;z-index:41;width:min(340px,calc(100vw - 28px));max-height:calc(100vh - 28px);overflow:auto;box-sizing:border-box;background:#1F3B2D;color:#F4EDE1;border-radius:22px;padding:18px 26px 22px;box-shadow:0 24px 60px rgba(0,0,0,.35);opacity:0;visibility:hidden;transform:translateY(-8px) scale(.98);transform-origin:top right;transition:opacity .25s,transform .25s,visibility .25s;font-family:Jost,sans-serif}
body.menu-open .menu-backdrop,body.menu-open .menu-panel{opacity:1;visibility:visible}
body.menu-open .menu-panel{transform:none}
.menu-panel .top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.menu-panel .top span{font-size:.75rem;letter-spacing:.32em;color:#E0A47E}
.menu-panel .close{width:44px;height:44px;margin-right:-10px;display:inline-flex;align-items:center;justify-content:center;background:none;border:0;border-radius:999px;color:inherit;cursor:pointer}
.menu-panel .close:hover,.menu-panel .close:focus-visible{background:rgba(255,255,255,.1)}
.menu-panel ul{list-style:none;margin:0;padding:0}
.menu-panel li a{display:block;padding:8px 0;color:#F4EDE1;text-decoration:none;font-family:"Cormorant Garamond",serif;font-size:2rem;line-height:1.1}
.menu-panel li a:hover,.menu-panel li a:focus-visible{color:#E0A47E}
.menu-panel li.sub a{font-size:1.3rem;font-style:italic;color:#E0A47E;padding:4px 0 4px 18px}
.menu-panel li.sub a:hover{color:#F4EDE1}
.menu-panel li a[aria-current]{color:#E0A47E}
.menu-panel .foot{margin-top:16px;padding-top:14px;border-top:1px solid #3E5A4A;font-size:.85rem;line-height:1.7;color:#D8CFBF}
.menu-panel .foot a{color:inherit}
@media (prefers-reduced-motion:reduce){.menu-backdrop,.menu-panel{transition:none}}
"""

def header_html(name, mode):
    brand = "" if name == "Home" else f'<a class="brand" href="index.html" aria-label="Lakaz home">{LOGO_SVG}<span>Lakaz</span></a>'
    def li(page, label, sub=False):
        cur = ' aria-current="page"' if page == name else ""
        cls = ' class="sub"' if sub else ""
        return f'<li{cls}><a href="{PAGES[page]}"{cur}>{label}</a></li>'
    links = (li("Home", "Home") + li("Houses", "Our Houses") + li("Filao", "Lakaz Filao", True) + li("Coco", "Lakaz Coco", True)
             + li("Story", "Lakaz Story") + li("Contact", "Contact Us"))
    return (f'<header class="site-head {mode}">{brand}'
            '<button type="button" class="burger" onclick="toggleMenu()" aria-controls="site-menu" aria-expanded="false" aria-label="Open menu">'
            '<svg width="30" height="20" viewBox="0 0 30 20" aria-hidden="true"><path d="M1 2 H29 M1 10 H29 M1 18 H29" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></header>'
            '<div class="menu-backdrop" onclick="toggleMenu()"></div>'
            '<div id="site-menu" class="menu-panel" role="dialog" aria-modal="true" aria-label="Menu">'
            '<div class="top"><span>LAKAZ</span><button type="button" class="close" onclick="toggleMenu()" aria-label="Close menu">'
            '<svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M2 2 L18 18 M18 2 L2 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></div>'
            f'<nav aria-label="Main"><ul>{links}</ul></nav>'
            '<div class="foot">Mont Choisy, Mauritius<br><a href="mailto:hello@lakazmauritius.com">hello@lakazmauritius.com</a><br>@lakaz.mauritius</div>'
            '</div>')

MENU_JS = """<script>
function toggleMenu(){var b=document.body,open=!b.classList.contains('menu-open');b.classList.toggle('menu-open',open);
var btn=document.querySelector('.burger');btn.setAttribute('aria-expanded',open);
if(open){setTimeout(function(){var a=document.querySelector('.menu-panel a');a&&a.focus()},60)}else{btn.focus()}}
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&document.body.classList.contains('menu-open'))toggleMenu()});
</script>
"""

def badge(text, ph=False):
    return f'<span class="spot{" ph" if ph else ""}">{html.escape(text)}</span>' if PREVIEW else ""

def convert(name):
    s = open(f"src/{name}.dc.html", encoding="utf-8").read()
    # head: pull helmet contents into <head>
    helmet = re.search(r"<helmet>(.*?)</helmet>", s, re.S).group(1)
    s = re.sub(r"<helmet>.*?</helmet>", "", s, flags=re.S)
    s = s.replace('<script src="./support.js"></script>', '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + helmet +
                  '<style>' + HEADER_CSS + (BADGE_CSS if PREVIEW else "") +
                  '.ph-box{display:flex;align-items:center;justify-content:center;text-align:center;background:#E3D8C6;color:#6B6A60;font-family:Jost,sans-serif;font-size:15px;letter-spacing:.04em;padding:16px;box-sizing:border-box}'
                  '.ph-box b{display:block;font-family:"Cormorant Garamond",serif;font-weight:500;font-size:22px;color:#1F3B2D;margin-top:4px}</style>')
    s = s.replace("<x-dc>", "").replace("</x-dc>", "")
    s = re.sub(r'<script type="text/x-dc".*?</script>', "", s, flags=re.S)
    # header: transparent over the hero photo, menu button top right, compact menu over a faded backdrop
    mode = "ink" if name == "Houses" else "over"
    s = re.sub(r"<header.*?</header>", lambda m: header_html(name, mode), s, count=1, flags=re.S)
    s = s.replace("</body>", MENU_JS + "</body>")
    # links
    for k, v in PAGES.items():
        s = s.replace(f'href="{k}.dc.html"', f'href="{v}"')
    # contact details
    s = s.replace("bonzour@[domain]", "hello@lakazmauritius.com").replace("[domain]", "lakazmauritius.com")
    # images
    slots = list(SLOTS[name])
    def rep(m):
        tag = m.group(0)
        style = re.search(r'style="([^"]*)"', tag).group(1)
        slot = slots.pop(0)
        if slot[0] == "photo":
            _, spot, num = slot
            pid, alt = PHOTO[num]
            img = f'<img src="{u(pid)}" srcset="{srcset(pid)}" sizes="100vw" alt="{html.escape(alt)}"{" fetchpriority=\"high\"" if spot == 1 else " loading=\"lazy\""} style="{style}; object-position: {FOCUS.get(num, "50% 50%")}">'
            return img + badge(f"Spot {spot} · Unsplash photo {num}")
        label = slot[1]
        box = f'<div class="ph-box" role="img" aria-label="Photo coming soon: {html.escape(label)}" style="{style}"><span>Photo coming soon<b>{html.escape(label)}</b></span></div>'
        return box + badge("Your photo", ph=True)
    s = re.sub(r"<img\b[^>]*>", rep, s)
    assert not slots, (name, slots)
    # Houses: new photo band under the intro
    if name == "Houses":
        band = (f'<section style="max-width: 1280px; margin: 0 auto; padding: 0 32px 2rem; box-sizing: border-box">'
                f'<div style="position: relative; height: clamp(16rem, 30vw, 28rem); border-radius: 24px; overflow: hidden">'
                f'<img src="{u(PHOTO[17][0])}" srcset="{srcset(PHOTO[17][0])}" sizes="100vw" alt="{PHOTO[17][1]}" loading="lazy" style="width: 100%; height: 100%; object-fit: cover; display: block; object-position: {FOCUS[17]}">'
                + badge("Spot 8 · Unsplash photo 17") + '</div></section>')
        s = s.replace("</section>", "</section>\n" + band, 1)
    HEIGHTS = {"Home": [("height: 48rem", "height: clamp(34rem, 56vw, 52rem)"), ("height: 34rem", "height: clamp(26rem, 42vw, 44rem)")],
               "Story": [("height: 30rem", "height: clamp(26rem, 46vw, 46rem)")],
               "Contact": [("height: 24rem", "height: clamp(24rem, 44vw, 44rem)")],
               "Coco": [("height: 40rem", "height: clamp(28rem, 48vw, 46rem)")],
               "Filao": [("height: 40rem", "height: clamp(28rem, 48vw, 46rem)")]}
    for a, b in HEIGHTS.get(name, []):
        assert s.count(a) == 1, (name, a, s.count(a))
        s = s.replace(a, b)
    if PREVIEW:
        # badges need a positioned parent
        s = s.replace("</body>", """<script>document.querySelectorAll('.spot').forEach(function(b){var p=b.parentElement;if(getComputedStyle(p).position==='static')p.style.position='relative'});</script></body>""")
    if name != "Home":
        pass
    open(f"{OUT}/{PAGES[name]}", "w", encoding="utf-8").write(s)

for n in PAGES:
    convert(n)
print("built", OUT, sorted(os.listdir(OUT)))
