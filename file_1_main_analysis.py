from file_2_preprocessing import FileDetection
from file_2_preprocessing import SessionDetails
from file_2_preprocessing import PitchRotation
from file_2_preprocessing import PositionalData
from file_2_preprocessing import VisualInspection

import os
import pandas as pd
import scipy.signal as signal


#%% set global working directory

'''

Please set the working directory that contains all files.

Example for Windows (delimiter "\"):  "C:\Desktop\..."

Example for Mac (delimiter "/"): "/Users/..."

Enclosed folder/files will be detected.

'''
## set folder path
#folder_path = 'PLEASE COPY/TYPE IN THE PATHNAME OF THE FOLDER CONTAINING ALL FILES'
## Example: "\Desktop\..." for Windows; "/Desktop/..." for Mac
folder_path = '/Users/abcd/Documents/Liverpool/Statsports/trial/Data'
#folder_path = '/Users/abcd/Documents/Liverpool/Manuscript-Tactical/Submission_JSET/Revision_R1/codes_05062025'

## identify relevant files and folder
filename_session, filename_pitch, foldername_position_data = FileDetection.detect_file_folder_name(folder_path)

#%% read session details
'''

This section reads the session detials of your interest.

Data exported from different devices/brands may include various types of information.

For the purpose of demonstration, the following columns are of interest,

Date, Category, Format, Team in SSGs, Player Name, Split Start Time, Split End Time


An overview provided below:

	Date	Category	Format	Number of team 	Player Name	Split Start Time	Split End Time
0	44519	U-18	6 v 6 	A	ID_1	44519.746692731	44519.747584907
1	44519	U-18	6 v 6 	A	ID_2	44519.746692731	44519.747584907
2	44519	U-18	6 v 6 	A	ID_3	44519.746692731	44519.747584907
3	44519	U-18	6 v 6 	A	ID_4	44519.746692731	44519.747584907
4	44519	U-18	6 v 6 	A	ID_5	44519.746692731	44519.747584907
5	44519	U-18	6 v 6 	A	ID_6	44519.746692731	44519.747584907


*** Please keep columns of interest in your dataset using the variable 'col_to_be_used' below

*** Please always keep the Timestamp info (i.e., Split Start Time, Split End Time) while their column names may vary
    
*** This is necessary for subsetting positional data later

'''

## filepath for session details
match_info_dir = os.path.join(folder_path, filename_session)

## read data
match_info = SessionDetails.read_match_data(match_info_dir)

## parser checking data format
time_format = SessionDetails.check_time_columns(match_info)

#%% read pitch location
'''

This section reads the latitude and longitude coordinates of pitch corners

Please ensure your file in the following format

    	Longitude	Latitude
0	-9.12436877	    41.72674194
1	-9.123890745	41.72592757
2	-9.123290669	41.72612579
3	-9.12376968	    41.72693916

'''

## read pitch data
pitch = PitchRotation.read_pitch(folder_path, filename_pitch)

## check dataset format
pitch = PitchRotation.check_pitch_columns(pitch)

#%% map projection

'''

Convert geographic coordinates into cartesian coordinates

Visual inspection option is provided

'''

ini_xyco_pitch = PitchRotation.coordinates_to_field(pitch) # get coordinates(x, y) of pitch

## plot the pitch after map projection
PitchRotation.plot_pitch(ini_xyco_pitch)

#%% rotation matirx calculation

'''

Make sure pitch length and width align with x-axis and y-axis respectively, for following goal-to-goal or side-to-side analysis.

Rotation matrix computed from rotating pitch will also be used to calibrate player positional data.

'''

## determine origin and other vertices
ini_xyco_pitch = ini_xyco_pitch.sort_values(by = 'Y', axis=0, ascending = True) # sort vertices by the value of y

origin = ini_xyco_pitch[0:2].sort_values(by = 'X', axis=0, ascending=True).iloc[[0]] # the origin

the_other = ini_xyco_pitch[0:2].sort_values(by = 'X', axis=0, ascending=True).iloc[[-1]] # the other vertex on x-axis

third_vex = ini_xyco_pitch[2:3] # third vertex

fourth_vex = ini_xyco_pitch[3:4] # forth vertex

## calculate rotation matrix
rotation_matrix = PitchRotation.rotation_matrix(origin, the_other, third_vex, fourth_vex)

## create DataFrame for saving rotated vertices
pitch_rotated = pd.DataFrame(columns = ['X', 'Y'])

## calibrate pitch coordinates (apply rotation matrix to four vertices)
for vex in (origin, the_other, third_vex, fourth_vex):
    
    pitch_rotated.loc[len(pitch_rotated)] = PitchRotation.rotating_vertex(rotation_matrix, vex)
    
print (f"\n Rotated pitch coordinates:\n {pitch_rotated} \n") # get rotated pitch vextices

## plot rotated pitch
PitchRotation.plot_pitch(pitch_rotated) # plot the pitch after rotation

## check if it is needed to switch X and Y in both position and pitch data (to make pitch length parallel with x-axis)
pitch_rotated, switch_X_Y = PitchRotation.switch_x_y(pitch_rotated)

#%% process individual positional data

'''

An example of individual positional data is provided below, necessary columns including Timestamp, Longtitude, Latitude.

    Timestamp	Longitude	Latitude
44519.71566	-9.123676222	41.7260952
44519.71566	-9.123676222	41.7260952

'''

## path to SSG positional data
position_data_dir = os.path.join(folder_path, foldername_position_data)

## check data format, necessary columns include 'Timestamp', 'Latitude', 'Longitude'
check_position_data = PositionalData.check_pitch_columns(position_data_dir) # if necessary columns missing and alternative

## number of players in each team
playernum = len(set([f for f in os.listdir(position_data_dir) if f.endswith('.csv')])) # read csv files only
print (f"\n {playernum} players in each team during the session")

## use the rotation matrix used for rotating pitch
rm = rotation_matrix

## timestamps of session start and end
start_ts, end_ts = PositionalData.identify_start_end_timestamp(match_info, time_format, playernum)

## process individual data into team data
ssg = PositionalData.team_tracking(position_data_dir, check_position_data, time_format, start_ts, end_ts, rm, switch_X_Y)

## create a 10 Hz dummy timeline starting from 0.1s
dum_timeline, ssg = PositionalData.create_new_timeline(time_format, ssg, start_ts, end_ts)


#%% check data loss

date_loss = PositionalData.check_data_loss(ssg, dum_timeline)

#%% merge the positional data with new timeline

ssg_10Hz = pd.merge(dum_timeline, ssg, on = "Timestamp", how = "outer")

#%% interpolation

ssg_10Hz = ssg_10Hz.interpolate(method="linear", limit_direction="both", axis=0)

#%% data smoothing, two options provided below

## Option 1: Savitzky-Golay filter
for col in range (2, playernum*2+2):
    
    ssg_10Hz.iloc[0:, col] = signal.savgol_filter(ssg_10Hz.iloc[0:, col], window_length = 7, polyorder = 1)

print ("Smoothing Finished")


# ## Option 2: Butterworth low-pass filter
# # Generate a sample signal: a sine wave with added noise
# fs = 500  # Sample rate (Hz)
    
# # Design a low-pass Butterworth filter
# order = 4  # Filter order
# cutoff = 10  # Cutoff frequency in Hz
    
# # Normalize the frequency (cutoff / Nyquist frequency)
# nyquist = 0.5 * fs
# normal_cutoff = cutoff / nyquist
    
# # Get the filter coefficients
# b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)

# for col in range (2, playernum*2+2):
    
#     ssg_10Hz.iloc[0:, col] = signal.filtfilt(b, a, ssg_10Hz.iloc[0:, col])

# print ("Smoothing Finished")

#%% visual inspection

"""

Plot the pitch and players.

"""

## a time point of interest, e.g., 2.5s after the session starts
sec = 12.5 # TYPE IN THE MOMENT YOU WOULD LIKE TO SEE

## plot the ocsillation
VisualInspection.plot_pitch_players(pitch_rotated, ssg_10Hz, sec)
