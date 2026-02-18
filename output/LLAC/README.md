# JSI LLAC

Powered by

<!--<p align="left">
  <a href="https://www.ijs.si/"><img src="https://www.ijs.si/ijsw/Rubrike?action=AttachFile&do=get&target=000-modra.jpg" alt="Jožef Stefan Institute (JSI) logo" width="220"></a>
</p>-->

<img src="../images/jsi-logo.png" width="220" alt="JSI Logo" />

| Project Links                                                            |
| ------------------------------------------------------------------------ |
| **Software GitHub Repository** → JSI LLAC `<in progress>` |
| **Progress GitHub Project** → `<in progress>`             |

## **General Description**

LLAC is conceived as a socio-technical assistant that supports users in analysing regulatory obligations and assessing compliance risks in AI systems. LLAC is focused on LLM-powered pipelines for **legal/privacy compliance work** (e.g., GDPR) using **agentic ingestion**, **claim extraction**, and **contextualization** utilities.

## **Architecture**

High-level flow (conceptual):

1. **Ingestion**: Collect/ingest legal or policy text/corpus (agentic ingestion experiments).
2. **Claim Extraction**: Identify extractable claims/statements and structure them.
3. **Contextualization**: Enrich extracted claims with surrounding context (to reduce ambiguity).
4. **Graph/Structuring**: Represent extracted knowledge and relations in a graph-like structure for downstream querying/analysis.

## **Component Definition**

Repository structure includes (non-exhaustive):

- `claim_extraction/` — claim extraction experiments/utilities 
- `contextualize/` — contextualization workflows
- `prompts/` — prompt templates used by components
- `config/` — configuration files/settings 
- `data/` — datasets / sample inputs
- `system_corpus/` — corpus materials used for experiments
- `util/` — shared helpers/utilities
- Root-level experiments mentioned in the repo overview include: `agentic_ingestion.py`, `graph.py`, `gdpr.txt`, plus folders like `gdpr_contextualized/` and `openrouter_test/`.  

## **Screenshots**

<!--<img width="1279" height="860" alt="image" src="https://github.com/user-attachments/assets/b05e783b-46e5-4d15-8f7d-0023281e1ba8" />-->
<img src="../images/llac.png" width="500" alt="LLAC" />


## **Commercial Information**

| Organisation (s) | License Nature | License |
| ---------------  | -------------- | ------- |
| Jožef Stefan Institute (JSI) | Open Source | MIT


## **Expected KPIs**

| What (Types)            | How (Process)                                                                       | Values                                                                                                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Answer Quality | Benchmark on compliance questions derived from regulatory documents/user evaluation| Retriever Recall@10>50%,   Accuracy > 0.8 |


## **Top Features**

- Modular experimentation layout (claim extraction, contextualization, prompts, utilities). 
- Legal-oriented artifacts and experiments (e.g., `gdpr.txt`, contextualized GDPR folder).
- Agentic ingestion + graph/structuring exploration.

## **How To Install**

For deploy/access please send an email to Inna Novalija (inna.koval@jsi.si)
