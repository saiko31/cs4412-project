# Pattern discovery of injury risk factors in under-25 professional footballers

## Author
**Alexander San Agustin Melendez**

## Overview
This project seeks to apply data mining techniques to find relationships between various factors (age, position, minutes played, etc.) and how these factors affect injuries in soccer players under the age of 25.

##  Data Sources
The project utilizes a hybrid dataset approach:
* **[StatsBomb Open Data](https://github.com/statsbomb/open-data):** Used for granular match events, minutes played, and performance metrics.
* **Transfermarkt (Scraped):** Used for player demographics, market value context, and historical injury records.

## Tech Stack
* **Language:** Python
* **Libraries:** Pandas, NumPy, Scikit-learn, BeautifulSoup/Scrapy (for Transfermarkt)
* **Documentation:** LaTeX (for technical reporting)

## Repository Structure

The project is organized to separate data acquisition, processing, and final analysis:

```text
├── data/
|  #  This is where all the data goes
├── notebooks/
|  #  Jupyternotebooks
├── src/
|  # All the source code for the project
├── docs/
|    # Here goes all the related documents, proposal included.
│   └── figures/            # Generated charts and tables for the IIIC paper
├── README.md
