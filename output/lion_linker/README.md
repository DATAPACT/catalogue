<div class="tool-header">
  <h1>Lion-Linker</h1>
  <img src="./images/SINTEF_Logo_Sentrert_RGB.svg" alt="SINTEF logo" width="220">
</div>

## **General Description**
Lion-Linker is a Python library that uses large language models (LLMs) to perform entity linking and disambiguation for tabular data. It takes tabular inputs, retrieves candidate entities, and ranks them to produce linked entities that can be used for dataset enrichment and downstream analysis within DATAPACT workflows.

## **Related Compliance aspects**

- Data/AI pipeline step implementation for data enrichment

## **Main Goal/Functionalities**
- LLM-assisted entity linking and ambiguity resolution for tabular data
- Candidate ranking with top-k suggestions for ambiguous cells
- Outputs suitable for dataset enrichment and analysis workflows

## **Architecture**

![Lion-Linker Architecture Placeholder](./images/lion-linker-architecture-placeholder.svg)

## **Component Definition**
Lion-Linker is a modular library that accepts tabular inputs, integrates with external candidate retrieval services or knowledge bases, and applies LLM-based ranking to select the most relevant entity for each target cell. The resulting links can be exported as enriched tables or structured outputs for further processing.

## **Screenshots**

n/a

## **Commercial Information**

| Organisation (s) | License Nature | License |
|------------------|----------------|---------|
| SINTEF | Open Source | Apache License 2.0 |

## **Expected KPIs**

|What (types)|How(Process)|Values|
|------------|------------|------|
|Effectiveness of contextual entity linking and ambiguity resolution in tabular data|Expert validation of entity linking results on ambiguous cases, comparing LLM-assisted ranking with non-LLM baseline ranking on representative table samples|Lion-Linker should rank the expert-preferred entity as top-1 in at least 75% of evaluated cases, and show a minimum 10% improvement in disambiguation accuracy compared to non-LLM ranking approaches. Additionally, the correct entity should appear within the top-5 candidates in at least 90% of evaluated cases|

## **Related Project Links**
| Project Links |
| ------------- |
| Related GitHub repository (Lion-Linker) <https://github.com/enRichMyData/lion_linker> |

## **How To Install**
The DATAPACT packaging for Lion-Linker is not yet published.
For updates, see the Lion-Linker repository: https://github.com/enRichMyData/lion_linker

### Detailed steps

n/a

## **How To Use**
For usage patterns and examples, see the Lion-Linker repository: https://github.com/enRichMyData/lion_linker

## **Other Information**

n/a

## **OpenAPI Specification**

n/a

## **Additional Links**

n/a
