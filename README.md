# GOLEM — Tanakh Recovery Platform

[![Deploy](https://github.com/ortamy/golem/actions/workflows/deploy.yml/badge.svg)](https://github.com/ortamy/golem/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Website](https://img.shields.io/badge/website-ortamy.github.io%2Fgolem-8b5cf6)](https://ortamy.github.io/golem)

Golem is a research platform for recovering the original meaning of the Tanakh through Paleo-Hebrew, Proto-Canaanite, and Phoenician scripts, three-letter roots, and systematic exposure of Greco-Latin substitutions introduced in translations. Not a religion. Not a congregation. A forensic linguistics project.

---

## Key Features

- **Paleo-Hebrew Analysis** — 22 letters as pictograms. Each carries an image, not just a sound. Proto-Canaanite and Phoenician scripts serve as reference witnesses.
- **Root Dictionary** — 154+ three-letter roots with Paleo-images, meanings, and Tanakh examples.
- **Religionism Checker** — detects substitution words (Lord → YHWH, God → Elohim) in any Russian text and suggests restored terms.
- **Translation Comparator** — side-by-side view of the Masoretic Text, Septuagint, and Synodal translation. See what was lost at each layer.
- **Research Laboratory** — integrated webapp with global search, dark mode, mobile support, and keyboard shortcuts.
- **Board Generator** — visual investigation boards for exposing substitution chains. Export to PNG, PDF, TXT.
- **Multi-Agent AI** — CrewAI-powered agents for automated root research, verse analysis, and exposure detection.

---

## Quick Start

**Online:** [ortamy.github.io/golem](https://ortamy.github.io/golem)
**Research Lab:** [ortamy.github.io/golem/webapp](https://ortamy.github.io/golem/webapp)

```bash
git clone https://github.com/ortamy/golem.git
cd golem
python tools/golem.py
```

```bash
cd products/agents
python main.py "אמן"
```

---

## Architecture

```
golem/
├── content/          Terminology, Tanakh, Bashah, Research
├── instructions/     Methodology: exposure, dictionaries, templates
├── products/
│   ├── website/      Public site + Research Laboratory (SPA)
│   ├── agents/       CrewAI multi-agent system
│   ├── discord-bot/  Discord bot (Node.js)
│   └── neuro/        Neural network "Ed"
├── tools/            Python utilities: checkers, generators, reports
└── data/             Structured data: roots.json, paleo.json, exposures.json
```

---

## Tech Stack

- **Public Site** — HTML/CSS, Tailwind CSS, Preline
- **Research Lab** — Vanilla JavaScript SPA with hash routing
- **Bots** — Node.js (Discord), Telegram Bot API
- **AI Agents** — CrewAI, Python 3.12, Claude API, OpenAI API
- **Utilities** — Python, JSON
- **Deployment** — GitHub Pages + GitHub Actions

---

## Methodology

1. **Paleo-Hebrew first.** Each of the 22 letters is a pictogram. Meaning is embedded in form. Proto-Canaanite and Phoenician parallels serve as reference witnesses.
2. **Three-letter roots.** Every word is reduced to its root. Root equals action, not abstraction.
3. **Translation chain analysis.** Synodal → Church Slavonic → Latin (Vulgate) → Greek (Septuagint) → Hebrew. Substitutions are identified at each layer.
4. **Nine distortion types.** Category substitution, juridification, psychologization, action-to-emotion shift, abstraction, meaning narrowing, dualization, meaning castration, babylonization.
5. **If it's complicated, it's wrong.** The Tanakh is an instruction manual, not a history book.

---

## Key Substitutions

- **Lord** (יהוה) → YHWH
- **God** (אלהים) → Elohim
- **Soul** (נפש) → Breathing being
- **Spirit** (רוח) → Breath / Wind
- **Faith** (אמונה) → Faithfulness in action
- **Sin** (חטא) → Miss (the mark)
- **Sacrifice** (קרבן) → Drawing near
- **Law** (תורה) → Instruction
- **Glory** (כבוד) → Weight / Presence
- **Church** (קהלה) → Assembly

---

## License

MIT

---

## Links

- **Website:** [ortamy.github.io/golem](https://ortamy.github.io/golem)
- **Laboratory:** [ortamy.github.io/golem/webapp](https://ortamy.github.io/golem/webapp)
- **GitHub:** [github.com/ortamy/golem](https://github.com/ortamy/golem)
