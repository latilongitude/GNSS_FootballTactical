from preprocessing import SessionDetails
from preprocessing import PitchRotation
from preprocessing import PositionalData
from preprocessing import VisualInspection

import pandas as pd
import scipy.signal as signal
import matplotlib.pyplot as plt
from shapely.geometry import LinearRing


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

*** Please always keep the Timestamp info (i.e., Split Start Time, Split End Time) whose column name may vary
    
*** This is necessary for subsetting positional data later

'''

col_to_be_used = ['Date', 'Category', 'Format','Number of team ', 'Player Name', 'Split Start Time', 'Split End Time']

colname_start_time = 'Split Start Time' # the actual column in your dataset that contains starting timestamps

colname_end_time = 'Split End Time' # the actual column in your dataset that contains ending timestamps

match_info_dir = '/Users/abcd/Documents/Liverpool/Manuscript-Tactical/github/Dataset_B/ssgdetails_6x6.xlsx'

match_info = SessionDetails.read_match_data(match_info_dir, col_to_be_used, colname_start_time, colname_end_time)

# parser checking data format
check_match_info = SessionDetails.check_time_columns(match_info)

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

pitch = pd.read_csv("/Users/abcd/Documents/Liverpool/Manuscript-Tactical/github/Dataset_C/pitch.csv")

check_pitch = PitchRotation.check_pitch_columns(pitch)

#%% map projection

'''

Convert geographic coordinates into cartesian coordinates

Visual inspection option is provided

'''

ini_xyco_pitch = PitchRotation.coordinates_to_field(pitch) # get coordinates(x, y) of pitch

PitchRotation.plot_pitch(ini_xyco_pitch) # plot the pitch after map projection

#%% rotation matirx calculation

'''

Make sure pitch length and width align with x-axis and y-axis respectively, for following goal-to-goal or side-to-side analysis.

Rotation matrix computed from rotating pitch will also be used to calibrate player positional data.

'''

## determine origin and other vertices
ini_xyco_pitch.sort_values(by = 'Y', axis=0, ascending = True, inplace = True) # sort vertices by the value of y

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
    
    pitch_rotated.loc[len(pitch_rotated)] = PitchRotation.rotating_vertex(vex, rotation_matrix)
    
print (f"Rotated pitch: {pitch_rotated} \n") # get rotated pitch vextices

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

playernum = 6 # PLEASE TYPE IN THE NUMBER OF EACH TEAM IN YOUR DATASET

start_ts = float(format(float(match_info.loc[0:playernum-1, ['Start Time']].max()), ".6f")) # timestamp of session end

end_ts = float(format(float(match_info.loc[0:playernum-1, ['End Time']].min()), ".6f")) # timestamp of session end

rm = rotation_matrix

## path to SSG positional data
position_data_dir = '/Users/abcd/Desktop/Dataset_A/'

## check data format, necessary columns include 'Timestamp', 'Latitude', 'Longitude'
check_player = PositionalData.check_pitch_columns(position_data_dir) # if necessary columns missing and alternative

## process individual data into team data
ssg = PositionalData.team_tracking(position_data_dir, check_player, start_ts, end_ts, rm, switch_X_Y)

## convert Timestamp into int
ssg["Timestamp"] = ssg["Timestamp"].map(lambda x: x*1000000).astype(int) # for following merging with dummy timeline

ssg.reset_index(drop = True, inplace = True)

## create a 10 Hz dummy timeline starting from 0.1s
dum_timeline = pd.DataFrame({"Timestamp": list(range(int(start_ts*1000000), int(end_ts*1000000)+1, 1))})

dum_timeline["Start [s]"] = dum_timeline.index.map(lambda x: x*0.1)

#%% check data loss

date_loss = PositionalData.check_data_loss(ssg, dum_timeline)

#%% merge the positional data with new timeline

ssg_10Hz = pd.merge(dum_timeline, ssg, on = "Timestamp", how = "outer")

#%% interpolation

ssg_10Hz.interpolate(method="linear", limit_direction="both", inplace=True, axis=0)

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

## a time point of interest, e.g., 2.5s after the session starts
sec = 2.5 # TYPE IN THE MOMENT YOU WOULD LIKE TO SEE

## plot the ocsillation
VisualInspection.plot_pitch_players(pitch_rotated, ssg_10Hz, sec)