# Navigating Team Tactical Analysis in Football: An Analytical Pipeline Leveraging Player Tracking Technology


This repository contains a data sample of football small-sided games (SSG), as well as the referentail code for data processing prior to tactical analysis. To preserve anonymity, personal and location data that can determine individuals' information have been modified without affecting the demonstration purpose. The purpose of this repository is to provide example code for all the preprocessing steps necessary for tactical analysis in football based on GNSS data. It can be used to analyze training sessions (including small-sided games) as well as match data. The code is primarily designed for Catapult tracking systems but can be adapted for other systems as well.

The rationale behind each processing step is explained in detail in:<br />
Zhang, G., Kempe, M., McRobert, A., Folgado, H., & Olthof, S.B.H (under review). Navigating the Game: An Analytical Pipeline for GNSS-Based Tactical Analysis in Football   

## Dataset A

An exemplar dataset of raw GNSS positional data from six individuals, each comprises columns of timestamp (Unix), and players' latitude and longitude coordinates during the SSG. Data were collected with Catapult Optimeye
S5 tracking devices (10 Hz, Catapult Innovations, South Melbourne, VIC, Australia).


## Dataset B

An exemplar dataset of session details, provides the exact start and end timestamps of the SSG.

## Dataset C

An exemplar dataset of pitch location information, provides the geographic coordinates of four pitch corners.

## Codes

`file_2_preprocessing.py` provides all functions needed for data processing in `file_1_main_analysis.py`

## Support

For support, please reach out to us on X (Twitter): <br />
- [@Zhang64182011](https://x.com/Zhang64182011) <br />
* [@kempe_matthias](https://x.com/kempe_matthias) <br />

## Publication
Zhang, G., Kempe, M., McRobert, A., Folgado, H., & Olthof, S.B.H (under review). Navigating the Game: An Analytical Pipeline for GNSS-Based Tactical Analysis in Football   
