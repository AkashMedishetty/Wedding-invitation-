#!/usr/bin/env python3
import base64, io, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

U = "/mnt/user-data/uploads/"
OUT = "/mnt/user-data/outputs/wedding/"
ASSETS = OUT + "assets/"

SRC = {
    "sky":    "1781826094380_image.png",
    "towers": "1781826103018_image.png",
    "arch":   "1781826108803_image.png",
    "garden": "1781826114218_image.png",
    "fore":   "1781826120741_image.png",
    "peacock":"1781826125615_image.png",
    "cows":   "1781826156578_image.png",
    "couple": "1781826216951_image.png",
}

def key_white(im, thresh=238, erode=1, feather=0.8, pad=6):
    """Remove ONLY background white connected to the image border.
    Enclosed white areas (white cow, white pavilion, lilies) are preserved."""
    im = im.convert("RGBA")
    a = np.array(im)
    r,g,b = a[...,0].astype(int),a[...,1].astype(int),a[...,2].astype(int)
    nw = (r>thresh)&(g>thresh)&(b>thresh)
    lbl,_ = ndimage.label(nw)                       # 4-conn components of near-white
    border = np.concatenate([lbl[0,:],lbl[-1,:],lbl[:,0],lbl[:,-1]])
    bg = set(np.unique(border)) - {0}
    bgmask = np.isin(lbl, list(bg))                 # background = white touching edge
    keep = ~bgmask
    if erode:                                       # trim 1px white fringe
        keep = ndimage.binary_erosion(keep, iterations=erode)
    alpha = (keep*255).astype(np.uint8)
    am = Image.fromarray(alpha,"L").filter(ImageFilter.GaussianBlur(feather))
    a[...,3] = np.array(am)
    out = Image.fromarray(a,"RGBA")
    bbox = out.getbbox()
    if bbox:
        x0,y0,x1,y1 = bbox
        x0=max(0,x0-pad);y0=max(0,y0-pad);x1=min(out.width,x1+pad);y1=min(out.height,y1+pad)
        out = out.crop((x0,y0,x1,y1))
    return out

def fit(im, w=None, h=None):
    if w: h2=int(im.height*w/im.width); im=im.resize((w,h2),Image.LANCZOS)
    elif h: w2=int(im.width*h/im.height); im=im.resize((w2,h),Image.LANCZOS)
    return im

def webp_b64(im, q=80, rgb=False):
    buf=io.BytesIO()
    if rgb: im.convert("RGB").save(buf,"WEBP",quality=q,method=6)
    else:   im.save(buf,"WEBP",quality=q,method=6)
    data=buf.getvalue()
    return data, "data:image/webp;base64,"+base64.b64encode(data).decode()

uri={}
# sky: keep full, no key
sky=fit(Image.open(U+SRC["sky"]).convert("RGB"), h=1500)
d,uri["sky"]=webp_b64(sky,82,rgb=True); open(ASSETS+"00-sky.webp","wb").write(d)

plan=[("towers",1000,80),("arch",1000,80),("garden",1000,80),
      ("fore",1000,80),("peacock",620,82),("cows",660,82)]
for name,w,q in plan:
    im=key_white(Image.open(U+SRC[name]))
    im=fit(im,w=w)
    d,uri[name]=webp_b64(im,q); open(ASSETS+f"{name}.webp","wb").write(d)

couple=fit(key_white(Image.open(U+SRC["couple"])), h=780)
d,uri["couple"]=webp_b64(couple,84); open(ASSETS+"couple.webp","wb").write(d)

for k in uri: print(k, round(len(uri[k])/1366), "KB(b64)")

# ---------------------------------------------------------------- HTML
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover"/>
<title>Sai Divya weds Sai Ramakrishna · 3 July 2026</title>
<meta name="description" content="With the blessings of Sri Venkateswara, you are graciously invited to the wedding of Sai Divya & Sai Ramakrishna — Friday, 3rd July 2026, 8:12 a.m., M.N.R. Gardens, Mancherial."/>
<meta property="og:title" content="Sai Divya weds Sai Ramakrishna"/>
<meta property="og:description" content="Friday, 3rd July 2026 · 8:12 a.m. · M.N.R. Gardens, Mancherial. We solicit your gracious presence."/>
<meta name="theme-color" content="#16271c"/>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Marcellus&family=Mukta:wght@300;400;500;600&family=Pinyon+Script&display=swap" rel="stylesheet">
<style>
:root{
 --green-deep:#16271c;--green:#284f37;--gold:#b08d3e;--gold-light:#d4af6a;--gold-bright:#ecd8a4;
 --cream:#faf5e9;--cream-deep:#f1e6cd;--paper:#fbf7ee;--ink:#22301f;--ink-soft:#4a5a48;
 --stage:clamp(320px,100vw,480px);--ease:cubic-bezier(.22,1,.36,1);
 --serif:"Cormorant Garamond",Georgia,serif;--label:"Marcellus",serif;--body:"Mukta",system-ui,sans-serif;--script:"Pinyon Script",cursive;}
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{font-family:var(--body);color:var(--ink);background:#0e1a12;overflow-x:hidden;-webkit-font-smoothing:antialiased}
.ambient{position:fixed;inset:0;z-index:0;
 background:radial-gradient(120% 80% at 85% 6%,rgba(236,216,164,.5),transparent 60%),
 radial-gradient(120% 90% at 8% 100%,rgba(40,79,55,.35),transparent 55%),
 linear-gradient(180deg,#1a2c20,#20392a 40%,#16271c)}
#petals{position:fixed;inset:0;z-index:1;pointer-events:none}
.stage{position:relative;z-index:2;width:var(--stage);margin:0 auto;background:var(--paper);
 box-shadow:0 0 80px rgba(0,0,0,.45),0 0 0 1px rgba(176,141,62,.25)}
@media(min-width:520px){.stage{margin:24px auto;border-radius:3px}}
section{position:relative;overflow:hidden}
.pad{padding:clamp(48px,11vw,70px) clamp(26px,7vw,40px)}
.reveal{opacity:0;transform:translateY(26px)}
.reveal.in{opacity:1;transform:none;transition:opacity 1.1s var(--ease),transform 1.1s var(--ease)}
.delay-1{transition-delay:.12s}.delay-2{transition-delay:.24s}.delay-3{transition-delay:.36s}
.label{font-family:var(--label);text-transform:uppercase;letter-spacing:.42em;font-size:.62rem;color:var(--gold)}
.rule{width:54px;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:18px auto}
.center{text-align:center}
.gold-text{background:linear-gradient(100deg,#9c7a30,#ecd8a4 38%,#caa44e 56%,#9c7a30 92%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;text-shadow:none}
.flourish{display:block;width:200px;max-width:62%;height:auto;margin:18px auto;color:var(--gold)}
.corner{position:absolute;width:44px;height:44px;color:var(--gold)}
.corner.tl{top:9px;left:9px}.corner.tr{top:9px;right:9px;transform:scaleX(-1)}
.corner.bl{bottom:9px;left:9px;transform:scaleY(-1)}.corner.br{bottom:9px;right:9px;transform:scale(-1)}
.stage::after{content:"";position:absolute;inset:0;z-index:60;pointer-events:none;opacity:.04;mix-blend-mode:multiply;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");background-size:140px}

/* HERO — scrollytelling: the courtyard parts, the Lords rise into the invitation */
.hero{position:relative;height:300svh;overflow:visible}
.hero-sticky{position:sticky;top:0;height:100svh;min-height:600px;overflow:hidden}
.scene{position:absolute;inset:0;z-index:0}
.layer{position:absolute;left:50%;bottom:0;transform:translateX(-50%);will-change:transform,opacity}
.layer img{display:block;width:100%;height:auto;pointer-events:none;-webkit-user-drag:none}
.l-sky{inset:0;left:0;transform:none;width:100%;height:100%;z-index:0}
.l-sky img{width:100%;height:100%;object-fit:cover;object-position:50% 30%}
.l-gopuram{width:46%;bottom:40%;z-index:1;opacity:.5;filter:blur(.6px)}
.l-arch{width:106%;bottom:30%;z-index:2}
.l-cows{left:auto;right:2%;transform:none;width:40%;bottom:17%;z-index:3}
.l-garden{width:108%;bottom:3%;z-index:4}
.l-couple{width:48%;bottom:7%;z-index:6}
.l-fore{width:108%;bottom:-20%;z-index:7}
.haze{position:absolute;inset:0;z-index:2;pointer-events:none;
 background:linear-gradient(180deg,transparent 38%,rgba(244,236,216,.30) 60%,transparent 78%)}
.cream-wash{position:absolute;inset:0;z-index:5;background:var(--paper);opacity:0;pointer-events:none}
.hero-invoc{position:absolute;top:5.5%;left:0;right:0;display:flex;justify-content:center;gap:clamp(12px,4.5vw,28px);z-index:8}
.hero-invoc span{font-family:var(--label);font-size:.58rem;letter-spacing:.28em;text-transform:uppercase;color:var(--green-deep);text-shadow:0 1px 6px rgba(255,255,255,.7)}
.hero-title{position:absolute;left:0;right:0;bottom:24%;text-align:center;z-index:8;padding:0 26px}
.hero-title::before{content:"";position:absolute;left:50%;top:48%;transform:translate(-50%,-50%);width:122%;height:160%;z-index:-1;
 background:radial-gradient(56% 50% at 50% 50%,rgba(251,247,238,.88),rgba(251,247,238,.4) 44%,transparent 72%);filter:blur(3px)}
.hero-title .emblem{width:52px;height:52px;margin:0 auto 12px;filter:drop-shadow(0 2px 8px rgba(255,255,255,.6))}
.hero-title h1{font-family:var(--serif);font-weight:500;color:var(--green-deep);line-height:1.02;font-size:clamp(2.5rem,13vw,3.6rem);text-shadow:0 2px 16px rgba(251,247,238,.85)}
.hero-title .amp{display:block;font-family:var(--script);font-size:.62em;margin:.02em 0;line-height:1}
.hero-title .hero-tagline{margin-top:12px;font-family:var(--script);font-size:clamp(1.5rem,7vw,2rem);color:var(--gold);line-height:1;text-shadow:0 1px 8px rgba(255,255,255,.6)}
.hero-title .when{margin-top:14px;font-family:var(--label);letter-spacing:.26em;text-transform:uppercase;font-size:.64rem;color:var(--ink-soft);text-shadow:0 1px 8px rgba(255,255,255,.7)}
.scrollcue{position:absolute;left:50%;bottom:20px;transform:translateX(-50%);z-index:9;opacity:.55}
.scrollcue i{position:relative;display:block;width:1px;height:42px;background:rgba(176,141,62,.32);overflow:hidden}
.scrollcue i::after{content:"";position:absolute;left:-1.5px;top:0;width:4px;height:4px;border-radius:50%;background:var(--gold);animation:cuedot 2.6s var(--ease) infinite}
@keyframes cuedot{0%{transform:translateY(-8px);opacity:0}25%{opacity:1}90%{opacity:.6}100%{transform:translateY(42px);opacity:0}}

/* INVITATION */
.invite{background:linear-gradient(180deg,var(--paper),var(--cream-deep));padding:clamp(40px,9vw,58px) clamp(16px,4.5vw,26px)}
.invite-card{position:relative;isolation:isolate;border:1px solid rgba(176,141,62,.45);padding:clamp(46px,11vw,66px) clamp(24px,6vw,34px);text-align:center;overflow:hidden;background:rgba(255,253,247,.45)}
.invite-card::before{content:"";position:absolute;inset:8px;border:1px solid rgba(176,141,62,.2);pointer-events:none}
.invite-watermark{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:90%;max-width:280px;height:auto;opacity:.07;pointer-events:none;z-index:-1}
.invite-copy{font-family:var(--serif);font-size:clamp(1.32rem,5.6vw,1.62rem);line-height:1.75;color:var(--ink);max-width:28ch;margin:0 auto}
.bride-pre{display:block;margin-top:24px;font-family:var(--label);letter-spacing:.3em;text-transform:uppercase;font-size:.6rem;color:var(--gold)}
.bride-name{font-family:var(--serif);font-weight:600;font-size:clamp(2.1rem,9vw,2.9rem);line-height:1.12;text-wrap:balance;margin-top:8px;padding-bottom:.08em}

/* UNION */
.union{background:linear-gradient(180deg,var(--cream-deep),var(--paper));text-align:center}
.name-block{margin:0 auto;max-width:30ch}
.pre{display:block;font-family:var(--label);letter-spacing:.24em;text-transform:uppercase;font-size:.6rem;color:var(--gold);margin-bottom:8px}
.big{font-family:var(--serif);font-size:clamp(2rem,8.5vw,2.7rem);font-weight:500;line-height:1.14;text-wrap:balance;color:var(--green-deep)}
.sub{display:block;font-size:.92rem;color:var(--ink-soft);font-style:italic;margin-top:12px;line-height:1.6;font-family:var(--serif)}
.knot{margin:30px auto;width:72px;height:72px}
.knot svg{width:100%;height:100%;display:block}
.union-emblem{display:block;width:54px;height:54px;margin:8px auto 0}

/* MUHURTHAM */
.muhurtham{background:linear-gradient(180deg,var(--green),var(--green-deep));color:var(--cream)}
.muhurtham .label{color:var(--gold-light)}
.muhurtham .rule{background:linear-gradient(90deg,transparent,var(--gold-light),transparent)}
.date-hero{text-align:center;font-family:var(--serif);margin:6px 0 2px}
.date-hero .d{font-size:clamp(3.4rem,18vw,5rem);font-weight:500;line-height:.9;color:var(--gold-bright)}
.date-hero .m{font-family:var(--label);letter-spacing:.3em;text-transform:uppercase;font-size:.78rem;margin-top:10px;color:var(--cream)}
.time-line{text-align:center;font-family:var(--serif);font-style:italic;font-size:1.5rem;color:var(--gold-light);margin-top:14px}
.stars{text-align:center;font-family:var(--label);letter-spacing:.16em;font-size:.74rem;color:rgba(250,245,233,.78);margin-top:16px;line-height:2}
.countdown{display:flex;justify-content:center;gap:clamp(8px,3.5vw,18px);margin-top:38px}
.cd{text-align:center;min-width:50px}
.cd b{display:block;font-family:var(--serif);font-size:clamp(2rem,9vw,2.6rem);font-weight:500;color:var(--gold-bright);font-variant-numeric:tabular-nums;line-height:1}
.cd span{font-family:var(--label);letter-spacing:.16em;text-transform:uppercase;font-size:.5rem;color:rgba(250,245,233,.65);margin-top:8px;display:block}
.cd-sep{font-family:var(--serif);font-size:1.5rem;color:var(--gold);margin-top:.1em}

/* VENUE */
.venue{background:var(--paper);text-align:center}
.venue h3{font-family:var(--serif);font-size:clamp(2rem,9vw,2.5rem);color:var(--green-deep);font-weight:500;margin:4px 0 6px}
.venue address{font-style:normal;font-size:1rem;line-height:1.9;color:var(--ink-soft)}
.lunch{font-family:var(--serif);font-style:italic;font-size:1.2rem;color:var(--gold);margin-top:18px}
.actions{display:flex;flex-direction:column;gap:12px;margin-top:30px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;font-family:var(--label);letter-spacing:.16em;
 text-transform:uppercase;font-size:.66rem;padding:15px 22px;border:1px solid var(--gold);color:var(--green-deep);
 background:transparent;text-decoration:none;border-radius:2px;transition:all .5s var(--ease);cursor:pointer}
.btn:hover{background:var(--green-deep);color:var(--gold-bright);border-color:var(--green-deep)}
.btn.solid{background:var(--green-deep);color:var(--gold-bright)}.btn.solid:hover{background:var(--green);border-color:var(--green)}
.btn svg{width:15px;height:15px}

/* HOSTS */
.hosts{background:linear-gradient(180deg,var(--cream-deep),var(--paper));text-align:center}
.host-grp+.host-grp{margin-top:28px}
.role{font-family:var(--label);letter-spacing:.24em;text-transform:uppercase;font-size:.58rem;color:var(--gold);margin-bottom:10px}
.nm{font-family:var(--serif);font-size:clamp(1.3rem,6vw,1.7rem);color:var(--green-deep);line-height:1.4}

/* BENEDICTION (footer) */
.bene{background:linear-gradient(180deg,var(--green-deep),#0f1c14);color:var(--cream);text-align:center;padding-bottom:50px}
.bene .flourish{color:var(--gold-light);margin:0 auto 20px}
.bene .label{color:var(--gold-light)}
.bene .from{font-family:var(--serif);font-weight:600;font-size:clamp(1.7rem,8vw,2.2rem);margin-top:8px}
.bene-cows{display:block;width:150px;height:auto;margin:26px auto 2px;opacity:.95;filter:drop-shadow(0 8px 18px rgba(0,0,0,.3))}
.bene .sig{margin-top:22px;font-family:var(--label);letter-spacing:.2em;font-size:.55rem;text-transform:uppercase;color:rgba(236,216,164,.5)}
.credit{display:inline-block;margin-top:20px;font-family:var(--label);letter-spacing:.2em;text-transform:uppercase;font-size:.56rem;color:var(--gold-light);text-decoration:none;border-bottom:1px solid transparent;transition:border-color .4s var(--ease)}
.credit:hover{border-color:var(--gold-light)}

@media(prefers-reduced-motion:reduce){
 .reveal{opacity:1;transform:none;transition:none}.scrollcue i{animation:none}
 .hero{height:100svh}.cream-wash{display:none}
 .layer{transform:translateX(-50%)!important}.l-sky,.l-cows{transform:none!important}}
</style>
</head>
<body>
<div class="ambient"></div>
<canvas id="petals"></canvas>
<main class="stage">

 <!-- 1 · HERO — the courtyard parts, the Lords rise into the invitation -->
 <section class="hero" id="hero">
  <div class="hero-sticky">
   <div class="scene">
    <div class="layer l-sky"><img src="__SKY__" alt=""></div>
    <div class="layer l-gopuram"><img src="__TOWERS__" alt=""></div>
    <div class="layer l-arch"><img src="__ARCH__" alt=""></div>
    <div class="layer l-cows"><img src="__COWS__" alt=""></div>
    <div class="layer l-garden"><img src="__GARDEN__" alt=""></div>
    <div class="layer l-couple"><img src="__COUPLE__" alt="Lord Venkateswara and Goddess Padmavati"></div>
    <div class="layer l-fore"><img src="__FORE__" alt=""></div>
    <div class="haze"></div>
    <div class="cream-wash"></div>
   </div>
   <div class="hero-invoc"><span>Srirasthu</span><span>Shubhamasthu</span><span>Avighnamasthu</span></div>
   <div class="hero-title">
    <h1 class="gold-text">Sai Divya<span class="amp">weds</span>Sai Ramakrishna</h1>
    <div class="when">Friday · 3<sup>rd</sup> July 2026</div>
    <div class="hero-tagline">we invite you to share in our joy</div>
   </div>
   <div class="scrollcue"><i></i></div>
  </div>
 </section>

 <!-- 2 · INVITATION -->
 <section class="invite">
  <div class="invite-card reveal">
   <img class="invite-watermark" src="__PEACOCK__" alt="" aria-hidden="true">
   <svg class="corner tl" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M1 39V11Q1 1 11 1H39" stroke="currentColor" stroke-width="1"/></svg>
   <svg class="corner tr" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M1 39V11Q1 1 11 1H39" stroke="currentColor" stroke-width="1"/></svg>
   <svg class="corner bl" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M1 39V11Q1 1 11 1H39" stroke="currentColor" stroke-width="1"/></svg>
   <svg class="corner br" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M1 39V11Q1 1 11 1H39" stroke="currentColor" stroke-width="1"/></svg>
   <span class="label">With the blessings of Sri Venkateswara</span>
   <svg class="flourish" viewBox="0 0 240 18" fill="none" aria-hidden="true"><g stroke="currentColor" stroke-width="1" stroke-linecap="round"><path d="M40 9H98"/><path d="M142 9H200"/></g><g fill="currentColor"><path d="M98 9q7-6 13 0q-7 6-13 0Z"/><path d="M142 9q-7-6-13 0q7 6 13 0Z"/><circle cx="120" cy="9" r="3"/><circle cx="34" cy="9" r="1.6"/><circle cx="206" cy="9" r="1.6"/></g><circle cx="120" cy="9" r="6.5" stroke="currentColor" stroke-width="1" fill="none"/></svg>
   <p class="invite-copy">We solicit your gracious presence with family &amp; friends on the auspicious occasion of the marriage of our youngest daughter</p>
   <span class="bride-pre">Chi · La · Sow</span>
   <div class="bride-name gold-text">Sai Divya</div>
  </div>
 </section>

 <!-- 3 · UNION -->
 <section class="union pad center" id="union">
  <span class="label reveal">United in matrimony</span>
  <svg class="union-emblem reveal delay-1" viewBox="0 0 64 64" fill="none" aria-hidden="true">
   <circle cx="32" cy="32" r="30" stroke="#b08d3e" stroke-width="1"/><circle cx="32" cy="32" r="21" stroke="#b08d3e" stroke-width=".6" opacity=".55"/>
   <path d="M32 13q9.5 9.5 0 19q-9.5-9.5 0-19Z" fill="#caa44e"/><path d="M32 51q9.5-9.5 0-19q-9.5 9.5 0 19Z" fill="#caa44e"/>
   <path d="M13 32q9.5-9.5 19 0q-9.5 9.5-19 0Z" fill="#caa44e" opacity=".85"/><path d="M51 32q-9.5-9.5-19 0q9.5 9.5 19 0Z" fill="#caa44e" opacity=".85"/>
   <circle cx="32" cy="32" r="3.2" fill="#b08d3e"/></svg>
  <div class="name-block groom reveal delay-1" style="margin-top:24px"><span class="pre">With</span><span class="big">Sai Ramakrishna</span>
   <span class="sub">Son of Smt. &amp; Sri Chinthala Sukrutha — Ramesh Babu, Mancherial</span></div>
 </section>

 <!-- 4 · SUMUHURTHAM -->
 <section class="muhurtham pad" id="muhurtham">
  <div class="center"><span class="label reveal">Sumuhurtham</span><div class="rule reveal delay-1"></div></div>
  <div class="date-hero reveal delay-1"><div class="d">03</div><div class="m">July 2026 · Friday</div></div>
  <div class="time-line reveal delay-2">at 8:12 in the morning</div>
  <div class="stars reveal delay-2">Shravana Nakshatram<br>Karkataka Lagnam</div>
  <div class="countdown reveal delay-3" id="countdown">
   <div class="cd"><b id="cd-d">--</b><span>Days</span></div><div class="cd-sep">:</div>
   <div class="cd"><b id="cd-h">--</b><span>Hours</span></div><div class="cd-sep">:</div>
   <div class="cd"><b id="cd-m">--</b><span>Min</span></div><div class="cd-sep">:</div>
   <div class="cd"><b id="cd-s">--</b><span>Sec</span></div></div>
 </section>

 <!-- 5 · VENUE -->
 <section class="venue pad">
  <span class="label reveal">The Gathering</span>
  <h3 class="reveal delay-1">M.N.R. Gardens</h3>
  <address class="reveal delay-1">Kyathanpally 'X' Road,<br>Gadderagadi, Mancherial.</address>
  <div class="lunch reveal delay-2">Lunch follows..</div>
  <div class="actions reveal delay-2">
   <a class="btn solid" id="directions" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 21s-7-6.3-7-11a7 7 0 1 1 14 0c0 4.7-7 11-7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>Get Directions</a>
   <a class="btn" id="addcal" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 9h16M8 3v4M16 3v4"/></svg>Add to Calendar</a></div>
 </section>

 <!-- 6 · HOSTS -->
 <section class="hosts pad">
  <span class="label reveal" style="display:block;margin-bottom:30px">With warm regards</span>
  <div class="host-grp reveal delay-1"><div class="role">Invited by</div><div class="nm">Smt. &amp; Sri Allakula Jyothi — Thirupathi</div></div>
  <div class="host-grp reveal delay-2"><div class="role">Co-invited by</div><div class="nm">Smt. &amp; Sri Pothurajula Sai Deepthi — Praveen</div></div>
 </section>

 <!-- 7 · BENEDICTION (footer) -->
 <section class="bene pad">
  <svg class="flourish reveal" viewBox="0 0 240 18" fill="none" aria-hidden="true"><g stroke="currentColor" stroke-width="1" stroke-linecap="round"><path d="M40 9H98"/><path d="M142 9H200"/></g><g fill="currentColor"><path d="M98 9q7-6 13 0q-7 6-13 0Z"/><path d="M142 9q-7-6-13 0q7 6 13 0Z"/><circle cx="120" cy="9" r="3"/></g><circle cx="120" cy="9" r="6.5" stroke="currentColor" stroke-width="1" fill="none"/></svg>
  <span class="label reveal delay-1">With best compliments from</span>
  <div class="from gold-text reveal delay-1">Near &amp; Dear</div>
  <img class="bene-cows reveal delay-2" src="__COWS__" alt="" aria-hidden="true">
  <div class="sig reveal delay-2">Sai Divya &amp; Sai Ramakrishna · 03·07·2026</div>
  <a class="credit reveal delay-2" href="https://purplehatevents.in" target="_blank" rel="noopener">Designed by PurpleHat Events</a>
 </section>

</main>

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lenis/1.0.42/lenis.min.js"></script>
<script>
(function(){
 var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
 var lenis=null;
 if(window.Lenis&&!reduce){lenis=new Lenis({lerp:.08,wheelMultiplier:1,touchMultiplier:1.6,smoothWheel:true});(function raf(t){lenis.raf(t);requestAnimationFrame(raf);})();}

 var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.16,rootMargin:'0px 0px -8% 0px'});
 document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});

 if(window.gsap&&window.ScrollTrigger&&!reduce){
  gsap.registerPlugin(ScrollTrigger);
  if(lenis){lenis.on('scroll',ScrollTrigger.update);gsap.ticker.add(function(t){lenis.raf(t*1000);});gsap.ticker.lagSmoothing(0);}

  /* keep centered planes centred while GSAP drives transforms */
  gsap.set('.l-gopuram,.l-arch,.l-garden,.l-couple,.l-fore',{xPercent:-50});
  gsap.set('.hero-title',{opacity:0,y:30});
  gsap.set('.hero-invoc',{opacity:0,y:-10});

  /* SIGNATURE — pinned: the courtyard parts and the Lords rise into the invitation */
  var htl=gsap.timeline({defaults:{ease:'none'},scrollTrigger:{trigger:'#hero',start:'top top',end:'bottom bottom',scrub:.7}});
  htl.to('.hero-invoc',{opacity:1,y:0,duration:.12,ease:'power2.out'},0)
     /* phase 1 — parallax drift, depth becomes visible */
     .to('.l-sky img',{yPercent:-7,scale:1.06,duration:.55},0)
     .to('.l-gopuram',{yPercent:-5,duration:.55},0)
     .to('.l-arch',{yPercent:-4,duration:.55},0)
     .to('.l-cows',{yPercent:6,duration:.55},0)
     .to('.l-garden',{yPercent:10,duration:.55},0)
     .to('.l-fore',{yPercent:20,duration:.55},0)
     .to('.l-couple',{yPercent:-3,duration:.42},0)
     .to('.scrollcue',{opacity:0,duration:.12},.05)
     /* phase 2 — courtyard parts & fades, couple rises and scales, cream fades in */
     .to('.l-arch',{yPercent:-38,opacity:0,duration:.5,ease:'power1.in'},.42)
     .to('.l-gopuram',{yPercent:-26,opacity:0,duration:.5,ease:'power1.in'},.42)
     .to('.l-cows',{yPercent:40,opacity:0,duration:.5,ease:'power1.in'},.42)
     .to('.l-garden',{yPercent:52,opacity:0,duration:.5,ease:'power1.in'},.42)
     .to('.l-fore',{yPercent:78,opacity:0,duration:.5,ease:'power1.in'},.42)
     .to('.l-sky img',{opacity:0,duration:.42},.5)
     .to('.cream-wash',{opacity:1,duration:.42},.5)
     .to('.l-couple',{yPercent:-86,scale:.58,duration:.62,ease:'power2.inOut'},.4)
     /* phase 3 — names settle beneath the risen Lords */
     .to('.hero-title',{opacity:1,y:0,duration:.3,ease:'power2.out'},.74);
 }

 /* countdown to 3 Jul 2026 08:12 IST */
 var T=new Date('2026-07-03T08:12:00+05:30').getTime(),E=function(i){return document.getElementById(i);},P=function(n){return(n<10?'0':'')+n;};
 (function tick(){var x=T-Date.now();if(x<0)x=0;
  E('cd-d').textContent=P(Math.floor(x/864e5));E('cd-h').textContent=P(Math.floor(x%864e5/36e5));
  E('cd-m').textContent=P(Math.floor(x%36e5/6e4));E('cd-s').textContent=P(Math.floor(x%6e4/1e3));setTimeout(tick,1000);})();

 var q=encodeURIComponent('M.N.R. Gardens, Kyathanpally X Road, Mancherial, Telangana');
 E('directions').href='https://www.google.com/maps/search/?api=1&query='+q;
 E('addcal').href='https://calendar.google.com/calendar/render?action=TEMPLATE&text='+encodeURIComponent('Sai Divya weds Sai Ramakrishna')+'&dates=20260703T081200/20260703T120000&ctz=Asia/Kolkata&location='+q+'&details='+encodeURIComponent('Shravana Nakshatram, Karkataka Lagnam. Lunch follows. With love from Near & Dear.');

 /* subtle petal-fall */
 if(!reduce){(function(){var c=document.getElementById('petals'),x=c.getContext('2d'),W,H,P=[];
  function S(){W=c.width=innerWidth;H=c.height=innerHeight;}S();addEventListener('resize',S);
  var N=innerWidth<560?12:20,C=['#ecb9c7','#f3d9e2','#e8cf95','#d4af6a'];
  function mk(i){return{x:Math.random()*W,y:Math.random()*-H,r:3+Math.random()*4,s:.25+Math.random()*.5,
   a:Math.random()*6.28,sw:.4+Math.random()*.6,c:C[i%C.length],o:.32+Math.random()*.4};}
  for(var i=0;i<N;i++)P.push(mk(i));
  (function d(){x.clearRect(0,0,W,H);for(var i=0;i<P.length;i++){var p=P[i];p.y+=p.s;p.a+=.01;p.x+=Math.sin(p.a)*p.sw;
   if(p.y>H+10){P[i]=mk(i);P[i].y=-10;}x.globalAlpha=p.o;x.fillStyle=p.c;x.beginPath();x.ellipse(p.x,p.y,p.r,p.r*1.7,p.a,0,7);x.fill();}
   requestAnimationFrame(d);})();})();}
})();
</script>
</body>
</html>"""

for k,v in uri.items():
    HTML = HTML.replace("__"+k.upper()+"__", v)

open(OUT+"index.html","w").write(HTML)
print("HTML bytes:", round(len(HTML)/1024), "KB")
