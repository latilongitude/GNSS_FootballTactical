# GNSS Football Tactical Pipeline

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)
[![Data Ready](https://img.shields.io/badge/datasets-SSG%20demo-green.svg)](#sample-datasets)

A reproducible pre-processing workflow for transforming raw GNSS positional data into analysis-ready inputs for football tactical studies. The repository includes sample datasets, turnkey scripts, and detailed guidance so researchers and analysts can go from raw Catapult/STATSports exports to pitch-aligned files tailored for tactical metrics.

> Personal and geographic identifiers have been anonymised without changing the analytical value of the demonstration datasets. Full motivation and methodology are described in the following publication:
Zhang, G., Kempe, M., McRobert, A., Folgado, H., & Olthof, S. (2025). Navigating Team Tactical Analysis in Football: An Analytical Pipeline Leveraging Player Tracking Technology. _Proceedings of the Institution of Mechanical Engineers, Part P: Journal of Sports Engineering and Technology._

## Contents
- [Overview](#overview)
- [Sample Datasets](#sample-datasets)
- [Pipeline Usage](#pipeline-usage)
- [File and Column Naming](#file-and-column-naming)
- [Friendly Notifications](#friendly-notifications)
- [Further Resources](#further-resources)
- [Citation](#citation)

## Overview

This package demonstrates every pre-processing step required before computing tactical KPIs (team centroid, stretch index, etc.). It accepts training sessions (including small-sided games) and full-match scenarios. The scripts were primarily developed around Catapult Optimeye/Vector devices while validating compatibility with STATSports exports and converted timestamps.

## Sample Datasets

1. **Dataset_A_Positional_Data** – Six sample players with `Timestamp`, `Latitude`, `Longitude`. Recorded with Catapult Optimeye S5 (10 Hz) plus supplementary Vector S7 and STATSports data.
2. **Dataset_B_Pitch** – Four pitch-corner coordinates (latitude/longitude). Provided as `.csv`, but `.xlsx` is also supported.
3. **Datset_C_SessionDetails** – Session segments with `Player Name`, `Start Time`, `End Time`.

## Pipeline Usage

1. Place `file_1_main_analysis.py`, `file_2_preprocessing.py`, and the three datasets inside the same folder; set that folder as your working directory.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the pipeline:

   ```bash
   python file_1_main_analysis.py
   ```

4. If automatic path detection fails, open `file_1_main_analysis.py`, go to line 44, and paste the absolute path of the working folder. Use `/` on Windows/Linux or `\` on macOS.

Only `file_1_main_analysis.py` needs to be executed; `file_2_preprocessing.py` provides helper functions and simply needs to remain in the same directory.

## File and Column Naming

| Asset | Recommended Name | Required Columns |
| --- | --- | --- |
| Positional folder | `Dataset_A_Positional_Data` | `Timestamp`, `Latitude`, `Longitude` |
| Pitch file (`.csv`/`.xlsx`) | `Dataset_B_Pitch` | `Latitude`, `Longitude` |
| Session details (`.csv`/`.xlsx`) | `Datset_C_SessionDetails` | `Start Time`, `End Time` (+ optional `Player Name`) |

The scripts tolerate case differences and minor typos but will surface friendly reminders when auto-corrections occur so you can fix upstream exports.

## Friendly Notifications

During execution the script may print messages such as:

```
[OK] Friendly reminder: Column ' Longitude' in U18_ID4.csv will be renamed to 'Longitude'. No action needed. Please double check column format in future uses.
```

These messages indicate that the run is healthy while highlighting naming inconsistencies you may want to correct in future datasets.

## Further Resources

- Additional STATSports sample data: https://github.com/latilongitude/Positional_STATSports
- Tactical metric computation package: https://github.com/latilongitude/Compute_basic_tactical_measures

## Citation

If this pipeline supports your work, please cite the following publication:

Zhang, G., Kempe, M., McRobert, A., Folgado, H., & Olthof, S. (2025). Navigating Team Tactical Analysis in Football: An Analytical Pipeline Leveraging Player Tracking Technology. _Proceedings of the Institution of Mechanical Engineers, Part P: Journal of Sports Engineering and Technology._

For collaboration or questions, open an issue or contact the contributors of this repository.

