# Alligator

Powered by

[<img src="./images/UNIMIB-logo.png" alt="UniMiB Logo" width="100"/>](https://www.unimib.it/)

## **General Description**
Alligator is a tool for semantic table interpretation (STI).

It analyzes tabular data by linking content cells to entities, classifying column content as entity names or literals, and associating column types and properties with a reference knowledge graph (KG) such as Wikidata or DBpedia.

By enriching tables with explicit semantic annotations, Alligator facilitates data integration, interoperability, and reuse in semantic and knowledge-based applications.

## **Related Compliance Aspects**
- Scalable knowledge-graph-based annotation of tabular data
- Pipeline component for semantic data enrichment

## **Main Goal/Functionalities**
- Perform cell-level semantic annotation using a two-stage ranking ML model
- Detect and link column types at schema level
- Detect and link column properties at schema level
- Perform entity matching and linking for cell content reconciliation

## **Architecture**
Alligator takes as input a tabular dataset in CSV format together with a set of candidate entities for linking the labels appearing in table cells, and produces a JSON file containing the resulting annotations.

The figure below illustrates the core pipeline of the process, which includes a two-stage ranking of candidate entities performed by a neural network–based machine learning model, followed by a decision component that computes confidence scores to identify the best candidate for each cell mention.

![Alligator Architecture](./images/alligator%20core.png)
 
## **Component Definition**
Alligator is implemented as a Python library and exposed through a REST API, enabling the semantic annotation of tabular data. The underlying approach relies on the computation of confidence scores that are used to rank candidate matches and to select the most appropriate annotations.

For entity matching at the cell level, confidence scores are computed by jointly considering the entity mentions occurring in individual cells as well as the row-level context derived from the content of the other cells within the same row. For column-level annotation, including the detection and linking of column types and properties, Alligator leverages and aggregates the results of the entity matching performed on the cells within each column.

The high quality of the resulting semantic annotations improves the reliability of the produced outputs, facilitates their interpretability, and supports human-in-the-loop validation and revision.

Alligator has been integrated into the SemT-X framework, which enables interactive table enrichment, supports manual review and correction of annotations, and allows the definition of domain-dependent rules to further improve annotation accuracy.

## **Screenshots**
n/a

## **Commercial Information**

| Organisation (s)            | License Nature | License    |
|-----------------------------|----------------|------------|
| University of Milan-Bicocca | Open Source | Apache 2.0 |

## **Expected KPIs**

|What (types)|How(Process)|Values|
|-|-|--|
|Quality of semantic annotations in tables for Entities (CEA), Predicates (CPA), and Types (CTA)|Using benchmarks for semantic table interpretation, refined for compliance-related challenges|CEA Accuracy >= 0.8, CTA F1 >= 0.8, CPA F1 >= 0.8|
|Efficiency|Measure of average processing time on sample representative datasets|ability to process 1000 rows in less than 500 seconds|

## **Related Project Links**
| Project Links |
| ------------- | 	
| Software GitHub Repository --> Refer to online documentation: https://github.com/enRichMyData/alligator


## **How To Install**
Refer to online documentation: https://github.com/enRichMyData/alligator

## **How To Use**

Refer to online documentation: https://github.com/enRichMyData/alligator


## **Other Information**

n/a

## **OpenAPI Specification**

n/a

## **Additional Links**

[R. Avogadro, M. Ciavotta, F. De Paoli, M. Palmonari and D. Roman, "Estimating Link Confidence for Human-in-the-Loop Table Annotation," 2023 IEEE/WIC International Conference on Web Intelligence and Intelligent Agent Technology (WI-IAT), Venice, Italy, 2023, pp. 142-149.](https://ieeexplore.ieee.org/document/10350082)


