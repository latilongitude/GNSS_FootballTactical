# Navigating Team Tactical Analysis in Football: An Analytical Pipeline Leveraging Player Tracking Technology

This repository contains a data sample of football small-sided games (SSG), as well as the referential code for data pre-processing prior to tactical analysis.

The purpose of this repository is to provide example code for all the preprocessing steps necessary for tactical analysis in football based on GNSS data. It can be used to analyze training sessions (including small-sided games) as well as match data.

The code is primarily designed for Catapult tracking systems and has been made compatible with other tracking systems as well, such as STATSports.

To preserve anonymity, personal and location data that can determine individuals' information have been modified without affecting the demonstration purpose.

The rationale behind each processing step is explained in detail in a manuscript under review:<br />
_Zhang, G., Kempe, M., McRobert, A., Folgado, H., & Olthof, S.B.H (under review). Navigating Team Tactical Analysis in Football: An Analytical Pipeline Leveraging Player Tracking Technology_
   
> [!IMPORTANT]
> Please check out the following lines before runing the code.


## 1. Dataset_A_Positional_data

An exemplar dataset of raw GNSS positional data from six individuals, each comprises following ccolumns

    - Timestamp (e.g., Unix or Converted timestamp)

    - Players' Latitude and Longitude coordinates

Examplar data were collected with Catapult Optimeye S5 tracking devices (10 Hz, Catapult Innovations, South Melbourne, VIC, Australia).

Additional data collected with Catapult Vector S7 and STATSports devices were also used during the pipeline development.


## 2. Dataset_B_Pitch

An exemplar dataset of pitch location information, provides the geographic coordinates of four pitch corners.


## 3. Datset_C_SessionDetails

An exemplar dataset of session details, provides the exact start and end timestamps of the SSG.


## 4. Codes

`file_2_preprocessing.py` provides all functions needed for data processing in `file_1_main_analysis.py`


### 4.1 Set global path

To make sure python begainners can get on this code package asap, all directories needed for reading files have been set in unified format.

After downloadling all files, users should 
    
    1. make sure files (`Dataset_A_Positional_Data`, `Dataset_B_Pitch.csv`, `Datset_C_SessionDetails.xlsx`) are under the same filepath (e.g., enclosed in single folder).
    
    2. copy/paste the filepath of the corresponding folder into line XXX in `file_1_main_analysis.py`. The correct file path should contain following delimiters: `/` (Windows or Linux), `\` (Mac).

> [!IMPORTANT]
> For your later use, please alawys ensure a correct filepath in `file_1_main_analysis.py`.


### 4.2 Standardised file naming (for future use)

While case-insensitivity and spelling errors are allowed to minimise users' trial-and-error, we would like users to be aware of the standardised file naming, and potential format issues that might need to be dealt with in their later uses.

In your future use, to ensure a smooth start with new datasets, please double check if your files follow the guidelines below.

- File naming

    - `Dataset_A_Positional_Data` for your folder containing individual position data files that are named as `TEAM_PLAYER`, such as `U18_ID13.csv`.
    - `Dataset_B_Pitch` for pitch location file (both `.csv` and `.xlsx` are supported)
    - `Datset_C_SessionDetails` for session's start and end timestamps ((both `.csv` and `.xlsx` are supported)

- Column naming

    - Files in folder `Dataset_A_Positional_Data` should contain the following columns
        - "Timestamp"
        - "Latitude"
        - "Longitude"
    
    - `Dataset_B_Pitch` should contain the following columns
        - "Latitude"
        - "Longitude"
    
    - `Datset_C_SessionDetails` should contain the following columns
        - "Start Time"
        - "End Time"

### 4.3 Pre-set helpful notification

> [!IMPORTANT]
> The following notifications (not warning) are designed to inform users of necessary file preparation

As mentioned above, positional data files should contain column "Timestamp", "Latitude", and "Longitude".
    
However, letter-case and spelling issues could happen in reality, and are therefore allowed in the current code package.
    
To help users double check file and column naming and domenstrate the notifications in case unexpected naming is found, the examplar dataset contains column names that do not fully follow the standardised naming.
    
For example, when running the code with the examplar data, you will see a prompt <br />
**_"[OK] Friendly reminder: Column ' Longitude' in U18_ID4.csv will be renamed to 'Longitude' in further processing. No action needed. Please double check column format in future uses."_**
This indicates the codes running well and the potential issues.
    
## Additional trial data

To demonstrate the pipeline's compatibility with different data sources, such as data from STATSports with converted timestamp, a giveaway dataset can be found in the following link [Positional_STATSports](https://github.com/latilongitude/Positional_STATSports).


## Support

For support, please reach out to us on LinkedIn or X : <br />
- [Guangze Zhang](https://www.linkedin.com/in/guangze-zhang-5902a2178) <br />
* [Matthias Kempe](https://www.linkedin.com/in/matthias-kempe-268208168) <br />

## Publication
Zhang, G., Kempe, M., McRobert, A., Folgado, H., & Olthof, S.B.H (under review). Navigating the Game: An Analytical Pipeline for GNSS-Based Tactical Analysis in Football   
