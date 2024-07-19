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

This sections reads session detials including columns of Date, Category, Format, Team in SSGs, Player Name, Split Start Time, Split End Time.

An example provided below:

	Date	Category	Format	Number of team 	Player Name	Split Start Time	Split End Time
0	44519	U-18	6 v 6 	A	ID_1	44519.746692731	44519.747584907
1	44519	U-18	6 v 6 	A	ID_2	44519.746692731	44519.747584907
2	44519	U-18	6 v 6 	A	ID_3	44519.746692731	44519.747584907
3	44519	U-18	6 v 6 	A	ID_4	44519.746692731	44519.747584907
4	44519	U-18	6 v 6 	A	ID_5	44519.746692731	44519.747584907
5	44519	U-18	6 v 6 	A	ID_6	44519.746692731	44519.747584907


Timestamp info will be used for subsetting positional data of interest later.

'''

match_info_dir = ' TEXT THE PATH OF YOUR FILE HERE '

match_info = SessionDetails.read_match_data(match_info_dir)

#%% read pitch location
'''

This section reads the latitude and longitude coordinates of pitch corners

An example provided below:
    	longitude	latitude
0	-9.12436877	    41.72674194
1	-9.123890745	41.72592757
2	-9.123290669	41.72612579
3	-9.12376968	    41.72693916

'''

pitch = pd.read_csv(" TEXT THE PATH OF YOUR FILE HERE ")

#%% map projection

'''

This section is for converting geographic coordinates to cartesian coordinates, visual inspection option is provided.

'''

ini_xyco_pitch = PitchRotation.coordinates_to_field(pitch) # get coordinates(x, y) of pitch

PitchRotation.plot_pitch(ini_xyco_pitch) # plot the pitch after map projection

#%% rotation matirx calculation

'''

This section is to align picth length and width with x-axis and y-axis respectively, for following goal-to-goal or side-to-side analysis.

Rotation matrix computed from rotating pitch will also to calibrate player positional data.

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
    
print (f"Rotated pitch: {pitch_rotated}") # get rotated pitch vextices

PitchRotation.plot_pitch(pitch_rotated) # plot the pitch after rotation

## check if it is needed to switch X and Y in both position and pitch data (to make pitch length parallel with x-axis)
pitch_rotated, switch_X_Y = PitchRotation.switch_x_y(pitch_rotated)

#%% process individual positional data

playernum = 6 # num of players for each side

start_ts = float(format(float(match_info.loc[0:playernum-1, ['Split Start Time']].max()), ".6f")) # timestamp of session end

end_ts = float(format(float(match_info.loc[0:playernum-1, ['Split End Time']].min()), ".6f")) # timestamp of session end

rm = rotation_matrix

## path to SSG positional data
position_data_dir = '/Users/abcd/Documents/Liverpool/Manuscript-Tactical/github/Dataset_A/'

ssg = PositionalData.team_tracking(position_data_dir, start_ts, end_ts, rm, switch_X_Y)

ssg["Timestamp"] = ssg["Timestamp"].map(lambda x: x*1000000).astype(int) # convert Timestamp into int, for following merging with dummy timeline
ssg.reset_index(drop = True, inplace = True)

## create a 10 Hz dummy timeline starting from 0.1s
dum_timeline = pd.DataFrame({"Timestamp": list(range(int(start_ts*1000000), int(end_ts*1000000)+1, 1))})

dum_timeline["Start [s]"] = dum_timeline.index.map(lambda x: x*0.1)


#%% check data loss

## the number of rows with NaN value (partial data loss)
print (f"Partial data loss: {len(ssg[ssg.isnull().T.any()])},\n Percent: {len(ssg[ssg.isnull().T.any()]) / len(dum_timeline)}")

## the number of missing timestamps (complete data loss)
print (f"Complete data loss: {len(dum_timeline) - len(ssg)},\n Percent: {(len(dum_timeline) - len(ssg)) / len(dum_timeline)}")

## count consecutive NaNs
nans = []

for player in ssg.columns[[1, 3, 5, 7, 9, 11]]:
    
    null_list = list(ssg[ssg[player].isnull()].index)
    
    for i in null_list:
        
        if null_list.index(i) == len(null_list) - 1:
            
            break
        
        elif null_list.index(i) != len(null_list) - 1 and i+1 == null_list[null_list.index(i)+1]:
            
            nans.append("2 NaNs")
            
            print ("!2 NaNs found!")
            
            if null_list.index(i) != len(null_list) - 2 and i+2 == null_list[null_list.index(i)+2]:
                
                nans.append("3 NaNs")
                
                print ("!!3 NaNs found!!")
                
                if null_list.index(i) != len(null_list) - 3 and i+3 == null_list[null_list.index(i)+3]:
                    
                    nans.append("4 NaNs")
                    
                    print ("!!!4 NaNs found!!!")
                    
                    if null_list.index(i) != len(null_list) - 4 and i+4 == null_list[null_list.index(i)+4]:
                        
                        nans.append("5 NaNs")
                        
                        print (f"!!!!5 NaNs found!!!! index = {i}")
                        
                        if null_list.index(i) != len(null_list) - 5 and i+5 == null_list[null_list.index(i)+5]:
                            
                            nans.append("6 NaNs")
                            
                            print (f"!!!!6 NaNs found!!!! index = {i}")

print ("2 consecutive NaNs:", nans.count("2 NaNs") - nans.count("3 NaNs")) # 2 consecutive NaNs

print ("3 consecutive NaNs", nans.count("3 NaNs") - nans.count("4 NaNs")) # 3 consecutive NaNs

print ("4 consecutive NaNs", nans.count("4 NaNs") - nans.count("5 NaNs")) # 4 consecutive NaNs

print ("5 consecutive NaNs", nans.count("5 NaNs") - nans.count("6 NaNs")) # 5 consecutive NaNs


#%% merge the positional data with new timeline

ssg_10Hz = pd.merge(dum_timeline, ssg, on = "Timestamp", how = "outer")


#%% interpolation

ssg_10Hz.interpolate(method="linear", limit_direction="both", inplace=True, axis=0)


#%% data smoothing

for col in range (2, playernum*2+2):
    ssg_10Hz.iloc[0:, col] = signal.savgol_filter(ssg_10Hz.iloc[0:, col], window_length = 7, polyorder = 1)
print ("Smoothing Finished")


#%% visual inspection

sec = 2.5 # the time point of the session of interest, e.g., 2.5s after the session starts

VisualInspection.plot_pitch_players(pitch_rotated, ssg_10Hz, sec)

