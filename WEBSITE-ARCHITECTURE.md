# 🌐 AgentBrake — Website-Architektur

*Bauplan für die Landing Page & Website. In Claude Code kannst du daraus
die echte Seite bauen lassen (z.B. mit dem frontend-design-Skill).*

---

## Wichtig: Reihenfolge

Die Website kommt NACH GitHub/PyPI und den ersten Communities (siehe GO-TO-MARKET.md).
Ein Entwickler-Tool braucht zuerst Code-Traktion. Aber: Eine einfache Landing
Page solltest du früh haben, weil du sie überall verlinkst (HN, Reddit, X).

**Für den Start reicht EINE Seite.** Die volle Struktur unten ist das Ziel,
nicht der Tag-1-Umfang.

---

## Site-Typ

Hybrid: Open-Source-Dev-Tool. Die Website hat zwei Jobs:
1. In 5 Sekunden erklären, was es tut (für HN/Reddit-Besucher).
2. Zum `pip install` und GitHub-Stern führen (Conversion = Install + Star).

Später ein dritter Job: die bezahlte Cloud-Version verkaufen.

---

## Seitenhierarchie (Zielzustand)

```
Homepage (/)                          ← Tag 1: nur diese Seite
├── Docs (/docs)                      ← Tag 1 light: README reicht erst
│   ├── Quickstart (/docs/quickstart)
│   ├── LangChain (/docs/langchain)
│   ├── CrewAI (/docs/crewai)
│   └── Configuration (/docs/config)
├── Pricing (/pricing)               ← erst wenn bezahlte Version existiert
├── Blog (/blog)                     ← für die Erfahrungs-Posts aus GTM Phase 3
│   └── [Posts] (/blog/slug)
└── GitHub (extern → Repo)
```

## Tag-1-Landing-Page: Abschnitte (von oben nach unten)

| # | Abschnitt | Inhalt |
|---|-----------|--------|
| 1 | **Hero** | Headline + der Install-Befehl + zwei Buttons |
| 2 | **Das Problem** | Die 47k-Story, kurz & konkret |
| 3 | **Die Lösung (Demo)** | Das Demo-GIF — der Aha-Moment |
| 4 | **So einfach ist es** | Der 1-Zeilen-Code-Block (LangChain + CrewAI Tab) |
| 5 | **Was es fängt** | Die Tabelle der Runaway-Typen aus der README |
| 6 | **Social Proof** | GitHub-Stars, Download-Zahl, später Testimonials |
| 7 | **Footer** | GitHub, Docs, PyPI, Lizenz |

### Hero-Texte (fertig zum Verwenden)

**Headline:** „Stop runaway AI agents before they burn your budget."
**Subheadline:** „AgentBrake is the emergency brake for LangChain & CrewAI.
One line of code stops infinite loops, cost blowouts, and endless reasoning —
in real time, before the next expensive call goes out."

**Primärer Button:** `pip install agentbrake-sdk` (zum Kopieren)
**Sekundärer Button:** „Star on GitHub ⭐"

---

## Navigation

**Header (4 Items + CTA):**
`Logo` · Docs · Pricing · Blog · **[GitHub ⭐]** (rechts, als CTA-Button)

**Footer (4 Spalten):**
- **Product:** Features, Pricing, Changelog
- **Docs:** Quickstart, LangChain, CrewAI, Config
- **Community:** GitHub, Discord, X/Twitter
- **Legal:** License (MIT), Privacy

---

## URL- & Tech-Empfehlung

- Domain-Vorschlag: `agentbrake.dev` (`.dev` signalisiert Dev-Tool; im pyproject schon eingetragen).
- Für Tag 1: eine statische Seite reicht völlig (HTML/CSS, oder ein Framework
  deiner Wahl). Hosten kostenlos auf Vercel oder GitHub Pages.
- Docs später mit einem Doc-Tool (z.B. Mintlify, Docusaurus) — aber erst, wenn nötig.

---

## Conversion-Ziel

Die Seite hat EIN Hauptziel: **Besucher → `pip install` + GitHub-Star.**
Nicht E-Mail sammeln, nicht „Demo buchen". Bei einem Dev-Tool ist der Install
die Conversion. Mach den Install-Befehl unübersehbar und 1-Klick-kopierbar.

---

## Was die neue Session bauen kann

In Claude Code: „Bau mir aus WEBSITE-ARCHITECTURE.md die Tag-1-Landing-Page
als eine HTML-Datei mit dem frontend-design-Skill, dunkles Dev-Tool-Design,
der Install-Befehl prominent zum Kopieren." → fertige Seite zum Deployen.
