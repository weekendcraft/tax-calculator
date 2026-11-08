#!/usr/bin/env python3
"""Split static content out of index.html into guide.html."""
import json, re

html = open('/tmp/sg-tax/index.html').read()

# extract content block between exact markers
start = html.index('<div class="content">')
end = html.index('<div class="disclaimer">')
content = html[start:end].rstrip()
html = html[:start] + html[end:]

# index JSON-LD: keep WebApplication only
m = re.search(r'  <script type="application/ld\+json">([\s\S]*?)</script>', html)
ld = json.loads(m.group(1))
webapp = [g for g in ld['@graph'] if g['@type'] == 'WebApplication']
html = html.replace(m.group(0), '  <script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": webapp}, ensure_ascii=False) + '</script>')

# discreet guide link above disclaimer
html = html.replace('  <div class="disclaimer">', '  <div class="fb"><a href="./guide.html">\U0001F4C4 Tax rates, rules &amp; FAQ</a></div>\n\n  <div class="disclaimer">')

# build guide.html
style = re.search(r'<style>([\s\S]*?)</style>', html).group(1)
faq = [g for g in ld['@graph'] if g['@type'] == 'FAQPage']
faq_ld = json.dumps({"@context": "https://schema.org", "@graph": faq}, ensure_ascii=False)
back = '  <div class="fb"><a href="./">\U0001F9EE Open the calculator</a></div>\n'
fb = '  <div class="fb"><a href="https://docs.google.com/forms/d/e/1FAIpQLSeJ4P2Ch76kIHVl6KZBA1MNx8pil4kZ32nLrQDQLr8oKQllVg/viewform?usp=pp_url&amp;entry.267710623=tax-calculator" target="_blank" rel="noopener">\U0001F4AC Send feedback</a></div>'
guide = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#059669">
<meta name="description" content="Income tax rates and rules for Singapore (IRAS YA2027), Indonesia (PPh 21 UU HPP) and Malaysia (LHDN): progressive brackets, PTKP, CPF/EPF reliefs, dependant reliefs and worked examples.">
<meta property="og:title" content="Income tax rates &amp; FAQ — Singapore, Indonesia, Malaysia">
<meta property="og:description" content="Official bracket tables, residency rules, reliefs and worked examples for SG/ID/MY personal income tax.">
<meta property="og:type" content="article">
<title>Income tax rates &amp; FAQ — SG · ID · MY</title>
  <style>{style}</style>
  <script type="application/ld+json">{faq_ld}</script>
</head>
<body>
  <h1>Income tax rates &amp; FAQ — \U0001F1F8\U0001F1EC \U0001F1EE\U0001F1E9 \U0001F1F2\U0001F3BE</h1>
{back}
{content}
{back}
{fb}
</body>
</html>
'''
open('/tmp/sg-tax/guide.html', 'w').write(guide)

# sitemap + robots
open('/tmp/sg-tax/sitemap.xml', 'w').write('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://weekendcraft.github.io/tax-calculator/</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>
  <url><loc>https://weekendcraft.github.io/tax-calculator/guide.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
</urlset>
''')
open('/tmp/sg-tax/robots.txt', 'w').write('User-agent: *\nAllow: /\n\nSitemap: https://weekendcraft.github.io/tax-calculator/sitemap.xml\n')

# service worker: add guide, bump version
sw = open('/tmp/sg-tax/sw.js').read().replace('tax-v5', 'tax-v6').replace("'./index.html', './manifest.json'", "'./index.html', './guide.html', './manifest.json'")
open('/tmp/sg-tax/sw.js', 'w').write(sw)

assert '<div class="content">' not in html, 'content still in index!'
open('/tmp/sg-tax/index.html', 'w').write(html)
print('split OK: index', len(html), 'bytes | guide', len(guide), 'bytes')
