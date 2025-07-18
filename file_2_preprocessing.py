import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

from shapely.geometry import LinearRing
from datetime import datetime, date, timedelta

#%%
class FileDetection:
    
    
    def detect_file_folder_name(folder_path):

        # Get all items in the folder, ignoring .DS_Store
        file_list = [f for f in os.listdir(folder_path) if f != '.DS_Store']
    
        # Detect position data folder: is a directory and contains 'pos'
        position_folders = [f for f in file_list if os.path.isdir(os.path.join(folder_path, f)) and 'pos' in f.lower()]
        if not position_folders:
            raise FileNotFoundError("No positional data folder found.")
        position_data_folder_name = position_folders[0]
    
        # Detect pitch file
        pitch_files = [f for f in file_list if 'pit' in f.lower() and '~' not in f.lower()]
        if not pitch_files:
            raise FileNotFoundError("No pitch file found.")
        pitch_file_name = pitch_files[0]
    
        # Detect session file
        session_files = [f for f in file_list if 'ses' in f.lower() and '~' not in f.lower()]
        if not session_files:
            raise FileNotFoundError("No session file found.")
        session_file_name = session_files[0]
    
        # Inform user
        print("\n" + '-' * 30 + "\n")
        print("Following files/folder are identified for processing:\n")
        print(f"'{position_data_folder_name}' -> The folder containing all positional data\n")
        print(f"'{pitch_file_name}' -> The file containing pitch coordinates\n")
        print(f"'{session_file_name}' -> The file containing start & end time\n")
        
        return session_file_name, pitch_file_name, position_data_folder_name
        

#%% 
class SessionDetails:
    
    ## read information: Date, Category, Format, Team in SSGs, Player Name, Split Start Time, Split End Time
    def read_match_data(folder_path, filename_session):
        
        '''
        read_match_data(match_info_dir, colname_start_time, colname_end_time):
        read tracking data for game_id and return as a DataFrame. 
        teamname is the name of the team in the filename. For the sample data this is either 'Home' or 'Away'.
        '''
        if filename_session.lower().endswith(".csv"):
            
            match = pd.read_csv(os.path.join(folder_path, filename_session), index_col=False)
            
        if filename_session.lower().endswith((".xls", ".xlsx")):
        
            match = pd.read_excel(os.path.join(folder_path, filename_session), sheet_name = 0, index_col=False)
        
        ## select columns of interest
        match.columns = match.columns.str.strip()
        
        colname_start_time_list = [s for s in match.columns if "start" in s.lower()]
        if not colname_start_time_list:
            raise FileNotFoundError("No column 'Start time' found.")
        colname_start_time = colname_start_time_list[0]
            
        colname_end_time_list = [s for s in match.columns if "end" in s.lower()]
        if not colname_end_time_list:
            raise FileNotFoundError("No column 'End time' found.")
        colname_end_time = colname_end_time_list[0]
        
        ## rename
        column_mapping = {colname_start_time:'Start Time', colname_end_time:'End Time'}
        match = match.rename(columns = column_mapping)
        
        return match
    
    
    ## parser checking data format
    def check_time_columns(df):
        
        report = {} # create a dictionary
    
        # Check if 'Start Time' column exists
        if 'Start Time' not in df.columns:
            report['Start Time'] = "Error: Missing 'Start Time' column."
        
        else:
            if not pd.api.types.is_float_dtype(df['Start Time']): # if it does not contain float values
                report['Start Time'] = "[OK] 'Start Time' column exists. \n"
                time_format = "datetime-time"
                
                #df['Start Time'] = pd.to_datetime(df['Start Time'], format="%H:%M:%S.%f").dt.time
            
            elif all(isinstance(x, float) and len(str(x).split('.')[-1]) > 3 for x in df['Start Time']): # if it contains float values with more than three digits
                report['Start Time'] = "[OK] 'Start Time' column exists and contains Unix formatted timestamps. \n"
                time_format = "Unix"
                
            else:
                raise ValueError(f"Unsupported time format: {time_format}")
        
        
        # Check if 'End Time' column exists
        if 'End Time' not in df.columns:
            report['End Time'] = "Error: Missing 'End Time' column."
            
        else:
            if not pd.api.types.is_float_dtype(df['End Time']):
                report['End Time'] = "'End Time' column exists. \n"
                
                df['End Time'] = pd.to_datetime(df['End Time'], format="%H:%M:%S.%f").dt.time
            else:
                report['End Time'] = "[OK] 'End Time' column exists and contains float values. \n"
        
        print ("\n" + '-' * 30 + "\n")
        print ('Time Column Check Results: \n')
        
        print (f"Timestamp format: '{time_format}' \n")
        
        for column, result in report.items():
            print(f"{column}: {result}")
        
        return time_format

    
#%% 
class PitchRotation:
    
    def read_pitch(folder_path, filename_pitch):
        
        if filename_pitch.lower().endswith(".csv"):
            
            pitch = pd.read_csv(os.path.join(folder_path, filename_pitch), index_col=False)
            
        elif filename_pitch.lower().endswith((".xls", ".xlsx")):
            
            pitch = pd.read_excel(os.path.join(folder_path, filename_pitch), index_col=False)
            
        else:
            raise ValueError("Unsupported file type. Please use a .csv or .xls/.xlsx file.")
            
        return pitch
            
    
    ## parser checking data format
    def check_pitch_columns(df):
        
        report = {} # create a dictionary
        
        if 'Longitude' not in df.columns:
            
            # Find a column name that likely represents longitude
            actual_lon_col_names = [c for c in df.columns if 'lon' in c.strip().lower()]
            
            if actual_lon_col_names:
                actual_lon_col_name = actual_lon_col_names[0]  # take the first match
                
                ## rename
                df = df.rename(columns = {actual_lon_col_name: 'Longitude'})
            
                report["Checking column 'Longitude'"] = (f"[OK] '{actual_lon_col_name}' is successfully found and used for processing, "
                                                         f"although Column 'Longitude' is missing in original file:)\n"
                                                         f"'{actual_lon_col_name}' has been renamed to 'Longitude' in the processed data. "
                                                         f"Please double check letter case in later uses.\n\n"
                                                         )
            else:
                report["Checking column 'Longitude'"] = "Error: Column 'Longitude' is missing and no similar column found. Please make sure column 'Longitude' exists.\n"
                
                
        if 'Latitude' not in df.columns:
            
            # Find a column name that likely represents longitude
            actual_lat_col_names = [c for c in df.columns if 'lat' in c.strip().lower()]
            
            if actual_lat_col_names:
                actual_lat_col_name = actual_lat_col_names[0]  # take the first match
                
                ## rename
                df = df.rename(columns = {actual_lat_col_name: 'Latitude'})
                
                report["Checking column 'Latitude'"] = (f"[OK] '{actual_lat_col_name}' is successfully found and used for processing, "
                                                        f"although Column 'Latitude' is missing in original file:)\n"
                                                        f"'{actual_lat_col_name}' has been renamed to 'Latitude' in the processed data. "
                                                        f"Please double check letter case in later uses.\n\n"
                                                        )
            else:
                report["Checking column 'Latitude'"] = "Error: Column 'Latitude' is missing and no similar column found. Please make sure column 'Latitude' exists.\n"
        
        
        if 'Longitude' in df.columns:
            
            if not pd.api.types.is_float_dtype(df['Longitude']):
                report['Data Type: Longitude'] = "Error: Column 'Longitude' now exists but does not contain float values.\n"
            else:
                report['Data Type: Longitude'] = "[OK] Column 'Longitude' now exists and contains float values. Ready to go.\n"
        
        
        if 'Latitude' in df.columns:
            
            if not pd.api.types.is_float_dtype(df['Latitude']):
                report['Data Type: Latitude'] = "Error: Column 'Latitude' now exists but does not contain float values.\n"
            else:
                report['Data Type: Latitude'] = "[OK] Column 'Latitude' now exists and contains float values. Ready to go.\n"
        
    
        print ('\n Pitch Coordinates Column Check Results:')
        print ('-' * 30)
        for column, result in report.items():
            print(f"{column}: {result}")
            
        return df
    
    
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
        print ("\n" + '-' * 30 + "\n")
        print ("[OK] Pitch coordinates successfully converted to Cartesian coordinates \n")
        #print (lon1)
        #print (lat1)
        return pd.DataFrame({'X': lon1
                            , 'Y': lat1})
    
    ## pitch plotting
    def plot_pitch (df, fig_name):
        
        """
        Plots a pitch outline using X and Y coordinates from a DataFrame.
        
        Parameters:
        - df: pandas DataFrame with 'X' and 'Y' columns representing pitch coordinates.
        - fig_name: filename to save the figure as (default: 'pitch_plot.png').
        
        Returns:
        - matplotlib Figure object
        """
        
        ini_pitch_x, ini_pitch_y = LinearRing(zip(df['X'], df['Y'])).xy # plot for visualisation (explicitly closed polygon)
        
        # fig = plt.figure()
        # plt.plot(ini_pitch_x, ini_pitch_y, "g", alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
        # plt.title(f"{fig_name}")
        
        fig, ax = plt.subplots()
        ax.plot(ini_pitch_x, ini_pitch_y, "g", alpha=0.7, linewidth=3,
                solid_capstyle='round', zorder=2)
        ax.set_title(f"{fig_name}")
        #ax.set_aspect('equal')
        #ax.axis("off")
        
        plt.savefig(f"{fig_name}.png", bbox_inches="tight")
        
        return fig
    
    
    ## establish rotation matrix
    def rotation_matrix (origin, the_other, third_vex, fourth_vex):
        
        dx = abs(float(the_other['X']) - float(origin['X']))
        dy = abs(float(the_other['Y']) - float(origin['Y']))
        angle = np.arctan2(dy, dx) * 180 / np.pi
        
        # Rotation Matrix for counuterclockwise rotating (RW_CCW)
        RM_CCW = np.array([[np.cos(angle*np.pi/180), -np.sin(angle*np.pi/180)],
                          [np.sin(angle*np.pi/180), np.cos(angle*np.pi/180)]])

        # Rotation Matrix for clockwise rotating (RW_CW)
        RM_CW = np.array([[np.cos(angle*np.pi/180), np.sin(angle*np.pi/180)],
                          [-np.sin(angle*np.pi/180), np.cos(angle*np.pi/180)]])
        
        # Clockwise or Counterclockwise rotating
        if float(origin['Y']) < float(the_other['Y']):
            RotationMatrix = RM_CW
        else:
            RotationMatrix = RM_CCW
        
        return RotationMatrix
    
    
    ## apply rotation matrix
    def rotating_vertex (RM, vertex): 
        rotation = np.dot(RM, vertex.T)
        return rotation[0,0], rotation[1,0]
    
    
    ## switch x and y coordinates (if needed), to make pitch length parallel with x-axis
    def switch_x_y (df):
        
        if df['X'].max() - df['X'].min() < df['Y'].max() - df['Y'].min() : ## if pitch length is parallel with with y-axis, it is needed
            
            df[["X","Y"]] = df[["Y","X"]]
            
            switch_X_Y = "yes" ## indicator, if X and Y in pitch data are switched here, X and Y in player positional data should also be switched
            
            print ("\n [OK] ** Pitch X and Y Coordinates Switched in Dataframe 'Pitch'. This is to ensure pitch length parallel with x-axis. **")
        
        else: 
    
            print ("\n [OK] ** Pitch length is parallel with x-axis. Pitch X and Y Coordinates Stay **")
    
            switch_X_Y = "no"
        
        return df, switch_X_Y
    
    
    
#%%
class PositionalData:
    
    ## parser checking data format
    def check_pitch_columns(file_dir):
        
        file_list = os.listdir(file_dir)
    
        if '.DS_Store' in file_list:
            file_list.remove('.DS_Store')
        
        print("\n" + "=" * 50 + "\n")
        print ("Following files found in directory:\n")
        print (*file_list, sep="\n") # check file list
        print ("\n\n") # blank lines after the list
            
        for file in file_list:
            print (file + "\n")
            path = os.path.join(file_dir, file)
            position = pd.read_csv(path, index_col=False)
        
            report = {} # create a dictionary for reporting
            found_columns = {} # create a dictionary to save the actual column names found in data
            
            print ('Player Coordinates Column Check Results:')
            print ('-' * 30)
            
            # Check if 'Timestamp' column exists
            if 'Timestamp' not in position.columns:
                    
                # Look for any column that contains 'timestamp' (case-insensitive)
                possible_timestamps = [col for col in position.columns if 'time' in col.strip().lower()]
                
                if possible_timestamps: 
                
                    found_columns['Timestamp'] = possible_timestamps[0]
                
                    print (f"[OK] Friendly reminder: Column '{possible_timestamps[0]}' in {file} will be renamed to 'Timestamp' in further processing. No action needed. Please double check column format in future uses.\n")
                
                else:
                    report['Timestamp'] = "Error: Missing column 'Timestamp' and no alternative column found."
                    
            else:
                if not pd.api.types.is_float_dtype(position['Timestamp']):
                    report['Timestamp'] = "[OK] Column 'Timestamp' contains non-float values."
                else:
                    report['Timestamp'] = "[OK] Column 'Timestamp' exists and contains float values."
        
        
        
            # Check if 'Longitude' column exists
            if 'Longitude' not in position.columns:
                
                # Look for any column that contains 'latitude' (case-insensitive)
                possible_longitude = [col for col in position.columns if 'lon' in col.strip().lower()]
                
                if possible_longitude:
                
                    found_columns['Longitude'] = possible_longitude[0]
                
                    print (f"[OK] Friendly reminder: Column '{possible_longitude[0]}' in {file} will be renamed to 'Longitude' in further processing. No action needed. Please double check column format in future uses.\n")
                
                else:
                    report['Longitude'] = "Error: Missing column 'Longitude' and no alternative column found."
                
            else:
                if not pd.api.types.is_float_dtype(position['Longitude']):
                    report['Longitude'] = "Error: Column 'Longitude' exists but does not contain float values."
                else:
                    report['Longitude'] = "[OK] Column 'Longitude' exists and contains float values."
        
        
        
            # Check if 'Latitude' column exists
            if 'Latitude' not in position.columns:
                
                # Look for any column that contains 'latitude' (case-insensitive)
                possible_latitude = [col for col in position.columns if 'lat' in col.strip().lower()]
                
                if possible_latitude:
                
                    found_columns['Latitude'] = possible_latitude[0]
                
                    print (f"[OK] Friendly reminder: Column '{possible_latitude[0]}' in {file} will be renamed to 'Latitude' in further processing. No action needed. Please double check column format in future uses.\n")
                
                else:
                    report['Latitude'] = "Error: Missing column 'Latitude' and no alternative column found."
                
            else:
                if not pd.api.types.is_float_dtype(position['Latitude']):
                    report['Latitude'] = "Error: Column 'Latitude' exists but does not contain float values."
                else:
                    report['Latitude'] = "[OK] Column 'Latitude' exists and contains float values."
            
            
            # Print report for each dataset
            for column, result in report.items():
                print(f"{column}: {result}")
            
            # Global check for each dataset
            if any("Error:" in str(v) for v in report.values()):
                print(f"\n Error(s) found in {file}. Please see detals above.\n")
            else:
                print (f"\n [OK] {file} is ready to go \n")
                
            print("\n" + "=" * 50 + "\n")
            
        return found_columns
    
    
    
    def identify_start_end_timestamp(match_info, time_format, playernum):
        
        if time_format == "Unix":
            
            start_timestamp = float(format(float(match_info.loc[0:playernum-1, ['Start Time']].max()), ".6f"))
            
            end_timestamp = float(format(float(match_info.loc[0:playernum-1, ['End Time']].min()), ".6f"))
        
        else:
            
            start_timestamp = match_info['Start Time'].value_counts().idxmax()
            
            end_timestamp = match_info['End Time'].value_counts().idxmax()
            
        return start_timestamp, end_timestamp
    
    
    
    def team_tracking(file_dir, check_player, time_format, StartTS, EndTS, RM, switch_X_Y):
        file_list = os.listdir(file_dir)
        
        if '.DS_Store' in file_list:
            file_list.remove('.DS_Store')
        
        TeamPosition = pd.DataFrame() # create a DataFrame for later use
        
        # for each player, carry out Column Renaming, Subsetting, Map Projection, Calibration (using rotation matrix)
        for file in file_list:
            print (f"merging {file} into team data ... \n")
            path = os.path.join(file_dir, file)
            position = pd.read_csv(path, index_col=False) # read useful columns
            
            required_columns = ['Timestamp', 'Latitude', 'Longitude']
            
            # rename columns if needed
            if any(col not in position.columns for col in required_columns):
                
                check_player_reversed = {value: key for key, value in check_player.items()}
                
                position = position.rename(columns = check_player_reversed)
                
                #print (position.columns)
            
            # check if all three are included and select columnns if they all exist
            missing_columns = [col for col in required_columns if col not in position.columns]
            
            if missing_columns:
                print(f"Error: Still missing columns: {missing_columns} \n")
                
            else:
                position = position[required_columns]
            
            
            ## for Unix formatted timestamp
            if time_format == "Unix":
            
                # round to floats with six decimals
                position['Timestamp'] = position['Timestamp'].round(6)
                
                # look for start timestamp
                if len(position.loc[position['Timestamp'] == StartTS]) >= 1: # if start timestamp is found
                    StartIndex = position.loc[position['Timestamp'] == StartTS].index[0] # get StartIndex from position data
                    print (f"[OK] Start timestamp matched: row {StartIndex} \n")
                else:
                    for i in range (1, 10):         
                        if len(position.loc[(position['Timestamp'] * 1000000).astype(int) == int(StartTS*1000000)+i]) >= 1: # if the data at StartTS got lost, then start from next timestamp
                            StartIndex = position.loc[(position['Timestamp'] * 1000000).astype(int) == int(StartTS*1000000)+i].index[0]
                            print (f"[OK] Start timestamp retrieved through further digging: row {StartIndex} \n")
                            break
                        else:
                            print (f"Start timestamp {StartTS+i*0.000001} Not Found in the first searching \n")
                
                # look for end timestamp
                if len(position.loc[position['Timestamp'] == EndTS]) >= 1: # if end timestamp is found
                    EndIndex = position.loc[position['Timestamp'] == EndTS].index[-1] # get EndIndex from position data
                    print (f"[OK] End timestamp matched: row {EndIndex} \n")
                else: 
                    for i in range (1, 10):
                        if len(position.loc[(position['Timestamp'] * 1000000).astype(int) == int(EndTS*1000000)-i]) >= 1: # if the data at EndTS got lost, then end at last timestamp
                            EndIndex = position.loc[(position['Timestamp'] * 1000000).astype(int) == int(EndTS*1000000)-i].index[-1]
                            print (f"[OK] End timestamp retrieved through further digging: row {EndIndex} \n")
                            break
                        else:
                            print (f"End timestamp {EndTS+i*0.000001} Not Found in the first searching \n")
            
            
            ## for datetime-time formatted timestamp
            if time_format == "datetime-time":
                
                ## for datetime-time timestamp
                position['Timestamp'] = pd.to_datetime(position['Timestamp'], format="%H:%M:%S.%f").dt.time
                
                # look for start timestamp
                if len(position.loc[position['Timestamp'] == StartTS]) >= 1: # if start timestamp is found
                    StartIndex = position.loc[position['Timestamp'] == StartTS].index[0] # get StartIndex from position data
                    print (f"[OK] Start timestamp matched: row {StartIndex} \n")
                else:
                    print (f"Error: Start timestamp {StartTS} Not Found \n")
                    
                # look for end timestamp
                if len(position.loc[position['Timestamp'] == EndTS]) >= 1: # if start timestamp is found
                    EndIndex = position.loc[position['Timestamp'] == EndTS].index[0] # get StartIndex from position data
                    print (f"[OK] Start timestamp matched: row {EndIndex} \n")
                else:
                    print (f"Error: Start timestamp {EndTS} Not Found \n")
                    
            
            
            ## subsetting by StartIndex and EndIndex to select useful data
            position = position.iloc[StartIndex:EndIndex+1,:]
            
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
                pos = position.iloc[[i], [3,4]].T
                position.iloc[[i], [3, 4]] = np.dot(RM, pos).T
            
            ## use indicator to switch X, Y or not
            if switch_X_Y == "yes": # Whether or not switch X and Y here depends on whether pitch X, Y have been switched
                position[["X", "Y"]] = position[["Y", "X"]]
                print ("[OK] ** Position data X, Y switched to follow the switching of pitch coordinates ** \n ")
            else:
                print ("[OK] ** Position data X, Y reserved to follow pitch coordinates ** \n")
            
            ## whether each timestamp is unique?
            if len(position["Timestamp"].unique()) != len(position):
                print ("!! Error: Same Timestamp Occurs !! \n")
            
            position.drop(columns=["Latitude", "Longitude"], inplace = True)
            
            ## amend column name
            playername = file.strip().split(".")[0].split("_")[1] # extract player name
            position.columns = ["Timestamp", "{}_x".format(playername), "{}_y".format(playername)]
            
            ## integrate into team positional dataset (full outer join)
            if file_list.index(file) == 0:
                TeamPosition = position
            else:
                TeamPosition = pd.merge(TeamPosition, position, on = 'Timestamp', how = 'outer')
                
            print (f"Data from {playername} successfully merged into team data \n")
            print ("\n" + "=" * 50 + "\n")
            
        ##
        TeamPosition = TeamPosition.sort_values(by = 'Timestamp', axis=0, ascending = True).reset_index(drop = True)
        
        print ("Team data successfully merged \n")
        print (TeamPosition)
        
        return TeamPosition
    
    
    
    def create_new_timeline (time_format, ssg, start_ts, end_ts):
        
        ## for Unix formatted timestamp
        if time_format == "Unix":
            
            ## convert Timestamp into int
            ssg["Timestamp"] = ssg["Timestamp"].map(lambda x: x*1000000).astype(int) # to be merged with the dummy timeline
            
            ## create a 10 Hz dummy timeline starting from 0.1s
            dum_timeline = pd.DataFrame({"Timestamp": list(range(int(start_ts*1000000), int(end_ts*1000000)+1, 1))})
            
            ## finalise team dataset
            dum_timeline["Start [s]"] = dum_timeline.index * 0.1
            
        ## for datetime-time timestamp
        elif time_format == "datetime-time":
            
            ## combine with dummy date
            start = datetime.combine(date.today(), start_ts)
            end = datetime.combine(date.today(), end_ts)
            
            ## each sample: 10 Hz leads to each step of 0.1 sec
            step = timedelta(seconds=0.1)
            
            ## create a 10 Hz dummy timeline starting from 0.1s
            dum_timeline = pd.DataFrame({"Timestamp": [(start + i * step).time() for i in range(int((end - start) / step) + 1)]})
            
            # finalise team dataset
            dum_timeline["Start [s]"] = dum_timeline.index * 0.1
            
        else:
            raise ValueError(f"Unsupported time format: {time_format}")
        
        return dum_timeline, ssg
    
    
    
    def check_data_loss (ssg, dum_timeline):
        
        ## the number of rows with NaN value (partial data loss)
        print("-" * 50)
        print("Partial data loss (missing data for some players)")
        
        partial_loss_rows = ssg[ssg.isnull().any(axis=1)]
        partial_loss_count = len(partial_loss_rows)
        total_expected = len(dum_timeline)
    
        print(f"N = {partial_loss_count}")
        print(f"Percent: {partial_loss_count / total_expected:.2%}")
        print("=" * 50)
        
        ## the number of missing timestamps (complete data loss)
        print("-" * 50)
        print("Complete data loss (missing data for all players)")
        
        complete_loss_count = len(dum_timeline) - len(ssg)
        
        print(f"N = {complete_loss_count}")
        print(f"Percent: {complete_loss_count / total_expected:.2%}")
        print("=" * 50)
        
        
        print("-" * 50)
        print("Consecutive NaNs per player")
        
        player_columns = ssg.columns[1::2]  # Select ID*_x columns
        max_consecutive = 6
        consecutive_counts = {n: 0 for n in range(2, max_consecutive + 1)}
        
        for player in player_columns:
            is_nan = ssg[player].isnull()
            group = (is_nan != is_nan.shift()).cumsum()
            runs = is_nan.groupby(group).sum()
            consecutive_nan_runs = runs[runs >= 2]

            for run_length in consecutive_nan_runs:
                for n in range(2, max_consecutive + 1):
                    if run_length == n:
                        consecutive_counts[n] += 1

        for n in range(2, max_consecutive + 1):
            print(f"{n} consecutive NaNs: {consecutive_counts[n]}")

        print("=" * 50)


#%%

class smoothing:
    
    def savitzky_golay(playernum, team_data):
        
        for col in range (2, playernum*2+2):
            
            team_data.iloc[0:, col] = signal.savgol_filter(team_data.iloc[0:, col], window_length = 7, polyorder = 1)
        
        print("\n")
        print("-" * 50)
        print ("Savitzky-Golay Filter Smoothing Finished")
        
        return team_data
    
    
    
    def butterworth_low_path_filter(playernum, team_data, fs, order, cutoff):
        
        """
        - playernum (int): Number of players.
        - team_data (pd.DataFrame): DataFrame containing tracking data, with player X/Y columns starting from column 2.
        - fs (float): Sampling frequency (Hz).
        - order (int): Filter order (e.g., 3 or 4).
        - cutoff (float): Cutoff frequency (Hz).
        """
            
        # Normalize the frequency (cutoff / Nyquist frequency)
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
            
        # Get the filter coefficients
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        
        for col in range (2, playernum*2+2):
            
            team_data.iloc[0:, col] = signal.filtfilt(b, a, team_data.iloc[0:, col])
        
        print("\n")
        print("-" * 50)
        print ("Butterworth Filter Smoothing Finished")
        
        return team_data



#%%
class VisualInspection:
    
    def plot_pitch_players (pitch, players, sec):
        
        ini_pitch_x, ini_pitch_y = LinearRing(zip(pitch['X'], pitch['Y'])).xy # plot for visualisation (explicitly closed polygon)
        
        fig = plt.figure()
        plt.plot(ini_pitch_x, ini_pitch_y, "g", alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
        
        x_cols = [c for c in players.columns if "_x" in c]
        y_cols = [c for c in players.columns if "_y" in c]
        
        # Plot player positions
        x_vals = players.loc[sec * 10, x_cols]
        y_vals = players.loc[sec * 10, y_cols]
        plt.scatter(x_vals, y_vals, color='red', zorder=1)
    
        # Add player labels
        for x_col, y_col in zip(x_cols, y_cols):
            player_id = x_col[:-2]  # Remove "_x" to get ID like 'ID67'
            x = players.loc[sec * 10, x_col]
            y = players.loc[sec * 10, y_col]
            plt.text(x, y, player_id, fontsize=9, ha='center', va='bottom', zorder=4)
    
        plt.suptitle(f"Time (since session started): {sec}s")
        plt.axis('equal')
        
        plt.savefig(f"{sec}s.png", bbox_inches="tight")
        
        return fig


