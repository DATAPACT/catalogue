<div class="tool-header">
  <h1>Koala UI</h1>
  <a href="https://www.sintef.no/">
    <img src="./images/sintef_logo.svg" alt="SINTEF logo" width="220">
  </a>
</div>

## **General Description**
Koala UI is a web user interface that supports semantic annotation and human-in-the-loop review of tabular data. It lets users explore datasets, inspect tables, run entity linking and annotation jobs, and export enriched CSV files. The UI is designed to make enrichment workflows transparent and auditable by domain experts and data stewards.

## **Related Compliance aspects**
- Semantic annotation
- Human-in-the-loop validation to support compliant data enrichment
- Data review and quality assurance for enrichment outputs

## **Main Goal/Functionalities**
- Interactive dataset exploration and filtering
- Manual and assisted semantic annotation of table columns and cells
- Entity linking integration (e.g., Lion Linker)
- DPV annotation support
- Export of enriched datasets for downstream processing

## **Architecture**
Koala UI is a React-based front-end that communicates with a Flask backend. The backend manages datasets and table metadata, orchestrates annotation and linking jobs, and handles export of enriched data. External linking/annotation services can be integrated via backend APIs.

## **Component Definition**
Koala UI provides the human-facing interface for semantic enrichment workflows. It supports dataset ingestion, column type management, entity linking and disambiguation, and validation of suggested annotations. Users can review candidate entities, adjust annotations, and export enriched tables. The UI integrates with backend services that manage data storage and invoke external enrichment services.

## **Screenshots**
![Koala UI table view](./images/koala_ui_screenshot.png)

## **Commercial Information**

| Organisation (s) | License Nature | License |
|------------------|----------------|---------|
| SINTEF | Open Source | MIT |

## **Expected KPIs**

|What (types)|How(Process)|Values|
|------------|------------|------|
|Usability and effectiveness of human-in-the-loop validation of enriched datasets|Usability evaluation with domain experts and data stewards using the SUS questionnaire, combined with time-on-task comparison against manual workflows|Koala UI should achieve a mean SUS score of at least 75 across evaluated users, with no more than 25% of individual scores falling below 65. Annotation validation tasks should require at least 30% less time compared to baseline manual workflows|

## **Related Project Links**
| Project Links |
| ------------- | 	
| Software GitHub Repository --> Koala UI (upstream) <https://github.com/enRichMyData/koala_ui> |


## **How To Install**
See the upstream repository for installation and setup instructions: <https://github.com/enRichMyData/koala_ui>

### Detailed steps

n/a

## **How To Use**
1. Start the Koala UI backend and front-end following the upstream instructions.
2. Open the web UI and load a dataset.
3. Define or review column types, then run entity linking and annotation.
4. Validate and adjust annotations as needed.
5. Export the enriched dataset.


## **Other Information**

n/a

## **OpenAPI Specification**

n/a

## **Additional Links**

n/a
