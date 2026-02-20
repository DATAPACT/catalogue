# Carbontracker

Developed and maintained by

[![UCPH](./images/ucph.jpg)](https://www.ku.dk/en)


## **General Description**

CarbonTracker serves as a computational instrument for monitoring and predicting the energy consumption and carbon footprint associated with the training of deep learning models. Addressing the growing environmental impact of large-scale neural network optimization, this tool provides a real-time tracking mechanism that couples hardware-level power telemetry with geolocation-based carbon intensity data. By operationalizing the "Green AI" paradigm, it enables researchers to quantify the environmental cost of their computational workflows, facilitating a transition from purely performance-driven metrics to a holistic evaluation that includes resource efficiency and ecological impact.

## **Related Compliance Aspects**

The software aligns with emerging standards for Responsible Computing and Environmental, Social, and Governance (ESG) criteria within the technology sector. It supports the generation of "Carbon Impact Statements," enabling standardized reporting of model training emissions. This functionality aids compliance with voluntary sustainability goals and institutional requirements for transparency in research, ensuring that the ecological footprint of artificial intelligence development is documented and audit-ready.

## **Main Goal/Functionalities**

The primary function of CarbonTracker is to provide accurate, interpretable estimates of the carbon dioxide equivalent (CO2eq) emitted during model training. It features a predictive engine that extrapolates total consumption from a limited initial set of epochs, allowing users to preemptively abort training runs that exceed acceptable environmental thresholds ("Stop-and-Confirm"). The tool aggregates telemetry from various hardware components—specifically NVIDIA GPUs and Intel CPUs—and interfaces with external APIs like ElectricityMaps to fetch real-time regional carbon intensity. Additionally, it offers a Command Line Interface (CLI) for log aggregation and retrospective analysis, as well as the generation of interpretable reports that contextualize emissions in tangible terms, such as equivalent kilometers driven.

## **Architecture**

The system is architected as a Python-based library that integrates directly into the training loops of deep learning frameworks such as PyTorch, TensorFlow, and Keras. It employs a multi-threaded design where a dedicated "sleeper thread" queries hardware interfaces (e.g., NVML for GPUs, RAPL for CPUs) at specified intervals to log power draw without blocking the main computational thread. This raw power data is synchronized with carbon intensity metrics fetched via web APIs. The core logic handles the extrapolation of these discrete measurements into global predictions, handling exception management and graceful degradation to national averages when specific geolocation data is unavailable.

## **Screenshots**

n/a

## **Commercial Information**

The software is developed and maintained by University of Copenhagen and is distributed as an Open Source project under the MIT License.

## **Expected KPIs**

| Optimization Objective | Process | Values |
| :--- | :--- | :--- |
| Profiling of energy consumption and carbon fooptrint of AI pipelines	| Pipeline rating according to efficiency | Measurement of energy consumption correlated with hardware measurements (correlation > 0.9)|

## **Related Project Links**

The source code and documentation are hosted on the CarbonTracker GitHub repository at [https://github.com/saintslab/carbontracker](https://github.com/saintslab/carbontracker).

## **How To Install**

CarbonTracker is deployed via the Python Package Index (PyPI). Installation requires a Python 3.6+ environment and can be executed using the standard package manager command `pip install carbontracker`. For users requiring specific hardware support or development versions, the repository can be cloned and installed directly.

## **How To Use**

Integration involves instantiating the `CarbonTracker` class within the training script and wrapping the epoch iteration loop. The tracker is initialized with the expected total number of epochs and optional parameters for monitoring frequency. During execution, the `epoch_start()` and `epoch_end()` methods must be called to demarcate the measurement windows. Upon completion or interruption, the tool outputs a summary of the energy consumed and the associated carbon emissions to the console and a local log file.

## **Other Information**

n/a

## **OpenAPI Specification**

n/a

## **Additional Links**

[Anthony, L. F. W., Kanding, B., & Selvan, R. (2020). Carbontracker: Tracking and Predicting the Carbon Footprint of Training Deep Learning Models. arXiv preprint arXiv:2007.03051.](https://arxiv.org/abs/2007.03051)
