<div class="tool-header">
  <h1 style="margin:0 0 12px 0;">Crocodile</h1>
  <a href="https://www.sintef.no/">
    <img src="./images/sintef_logo.svg" alt="SINTEF logo" width="220">
  </a>
</div>

## **General Description**
Crocodile is a Python library that performs entity linking over tabular data to support dataset enrichment and annotation. It connects cell values to canonical entities or knowledge base entries, helping improve data quality and enabling downstream analytics on enriched datasets.

## **Related Compliance aspects**
- Data/AI pipeline step implementation for data enrichment

## **Main Goal/Functionalities**
- Entity linking on tabular data
- Automated dataset enrichment and annotation
- Improve annotation quality for downstream use

## **Architecture**
The picture below shows the component in the DATAPACT architecture.
![Crocodile_Architecture](./images/crocodile_architecture.svg)

## **Component Definition**
Crocodile links entity mentions in tabular fields to canonical entities or knowledge bases, enriching datasets with standardized identifiers and metadata. This supports evaluation workflows and improves annotation consistency and quality across representative data samples.

## **Screenshots**
n/a

## **Commercial Information**

| Organisation (s) | License Nature | License |
|------------------|----------------|---------|
| SINTEF | Open Source | Apache-2.0 |

## **Expected KPIs**

| What (types) | How (Process) | Values |
|--------------|----------------|--------|
| **Entity Linking Accuracy (Benchmark Evaluation)** | Evaluate Precision@1 on the published benchmark datasets (Movies, Companies, Spend Network) available on Zenodo (https://zenodo.org/records/17160156). | Precision@1 ≥ 0.98 on Movies, ≥ 0.98 on Companies, and ≥ 0.56 on Spend Network (SN). |
| **Performance – Processing Throughput** | Benchmark Crocodile under documented reference infrastructure. Measure total wall-clock time for fixed-size input. | Process ≥ 100 rows within ≤ 60 seconds (end-to-end, including retrieval and ranking) |
| **Caching Mechanism & Performance Impact** | Evaluate system behaviour with caching enabled versus disabled on identical benchmark datasets. Measure cache hit ratio and total runtime difference. | Caching mechanism implemented and documented. Cache hit statistics exposed and positive runtime reduction observed when cache is enabled |

## **Related Project Links**
| Project Links |
| ------------- |	
| Software GitHub Repository --> Crocodile software <https://github.com/enRichMyData/crocodile> |

## **How To Install**
See the external repository for installation instructions: <https://github.com/enRichMyData/crocodile>

### Detailed steps

See the external repository README and docs: <https://github.com/enRichMyData/crocodile>

## **How To Use**

See usage instructions in the external repository: <https://github.com/enRichMyData/crocodile>

## **Other Information**

n/a

## **OpenAPI Specification**

n/a

## **Additional Links**

n/a
