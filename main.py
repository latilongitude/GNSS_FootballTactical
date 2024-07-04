from preprocessing import SessionDetails
from preprocessing import PitchRotation
from preprocessing import PositionalData

import pandas as pd
import scipy.signal as signal
import matplotlib.pyplot as plt
from shapely.geometry import LinearRing


FILE_NAME =
"""text file to ...
"""
DIR_NAME

#%% read session details
''' 

'''
match_info_dir = '/... FILE PATH .../Dataset_B/ssgdetails_6x6.xlsx'

match_info = SessionDetails.read_match_data(match_info_dir)

#%% read pitch location

pitch = pd.read_csv("/... FILE PATH .../Dataset_C/pitch.csv")

#%% map projection

ini_xyco_pitch = PitchRotation.coordinates_to_field(pitch) # get coordinates(x, y) of pitch

## determine origin and other vertices !! get back to manucsript
ini_xyco_pitch.sort_values(by = 'Y', axis=0, ascending = True, inplace = True)

origin = ini_xyco_pitch[0:2].sort_values(by = 'X', axis=0, ascending=True).iloc[[0]] # origin

the_other = ini_xyco_pitch[0:2].sort_values(by = 'X', axis=0, ascending=True).iloc[[-1]] # the other vertex on x-axis

third_vex = ini_xyco_pitch[2:3]

fourth_vex = ini_xyco_pitch[3:4]

rotation_matrix = PitchRotation.rotation_matrix(origin, the_other, third_vex, fourth_vex) # calculate rotation matrix

## create DataFrame for saving rotated vertices
pitch_rotated = pd.DataFrame(columns = ['X', 'Y'])

## apply rotation matrix to four vertices
for vex in (origin, the_other, third_vex, fourth_vex):
    
    pitch_rotated.loc[len(pitch_rotated)] = PitchRotation.rotating_vertex(vex, rotation_matrix)
    
print (f"Rotated pitch: {pitch_rotated}") # get rotated pitch vextices

# ## plot rotated pitch
# pitch_x, pitch_y = LinearRing(zip(pitch_rotated['X'], pitch_rotated['Y'])).xy
# fig = plt.figure()
# plt.plot(pitch_x, pitch_y, "g", alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)

## check if it needs to switch X and Y in both position and pitch data (to make pitch length parallel with x-axis)
if pitch_rotated['X'].max() - pitch_rotated['X'].min() < pitch_rotated['Y'].max() - pitch_rotated['Y'].min() : ## if pitch length is parallel with with y-axis, it is needed
    
    pitch_rotated[["X","Y"]] = pitch_rotated[["Y","X"]]
    
    print ("!! Pitch X,Y Switched !!")
    
    switch_X_Y = "yes" ## indicator, if X and Y in pitch data are switched here, X and Y in player positional data should also be switched

else: 
    
    print ("** Pitch X,Y Stay **")
    
    switch_X_Y = "no"


#%% process individual positional data

playernum = 6 # num of players for each side

start_ts = float(format(float(match_info.loc[0:playernum-1, ['Split Start Time']].max()), ".6f")) # timestamp of session end

end_ts = float(format(float(match_info.loc[0:playernum-1, ['Split End Time']].min()), ".6f")) # timestamp of session end

rm = rotation_matrix

## path to SSG positional data
position_data_dir = '/... FILE PATH .../Dataset_A/'

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


#%% merging with new timeline

ssg_10Hz = pd.merge(dum_timeline, ssg, on = "Timestamp", how = "outer")


#%% interpolation

ssg_10Hz.interpolate(method="linear", limit_direction="both", inplace=True, axis=0)


#%% data smoothing
def my_funct(a, b=3):
    return a + b

d = my_funct(4) # result 7
d = my_funct(3, b=7) # result in 10

for col in range (2, playernum*2+2):
    ssg_10Hz.iloc[0:, col] = signal.savgol_filter(ssg_10Hz.iloc[0:, col], window_length = 7, polyorder = 1)
print ("Smoothing Finished")

