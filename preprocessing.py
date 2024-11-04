import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LinearRing

#%% 
class SessionDetails:
    
    ## read information: Date, Category, Format, Team in SSGs, Player Name, Split Start Time, Split End Time
    def read_match_data(match_info_dir, col_to_be_used, colname_start_time, colname_end_time):
        
        match = pd.read_excel(match_info_dir, sheet_name = 1, usecols = col_to_be_used)
        
        ## rename
        column_mapping = {colname_start_time:'Start Time', colname_end_time:'End Time'}
        match = match.rename(columns = column_mapping)
        
        return match
    
    ## parser checking data format
    def check_time_columns(df):
        
        report = {} # create a dictionary
    
        # Check if 'Start Time' column exists
        if 'Start Time' not in df.columns:
            report['Start Time'] = "Missing 'Start Time' column."
        else:
            if not pd.api.types.is_float_dtype(df['Start Time']):
                report['Start Time'] = "'Start Time' column exists but does not contain float values."
            else:
                report['Start Time'] = "'Start Time' column exists and contains float values."
    
        # Check if 'End Time' column exists
        if 'End Time' not in df.columns:
            report['End Time'] = "Missing 'End Time' column."
        else:
            if not pd.api.types.is_float_dtype(df['End Time']):
                report['End Time'] = "'End Time' column exists but does not contain float values."
            else:
                report['End Time'] = "'End Time' column exists and contains float values."
    
        print ('Time Column Check Results:')
        print ('-' * 30)
        for column, result in report.items():
            print(f"{column}: {result}")

    
#%% 
class PitchRotation:
    
    ## parser checking data format
    def check_pitch_columns(df):
        
        report = {} # create a dictionary
    
        # Check if 'longitude' column exists
        if 'Longitude' not in df.columns:
            report['Longitude'] = "Missing 'Longitude' column."
        else:
            if not pd.api.types.is_float_dtype(df['Longitude']):
                report['Longitude'] = "'Longitude' column exists but does not contain float values."
            else:
                report['Longitude'] = "'Longitude' column exists and contains float values."
    
        # Check if 'latitude' column exists
        if 'Latitude' not in df.columns:
            report['Latitude'] = "Missing 'Latitude' column."
        else:
            if not pd.api.types.is_float_dtype(df['Latitude']):
                report['Latitude'] = "'Latitude' column exists but does not contain float values."
            else:
                report['Latitude'] = "'Latitude' column exists and contains float values."
    
        print ('Pitch Coordinates Column Check Results:')
        print ('-' * 30)
        for column, result in report.items():
            print(f"{column}: {result}")
    
    ## map projection
    def coordinates_to_field(df): 
        a = 6378.137
        e = 0.0818192
        k0 = 0.9996
        E0 = 500
        N0 = 0
        lon1 = []
        lat1 = []
        lons = df['Longitude'].to_list()
        lats = df['Latitude'].to_list()
        for i in range(len(df)):
            lon = lons[i]
            lat = lats[i]
            Zonenum = int(lon / 6) + 31
            lamda0 = (Zonenum - 1) * 6 - 180 + 3
            lamda0 = lamda0 * math.pi / 180
            phi = lat * math.pi / 180
            lamda = lon * math.pi / 180
            v = 1 / math.sqrt(1 - e ** 2 * math.sin(phi) ** 2)
            A = (lamda - lamda0) * math.cos(phi)
            T = math.tan(phi) ** 2
            C = e ** 2 * math.cos(phi) * math.cos(phi) / (1 - e ** 2)
            s = (1 - e ** 2 / 4 - 3 * e ** 4 / 64 - 5 * e ** 6 / 256) * phi - \
                (3 * e ** 2 / 8 + 3 * e ** 4 / 32 + 45 * e ** 6 / 1024) * math.sin(2 * phi) + \
                (15 * e ** 4 / 256 + 45 * e ** 6 / 1024) * math.sin(4 * phi) - \
                35 * e ** 6 / 3072 * math.sin(6 * phi)
            UTME = E0 + k0 * a * v * (A + (1 - T + C)*A ** 3 / 6+(5 - 18 * T + T ** 2) * A ** 5 / 120)
            UTMN = N0 + k0 * a * (s + v * math.tan(phi) * (A ** 2 / 2 + (5 - T + 9 * C + 4 * C ** 2) * A ** 4 / 24 + (61 - 58 * T + T ** 2) * A ** 6 / 720))
            UTME = UTME * 1000 # convert UTME (Kilometre) to meter
            UTMN = UTMN * 1000 # convert UTMN (Kilometre) to meter
            lat1.append(UTME)
            lon1.append(UTMN)
        print (lon1)
        print (lat1)
        return pd.DataFrame({'X': lon1
                            , 'Y': lat1})
    
    ## pitch plotting
    def plot_pitch (df):
        
        ini_pitch_x, ini_pitch_y = LinearRing(zip(df['X'], df['Y'])).xy # plot for visualisation (explicitly closed polygon)
        fig = plt.figure()
        plt.plot(ini_pitch_x, ini_pitch_y, "g", alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
        
        return fig
    
    ## establish rotation matrix
    def rotation_matrix (origin, the_other, third_vex, fourth_vex):
        
        dx = abs(float(the_other['X']) - float(origin['X']))
        dy = abs(float(the_other['Y']) - float(origin['Y']))
        angle = np.arctan2(dy, dx) * 180 / np.pi
        
        # Rotation Matrix for clockwise rotating (RW_CW)
        RM_CW = np.array([[np.cos(angle*np.pi/180), -np.sin(angle*np.pi/180)],
                          [np.sin(angle*np.pi/180), np.cos(angle*np.pi/180)]])

        # Rotation Matrix for counter-clockwise rotating (RW_CCW)
        RM_CCW = np.array([[np.cos(angle*np.pi/180), np.sin(angle*np.pi/180)],
                          [-np.sin(angle*np.pi/180), np.cos(angle*np.pi/180)]])
        
        # Clockwise or Counterclockwise rotating
        if float(origin['Y']) < float(the_other['Y']):
            RotationMatrix = RM_CW
        else:
            RotationMatrix = RM_CCW
        
        return RotationMatrix
    
    
    ## apply rotation matrix
    def rotating_vertex (vertex, RM): 
        rotation = np.dot(vertex, RM)
        return rotation[0,0], rotation[0,1]
    
    
    ## switch x and y coordinates (if needed), to make pitch length parallel with x-axis
    def switch_x_y (df):
        
        if df['X'].max() - df['X'].min() < df['Y'].max() - df['Y'].min() : ## if pitch length is parallel with with y-axis, it is needed
            
            df[["X","Y"]] = df[["Y","X"]]
            
            switch_X_Y = "yes" ## indicator, if X and Y in pitch data are switched here, X and Y in player positional data should also be switched
            
            print ("!! Pitch X and Y Coordinates Switched in Dataframe !!")
        
        else: 
    
            print ("** Pitch X and Y Coordinates Stay **")
    
            switch_X_Y = "no"
        
        return df, switch_X_Y
    
    
    
#%%
class PositionalData:
    
    ## parser checking data format
    def check_pitch_columns(file_dir):
        
        file_list = os.listdir(file_dir)
        print (f"{file_list}\n") # check file list
        if '.DS_Store' in file_list:
            file_list.remove('.DS_Store')
            
        for file in file_list:
            print (file)
            path = os.path.join(file_dir, file)
            position = pd.read_csv(path)
        
            report = {} # create a dictionary for reporting
            found_columns = {} # create a dictionary to save the actual column names found in data
            
            print ('Player Coordinates Column Check Results:')
            print ('-' * 30)
            
            # Check if 'Timestamp' column exists
            if 'Timestamp' not in position.columns:
                
                # Look for any column that contains 'timestamp' (case-insensitive)
                possible_timestamps = [col for col in position.columns if 'timestamp' in col.lower()]
                
                found_columns['Timestamp'] = possible_timestamps[0]
                
                print (f"Column {possible_timestamps} in {file} should be renamed to 'Timestamp'")
                
                if not possible_timestamps:
                    report['Timestamp'] = "Missing 'Timestamp' column and no variations found."
                    
            else:
                if not pd.api.types.is_float_dtype(position['Timestamp']):
                    report['Timestamp'] = "'Timestamp' column exists but does not contain float values."
                else:
                    report['Timestamp'] = "'Timestamp' column exists and contains float values."
        
        
        
            # Check if 'Longitude' column exists
            if 'Longitude' not in position.columns:
                
                # Look for any column that contains 'latitude' (case-insensitive)
                possible_longitude = [col for col in position.columns if 'longitude' in col.lower()]
                
                found_columns['Longitude'] = possible_longitude[0]
                
                print (f"Column {possible_longitude} in {file} should be renamed to 'Latitude'")
                
                if not possible_longitude:
                    report['Longitude'] = "Missing 'Longitude' column and no variations found."
                
            else:
                if not pd.api.types.is_float_dtype(position['Longitude']):
                    report['Longitude'] = "'Longitude' column exists but does not contain float values."
                else:
                    report['Longitude'] = "'Longitude' column exists and contains float values."
        
        
        
            # Check if 'Latitude' column exists
            if 'Latitude' not in position.columns:
                
                # Look for any column that contains 'latitude' (case-insensitive)
                possible_latitude = [col for col in position.columns if 'latitude' in col.lower()]
                
                found_columns['Latitude'] = possible_latitude[0]
                
                print (f"Column {possible_latitude} in {file} should be renamed to 'Latitude'")
                
                if not possible_latitude:
                    report['Latitude'] = "Missing 'Latitude' column and no variations found."
                
            else:
                if not pd.api.types.is_float_dtype(position['Latitude']):
                    report['Latitude'] = "'Latitude' column exists but does not contain float values."
                else:
                    report['Latitude'] = "'Latitude' column exists and contains float values."
        
        
        
            for column, result in report.items():
                print(f"{column}: {result}")
            print ("\n")
            
        return found_columns
            
    
    def team_tracking(file_dir, check_player, StartTS, EndTS, RM, switch_X_Y):
        file_list = os.listdir(file_dir)
        print (f"{file_list}\n") # check file list
        if '.DS_Store' in file_list:
            file_list.remove('.DS_Store')
        
        TeamPosition = pd.DataFrame() # create a DataFrame for later use
        
        # for each player, carry out Column Renaming, Subsetting, Map Projection, Calibration (using rotation matrix)
        for file in file_list:
            print (file)
            path = os.path.join(file_dir, file)
            position = pd.read_csv(path) # read useful columns
            
            required_columns = ['Timestamp', 'Latitude', 'Longitude']
            
            # rename columns if needed
            if any(col not in position.columns for col in required_columns):
                
                check_player_reversed = {value: key for key, value in check_player.items()}
                
                position = position.rename(columns = check_player_reversed)
                
                print (position.columns)
            
            # check if all three are included and select columnns if they all exist
            missing_columns = [col for col in required_columns if col not in position.columns]
            
            if missing_columns:
                print(f"Still missing columns: {missing_columns}")
                
            else:
                position = position[required_columns]
            
            # round to floats with six decimals
            position['Timestamp'] = position['Timestamp'].round(6)
            
            
            if len(position.loc[position['Timestamp'] == StartTS]) >= 1: # if start timestamp is found
                StartIndex = position.loc[position['Timestamp'] == StartTS].index[0] # get StartIndex from position data
                print (f"StartIndex matched in the first place: {StartIndex}")
            else:
                for i in range (1, 10):         
                    if len(position.loc[(position['Timestamp'] * 1000000).astype(int) == int(StartTS*1000000)+i]) >= 1: # if the data at StartTS got lost, then start from next timestamp
                        StartIndex = position.loc[(position['Timestamp'] * 1000000).astype(int) == int(StartTS*1000000)+i].index[0]
                        print (f"StartIndex matched by further digging: {StartIndex}")
                        break
                    else:
                        print (f"StartIndex {StartTS+i*0.000001} Not Found")
                        
            if len(position.loc[position['Timestamp'] == EndTS]) >= 1: # if end timestamp is found
                EndIndex = position.loc[position['Timestamp'] == EndTS].index[-1] # get EndIndex from position data
                print (f"EndIndex matched in the first place: {EndIndex}")
            else: 
                for i in range (1, 10):
                    if len(position.loc[(position['Timestamp'] * 1000000).astype(int) == int(EndTS*1000000)-i]) >= 1: # if the data at EndTS got lost, the end at last timestamp
                        EndIndex = position.loc[(position['Timestamp'] * 1000000).astype(int) == int(EndTS*1000000)-i].index[-1]
                        print (f"EndIndex matched by further digging: {EndIndex}")
                        break
                    else:
                        print (f"EndIndex {EndTS+i*0.000001} Not Found")
            
            ## subsetting by StartIndex and EndIndex
            position = position.iloc[StartIndex:EndIndex+1,:]
            print (f"StartIndex: {StartIndex}")
            print (f"EndIndex: {EndIndex}")
            print (position)
            
            ## map projection
            a = 6378.137
            e = 0.0818192
            k0 = 0.9996
            E0 = 500
            N0 = 0
            lon1 = []
            lat1 = []
            lons = position['Longitude'].to_list()
            lats = position['Latitude'].to_list()
            
            for k in range(len(position)):
                lon = lons[k]
                lat = lats[k]
                Zonenum = int(lon / 6) + 31
                lamda0 = (Zonenum - 1) * 6 - 180 + 3
                lamda0 = lamda0 * math.pi / 180
                phi = lat * math.pi / 180
                lamda = lon * math.pi / 180
                v = 1 / math.sqrt(1 - e ** 2 * math.sin(phi) ** 2)
                A = (lamda - lamda0) * math.cos(phi)
                T = math.tan(phi) ** 2
                C = e ** 2 * math.cos(phi) * math.cos(phi) / (1 - e ** 2)
                s = (1 - e ** 2 / 4 - 3 * e ** 4 / 64 - 5 * e ** 6 / 256) * phi - \
                    (3 * e ** 2 / 8 + 3 * e ** 4 / 32 + 45 * e ** 6 / 1024) * math.sin(2 * phi) + \
                    (15 * e ** 4 / 256 + 45 * e ** 6 / 1024) * math.sin(4 * phi) - \
                    35 * e ** 6 / 3072 * math.sin(6 * phi)
                UTME = E0 + k0 * a * v * (A + (1 - T + C)*A ** 3 / 6+(5 - 18 * T + T ** 2) * A ** 5 / 120)
                UTMN = N0 + k0 * a * (s + v * math.tan(phi) * (A ** 2 / 2 + (5 - T + 9 * C + 4 * C ** 2) * A ** 4 / 24 + (61 - 58 * T + T ** 2) * A ** 6 / 720))
                
                ### UTME,UTMN based on kilometer. Convert them into meter
                UTME = UTME * 1000
                UTMN = UTMN * 1000
                lat1.append(UTME)
                lon1.append(UTMN)

            position["X"] = lon1
            position["Y"] = lat1
            
            ## calibrate player positional data
            for i in range (len(position)):
                pos = position.iloc[[i], [3,4]]
                position.iloc[[i], [3, 4]] = np.dot(pos, RM)
            
            ## use indicator to switch X, Y or not
            if switch_X_Y == "yes": # Whether or not switch X and Y here depends on whether pitch X, Y have been switched
                position[["X", "Y"]] = position[["Y", "X"]]
                print ("!! Position data X, Y switched, because it was switched in pitch coordinates !!")
            else:
                print ("** Not Switching X, Y in position data, because it was not switched in pitch coordinates either **")
            
            ## whether each timestamp is unique?
            if len(position["Timestamp"].unique()) != len(position):
                print ("!! Same Timestamp Occurs !!")
            
            position.drop(columns=["Latitude", "Longitude"], inplace = True)
            
            ## amend column name
            playername = file[12:16] # extract player name
            position.columns = ["Timestamp", "{}_x".format(playername), "{}_y".format(playername)]
            
            ## integrate into team positional dataset (full outer join)
            if file_list.index(file) == 0:
                TeamPosition = position
            else:
                TeamPosition = pd.merge(TeamPosition, position, on = 'Timestamp', how = 'outer')
        
        TeamPosition.sort_values(by = 'Timestamp', axis=0, ascending = True, inplace = True)
        
        TeamPosition.reset_index(drop = True)
        
        print (TeamPosition)
        
        return TeamPosition
    
    
    def check_data_loss(ssg, dum_timeline):
        
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
    
    
#%%
class VisualInspection:
    
    def plot_pitch_players (pitch, players, sec):
        ini_pitch_x, ini_pitch_y = LinearRing(zip(pitch['X'], pitch['Y'])).xy # plot for visualisation (explicitly closed polygon)
        fig = plt.figure()
        plt.plot(ini_pitch_x, ini_pitch_y, "g", alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
        x_col = [c for c in players.columns if "_x" in c]
        y_col = [c for c in players.columns if "_y" in c]
        plt.scatter(players.loc[sec*10][x_col], players.loc[sec*10][y_col])
        plt.suptitle(str(sec) + "s")
        
        return fig


