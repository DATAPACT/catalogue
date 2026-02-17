# JSI Wikifier

Powered by

<!--<p align="left">
  <a href="https://www.ijs.si/"><img src="https://www.ijs.si/ijsw/Rubrike?action=AttachFile&do=get&target=000-modra.jpg" alt="Jožef Stefan Institute (JSI) logo" width="220"></a>
</p>-->

<img width="259" height="194" alt="image" src="https://github.com/user-attachments/assets/fc210d14-b546-44f1-b8f6-7ff7ba0533af" />


| Project Links                                                            |
| ------------------------------------------------------------------------ |
| **Public Service** → [https://wikifier.org](https://wikifier.org)        |

---

## **General Description**

JSI Wikifier is a semantic annotation and entity linking tool that identifies concepts in text and links them to knowledge bases (e.g., Wikipedia / Wikidata / DBpedia). It supports **~100 languages**, performs context-aware disambiguation, and returns rich metadata (titles, KB identifiers, offsets, confidence, and support scores). Typical use cases include content enrichment, information extraction, search/indexing, and analytics.

> 🔎 Quick view: Input free text → **Wikifier** → Output JSON with entities and links.

---

## **Architecture**

High-level data flow:

1. **Client** (browser, script, or backend) sends text and language params
2. **API Layer** validates requests and rate limits
3. **Annotation Engine**

   * Text preprocessing & language detection (if enabled)
   * Mention detection / candidate generation
   * **Disambiguation & scoring** using context signals
4. **Linking** to target KBs (Wikipedia / Wikidata / DBpedia)
5. **Response Formatter** → JSON / HTML preview
6. (Optional) **Caching & Storage** for performance and auditing

---

## **Component Definition**

* **REST API** — HTTP endpoints for annotation and configuration (rate‑limited; **requires `userKey`** on the public service).
* **Annotator** — mention detection + multilingual disambiguation engine
* **KB Connector** — access to Wikipedia/Wikidata/DBpedia indices
* **Language Module** — tokenization, normalization, and locale-specific rules
* **Cache/Store (optional)** — Redis/SQLite/PostgreSQL depending on deployment
* **Admin/Monitoring (optional)** — metrics, usage stats, health checks

---

## **Screenshots** (TBD)

* Annotation preview (web UI): `![Preview](./images/preview.png)`
* JSON response sample: `![JSON](./images/json.png)`

<img width="879" height="811" alt="image" src="https://github.com/user-attachments/assets/36427c49-bc2d-4a4e-82ea-374bc3c895ac" />
---

## **Commercial Information**

| Organisation (s)             | License Nature                                                                        | License / Terms                                                                                                                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Jožef Stefan Institute (JSI) | Public web service (fair use); source code for service infra not publicly distributed | Usage requires `userKey`; see [https://wikifier.org/register.html](https://wikifier.org/register.html) and service docs [https://wikifier.org/info.html](https://wikifier.org/info.html) |

> For commercial or on‑premise options, contact the maintainers.


---

## **Expected KPIs**

| What (Types)            | How (Process)                                                                       | Values                                                                                                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Annotation precision | Annotation precision. Measuring Precision Top N for semantic annotation/wikification task based on developed gold standard. | Annotation precision. Annotation Precision Top 1 > 0.8 |


---

## **Top Features**

* **Multilingual** annotation (≈100 languages)
* **Entity linking** to Wikipedia / Wikidata / DBpedia
* **Context-aware disambiguation** with confidence/support scores
* **Offsets & spans** for mentions (begin/end character positions)
* **Flexible output** (JSON for machines; HTML for quick inspection)
* **Batch & streaming** friendly requests
* **Configurable thresholds** (e.g., minimum confidence/support)

---

## **How To Use**

### Call the public service (GET or POST)

According to the official documentation, call:
`https://www.wikifier.org/annotate-article?text=...&lang=...&...` (GET) or send the same parameters as `application/x-www-form-urlencoded` in the POST body. **`userKey` is required.**

**Minimal example (GET):**

```bash
curl -G \
  --data-urlencode "userKey=<YOUR_USER_KEY>" \
  --data-urlencode "text=Barack Obama was the 44th President of the United States." \
  --data-urlencode "lang=en" \
  "https://www.wikifier.org/annotate-article"
```

**Typical example (POST):**

```bash
curl -X POST "https://www.wikifier.org/annotate-article" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "userKey=<YOUR_USER_KEY>" \
  --data-urlencode "text=Ljubljana is the capital of Slovenia." \
  --data-urlencode "lang=auto" \
  --data-urlencode "secondaryAnnotLanguage=en" \
  --data-urlencode "wikiDataClasses=true" \
  --data-urlencode "wikiDataClassIds=true" \
  --data-urlencode "support=true" \
  --data-urlencode "ranges=false" \
  --data-urlencode "includeCosines=false" \
  --data-urlencode "nTopDfValuesToIgnore=200" \
  --data-urlencode "maxMentionEntropy=3"
```

**Key parameters (selection):**

* `userKey` (required) — register at `/register.html`.
* `text` — UTF‑8 encoded text (URL‑encode non‑ASCII when using GET).
* `lang` — ISO‑639 code (e.g., `en`, `sl`) or `auto` for autodetect.
* `secondaryAnnotLanguage` — add names/links from another Wikipedia (default `en`).
* `wikiDataClasses`, `wikiDataClassIds` — include Wikidata classes / IDs.
* `support` — include supporting subranges for each annotation.
* `ranges` — include all candidate annotations for each span (large output).
* `includeCosines` — include page/document cosine similarities.
* `pageRankSqThreshold` (+ `applyPageRankSqThreshold`) — pagerank‑based pruning.
* `nTopDfValuesToIgnore`, `nWordsToIgnoreFromList` — ignore very frequent words.
* `partsOfSpeech` / `verbs` (English only) — include PoS and WordNet synsets.

**Output shape (abridged):**

```json
  "annotations": [ { "title": "New York City", "url": "…", "lang": "en", "wikiDataClassIds": ["Q515", …], "dbPediaIri": "…", "support": [ {"wFrom": 0, "wTo": 1, …} ] } ],
  "words": ["New", "York", "City"],
  "spaces": ["", " ", " ", "."],
  "ranges": [ { "wFrom": 0, "wTo": 1, "candidates": [ {"title": "New York", …} ] } ]
```

> Also available: `get-cosine-similarity` for page–page cosine and functions for extracting subgraphs of the Wikipedia link graph.

---

## **Other Information**

* Data sources: Wikipedia / Wikidata / DBpedia (versions depend on your indices)
* Privacy: avoid sending sensitive text to external endpoints; prefer self‑hosting if needed
* Internationalization: pass `lang` or enable auto-detection

---

## **Additional Links**
{wikifier.org/info.html)
* Supported languages: [https://wikifier.net/languages.html](https://wikifier.net/languages.html)
* About the service: [https://www.wikifier.org/about.html](https://www.wikifier.org/about.html)
* Official documentation: [https://www.wikifier.org/info.html](https://www.
* API (OpenAPI) spec page (project site): [https://jsi-eubusinessgraph.github.io/jsi-wikifier-api/](https://jsi-eubusinessgraph.github.io/jsi-wikifier-api/)
