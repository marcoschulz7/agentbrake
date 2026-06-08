# 📋 AgentBrake — Projekt-Kontext & Übergabe

*Dies ist der Übergabe-Brief. In Claude Code als Erstes lesen lassen, dann ist die neue Session sofort im Bild.*

---

## Was ist das hier?

**AgentBrake** — die Notbremse für Multi-Agenten-Systeme. Ein Python-Paket, das
Runaway-Loops in **LangChain** und **CrewAI** in Echtzeit stoppt, bevor aus
50 Cent ein 47.000-Dollar-Loop wird.

Das Produkt **existiert und funktioniert bereits** — es ist kein Konzept.
Es ist gegen die echten Libs verifiziert: CrewAI 1.14.6 und LangChain 1.3
(inkl. eines No-Key-Beispiels, das einen echten LangGraph-Loop bremst).

## Die Geschäftsidee in einem Satz

Solo-Entwickler-Produkt in einer brandneuen, noch nicht dominierten Nische
(Agenten-Kostenkontrolle). Open-Source-Kern (MIT) für Verbreitung, später
bezahlte Cloud-/Team-Version für Umsatz. Langfristiges Ziel: Übernahme durch
einen großen Player (Datadog, LangChain Inc., ein Hyperscaler) oder profitabler
SaaS.

## Warum diese Nische (Recherche-Ergebnis, Stand Juni 2026)

- Markt explodiert: LLM-API-Ausgaben haben sich 2024→2025 verdoppelt (3,5 → 8,4 Mrd. $).
- Schmerz ist real & teuer dokumentiert: ein LangChain-Loop kostete real $47.000 über 11 Tage.
- CrewAI: 12 Mio. Agenten-Läufe/Tag in Produktion. LangChain: 50.000+ Produktions-Apps.
- Die Lücke: Bestehende Tools **loggen** Loops, sie **stoppen** sie nicht in Echtzeit.
  AgentBrake greift ein statt nur zu beobachten.
- Konkurrenz existiert (Magicrails, Waxell, Galileo), aber niemand besitzt die
  Position „*die* LangChain/CrewAI-Notbremse" eindeutig. Markt ist erst Wochen alt.

## Was schon gebaut ist

| Datei | Inhalt | Status |
|-------|--------|--------|
| `src/agentbrake/__init__.py` | Öffentliche API (Exports), Package-Einstieg | ✅ |
| `src/agentbrake/core.py` | Framework-neutrale Engine: Loop-Detektor, Budget-Tracker, Preis-Tabelle | ✅ getestet (14 Tests) |
| `src/agentbrake/langchain.py` | **Zwei** Integrationen: `LangChainBrake` (Callback, klassisches 0.x) + `LangChainBrakeMiddleware` (1.x / LangGraph) | ✅ Unit-Tests + echte Integrationstests gegen LangChain **1.3** |
| `src/agentbrake/crewai.py` | CrewAI-Adapter via Monkey-Patching | ✅ gegen echtes CrewAI **1.14.6** verifiziert & repariert — siehe Hinweis unten |
| `tests/` | Engine + LangChain (Unit + Middleware-Integration) + CrewAI | ✅ **grün** — 20 ohne Frameworks, 22 mit LangChain, 26 mit CrewAI; nicht-installierte Pfade skippen sauber |
| `pyproject.toml` | Packaging (hatchling, src-Layout) + pytest-Config | ✅ Wheel baut, `pip install -e .` läuft |
| `README.md` | Doku + Verkaufstext | ✅ aktualisiert (1.x-Middleware vs. 0.x-Callback) |
| `examples/` | `langchain_quickstart.py` (läuft **ohne API-Key**), `crewai_quickstart.py` (braucht Key), `README.md` | ✅ |

### ⚠️ Wichtiger Hinweis zum LangChain-Adapter (Stand 1.x)

LangChain 1.x hat die Agenten-Architektur auf `create_agent` / LangGraph
umgebaut. Zwei Konsequenzen, die den Adapter direkt betreffen:

- **Callbacks können nicht mehr bremsen.** In LangGraph laufen Callback-Handler
  als Beobachter; eine Exception aus einem Callback wird **geloggt und
  verschluckt**, der Lauf geht weiter. Der klassische `LangChainBrake`-Callback
  funktioniert daher nur noch beim alten `AgentExecutor` (0.x).
- **Für 1.x gibt es `LangChainBrakeMiddleware`.** Middleware läuft *im*
  Ausführungsgraphen (`wrap_tool_call` / `wrap_model_call`), eine Exception
  daraus stoppt den Lauf wirklich. Verifiziert: das No-Key-Beispiel bremst einen
  echten LangGraph-Loop bei Step 3.

**Faustregel:** 1.x (`create_agent`) → `LangChainBrakeMiddleware`. Klassischer
`AgentExecutor` (0.x) → `LangChainBrake`-Callback.

### ⚠️ Wichtiger Hinweis zum CrewAI-Adapter (Stand 1.x)

CrewAI 1.x hat die interne Architektur umgebaut: `LLM(...)` ist jetzt eine
**Factory**, die provider-spezifische Subklassen (`OpenAICompletion`, …)
zurückgibt — das alte Patchen von `LLM.call` lief ins Leere. Der Adapter wurde
darauf umgebaut: er patcht jetzt **jede Provider-Klasse mit eigenem `call()`**
(plus `ToolUsage._use`). Was man wissen muss:

- **Loop-/Step-/Tool-/Duration-Limits** greifen zuverlässig (über `ToolUsage._use`).
- **Cost-Limit** ist so genau, wie der Provider seine Tokens meldet
  (`_token_usage`); ohne gemeldete Tokens fällt der Adapter auf eine grobe
  Längen-Schätzung zurück.
- `install()` muss **nach** dem Bauen der Agenten/LLMs laufen (CrewAI lädt
  Provider lazy) — am besten direkt vor `crew.kickoff()`.
- **Live verifiziert (0.1.1):** ein echter Crew-Lauf gegen OpenAI hat bestätigt,
  dass die Bremse `crew.kickoff()` wirklich stoppt und echte Tokens/Kosten trackt.
  Der Live-Lauf deckte auf, dass CrewAI Exceptions per `except Exception` schluckt
  → `AgentBrakeError` ist jetzt eine `BaseException` (Kill-Switch), die kein
  Framework-Handler fangen kann. Abgesichert durch einen Offline-`kickoff()`-Test.

## Die offenen nächsten Schritte (Priorität von oben)

1. **Launchen.** Alles steht (live auf PyPI 0.1.1 + GitHub, Demo-GIF, Launch-Texte
   in `LAUNCH-POSTS.md`). Show HN posten (Di–Do ~17:00 dt.), dann r/LangChain +
   X-Thread, und auf **jeden** Kommentar antworten. Das ist der nächste echte Schritt.
2. **Go-to-Market vertiefen.** Siehe `GO-TO-MARKET.md` — Testimonials sammeln,
   Erfahrungs-Post, Product Hunt (erst mit GitHub-Traktion).
3. **Landing Page bauen.** Siehe `WEBSITE-ARCHITECTURE.md` — bewusst *nach* der
   ersten Verbreitung.

**Erledigt (Juni 2026):** Packaging zu echtem `src/agentbrake`-Paket umgebaut
(`__init__.py`, Wheel baut, `pip install -e .` läuft) · Testsuite neu von Null
geschrieben · CrewAI-Adapter gegen echtes CrewAI 1.14.6 verifiziert und auf die
neue Provider-Factory-Architektur repariert · LangChain-1.x-Lücke gefunden
(Callbacks bremsen in LangGraph nicht mehr) und mit `LangChainBrakeMiddleware`
geschlossen — bremst nachweislich einen echten LangGraph-Loop ohne API-Key ·
Examples für beide Frameworks · **live auf PyPI (`agentbrake-sdk`) + GitHub
veröffentlicht** · Demo-GIF + Launch-Texte erstellt · **0.1.1:** Live-Lauf deckte
auf, dass CrewAI die Bremse verschluckte → mit `BaseException`-Kill-Switch gefixt,
end-to-end live gegen OpenAI verifiziert.

## Arbeitsweise mit Marco (für Claude in der neuen Session)

- Marco kommuniziert auf Deutsch (informell).
- Marco will so wenig wie möglich selbst machen — Claude agiert als technischer
  Co-Founder und trifft Entscheidungen, statt viele Fragen zu stellen.
- Marco schätzt Ehrlichkeit über Schönfärberei: echte Vorbehalte nennen
  (z.B. „CrewAI-Cost-Limit hängt davon ab, dass der Provider Tokens meldet"),
  nicht verstecken.
- Iterativ arbeiten: erste Version ist Startpunkt, nicht Endprodukt.

## Wichtiger realistischer Rahmen

Große Firmen kaufen selten reine Ideen oder frühe Tools. Was zählt, ist
**Traction**: echte Nutzer, GitHub-Stars, Downloads. Der Plan ist deshalb:
erst Verbreitung über Open Source + Communities, dann Umsatz, dann ggf. Exit.
Das ist ein Monate-bis-Jahre-Weg, kein Schnellschuss — ehrlich eingeordnet.
