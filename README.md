# Preparing GNSS positional data for football tactical analysis

This repository is set up to provide examplary code for **all pre-processing steps necessary for preparing GNSS positional data for football tactical analysis**. It can be used to analyze training sessions (including small-sided games) as well as match scenarios.</br></br>
This repository contains a data sample of football small-sided games (SSG), as well as the referential code for step-by-step pre-processing.</br></br>
The code is primarily designed for Catapult tracking systems and has been made compatible with other tracking systems as well, such as STATSports. However, different parsers might still be required to load data from different data providers. Please make sure to double check the data format after loading the data.</br></br>
To preserve anonymity, personal and location data that can determine individuals' information have been modified without affecting the demonstration purpose.</br></br>
The rationale behind each processing step is explained in detail in a manuscript under review.</br></br>

> [!IMPORTANT]
> Please check out the following lines before runing the code.
 

## 1. Dataset_A_Positional_data

An exemplar dataset of raw GNSS positional data from six individuals, each comprises following columns necessary for data processing.</br>
|   Timestamp    |  Latitude  |  Longitude  |
|----------------|------------|-------------|
|       ...      |     ...    |     ...     |

    - Timestamp (e.g., Unix or Converted timestamp)

    - Latitude and Longitude coordinates

Examplar data were collected using Catapult Optimeye S5 tracking devices (10 Hz, Catapult Innovations, South Melbourne, VIC, Australia).</br></br>
Additional data collected using Catapult Vector S7 and STATSports player tracking devices were also used during the pipeline development.

## 2. Dataset_B_Pitch

An exemplar dataset of pitch location information, provides the geographic coordinates of four pitch corners.</br>
|  Latitude  |  Longitude  |
|------------|-------------|
|     ...    |     ...     |

## 3. Datset_C_SessionDetails

An exemplar dataset of session details, provides the exact start and end timestamps of the SSG.</br>
|  Player Name  |  Start Time  |  End Time  |
|---------------|--------------|------------|
|      ...      |      ...     |     ...    |

## 4. Codes

> [!TIP]
> Users only have to run `file_1_main_analysis.py` for data processing.</br></br>
> `file_2_preprocessing.py` provides all functions needed for data processing in `file_1_main_analysis.py`.</br></br>

> [!IMPORTANT]
> Please read **4.2 Set global path** before running the code.

### 4.1 Install packages

> [!IMPORTANT]
> Before running the code, install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 4.2 Set global path

To make sure users can get on this code package asap, all directories needed for reading files have been set in unified format.

> [!IMPORTANT]
> Before running the code, users should make sure
> - files (`Dataset_A_Positional_Data`, `Dataset_B_Pitch.csv`, `Datset_C_SessionDetails.xlsx`, `file_1_main_analysis.py`, `file_2_preprocessing.py`) are enclosed in a **single folder**.
> - working directory is set as the folder where all files above are stored.<br/><br/>
Once all files are enclosed in a single folder, the folder's path is set to be automatically identified.</br></br>
> If it fails to automatically identify folder path, please try to insert the folder path manually: :arrow_down:</br>
>  - Copy/paste the filepath of the corresponding folder path into `line 44` in `file_1_main_analysis.py`.
>  - The correct file path should contain following delimiters: `/` (Windows or Linux), `\` (Mac).<br/><br/>

> [!TIP]
> For your later use, please alawys ensure a correct folder path in `file_1_main_analysis.py`.

### 4.3 Standardised file naming (for future use)

While case-insensitivity and spelling errors are allowed to minimise users' trial-and-error, we would like users to be aware of the standardised file naming, and potential format issues that might need to be dealt with in their later uses.</br></br>
In your future use, to ensure a smooth start with new datasets, please double check if your files follow the guidelines below.

- File naming

    - `Dataset_A_Positional_Data` for your folder containing all individual position data
    - `Dataset_B_Pitch` for pitch location file (both `.csv` and `.xlsx` supported)
    - `Datset_C_SessionDetails` for session's start and end timestamps ((both `.csv` and `.xlsx` supported)

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

### 4.4 Pre-set helpful notification

> [!IMPORTANT]
> The following notifications (not warning) are designed to inform users of necessary file preparation.

As mentioned above, positional data files should contain column **"Timestamp", "Latitude", and "Longitude"**.<br/><br/>
However, letter-case and spelling issues could happen in reality, and are therefore allowed in the current code package.<br/><br/>
To help users **double check file and column naming and domenstrate the notifications in case unexpected naming found, the examplar dataset contains column names that do not fully follow the standardised naming**.<br/><br/>
As an example, when running the code with the examplar data, you will see a prompt </br>
`"[OK] Friendly reminder: Column ' Longitude' in U18_ID4.csv will be renamed to 'Longitude' in further processing. No action needed. Please double check column format in future uses."`<br/></br>
:arrow_up: The prompt indicates **the code running well :white_check_mark: and the potential issues**.
    
## Additional trial data

To demonstrate the pipeline's compatiability with different sources, such as data from STATSports player tracking devices with converted timestamps.</br></br>
A giveaway dataset can be found in the following link [latilongitude/Positional_STATSports](https://github.com/latilongitude/Positional_STATSports).
