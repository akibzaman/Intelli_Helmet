import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os.path
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#Read input data
csv1 = pd.read_csv("Input/eegIDRecord.csv")
csv_hr = pd.read_csv("Input/heart_input.csv")

#Create Output Folder
yourpath="Output"
parent_dir = os.path.abspath(os.path.join(yourpath, os.pardir))
path = os.path.join(parent_dir, yourpath)

try:
    os.makedirs(path, exist_ok = True)
    print("Directory '%s' created successfully" % yourpath)
except OSError as error:
    print("Directory '%s' can not be created" % yourpath)

#Initialize a DataFrame
df = pd.DataFrame(columns= ['timestampMs','date','time','date_time'])
# df = pd.DataFrame(columns= ['timestampMs','date','time','second'])

#Copy timestamp from EEG data to DataFrame
df['timestampMs'] = pd.to_datetime(csv1['timestampMs'], unit='ms')
# print (df)

#Convert timestamp to UTC date and time
df['timestampMs'] = pd.to_datetime(df.timestampMs)
## Adding Hours
hours_to_add = 6 #Defining the time zone UTC+06
df['timestampMs'] = df['timestampMs'] + timedelta(hours = hours_to_add) #Converting to local time zone
df['date'] = df['timestampMs'].dt.strftime('%m/%d/%Y')
df['time'] = df['timestampMs'].dt.strftime('%H:%M')
# print ( df['time'].dtypes)

#Convert timestamp to UTC date and time
csv1['timestampMs'] = pd.to_datetime(csv1['timestampMs'], unit='ms')
csv1['timestampMs'] = csv1['timestampMs'] + timedelta(hours = hours_to_add)
# print (csv1.head())

#Merge temporary dataframe with EEG data
merged_data_eeg = pd.DataFrame
merged_data_eeg = csv1.merge(df,on=["timestampMs"])
# print(merged_data_eeg)

#Matching the date format in Heart Rate data
csv_hr['date'] = pd.to_datetime(csv_hr.date)
csv_hr['date'] = csv_hr['date'].dt.strftime('%m/%d/%Y')
print (csv_hr.head())

#Merge all data on same date and time
merged_data_all = pd.DataFrame
merged_data_all = merged_data_eeg.merge(csv_hr,on=["date","time"])

#Create Timestamp in nano second
merged_data_all['timestampMs'] = merged_data_all['timestampMs'] - timedelta(hours = hours_to_add) #Converting to UTC
merged_data_all['timestampMs'] = merged_data_all.timestampMs.values.astype(np.int64)              #Converting to Timestamp ns
merged_data_all.rename(columns = {'timestampMs':'timestampNs'}, inplace = True)

merged_data_all['date_time'] = merged_data_all['time'] + " " + merged_data_all['date']

print(merged_data_all.dtypes)
# print(merged_data_all)

#Create new .csv files for processing
merged_data_all.to_csv("Output/heart_rate.csv", index= None, columns=['date_time','heartRate'])
merged_data_all.to_csv("Output/alpha.csv", index= None, columns=['date_time','alphaLow','alphaHigh'])
merged_data_all.to_csv("Output/beta.csv", index= None, columns=['date_time','betaLow','betaHigh'])
merged_data_all.to_csv("Output/model_input.csv", index= "Index",    columns=['timestampNs','attention','meditation','blinkStrength','delta','theta','alphaLow','alphaHigh','betaLow','betaHigh','gammaLow','gammaMid','heartRate'])
merged_data_all.to_csv("Flask/user.csv", index= None, columns=['timestampNs','poorSignal','heartRate','alphaLow','alphaHigh','betaLow','betaHigh','attention','meditation','blinkStrength'])

heart_merge = pd.read_csv("Output/heart_rate.csv")
hrlist=[];
for x in range(len(heart_merge)-1):
  if heart_merge['heartRate'].iloc[x] == heart_merge['heartRate'].iloc[x+1]:
      hrlist.append(x+1)

heart_merge.drop(index=heart_merge.index[hrlist]).to_csv("Output/heart_rate.csv", index= None, columns=['date_time','heartRate'])

#Initialize the connection with google sheet
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('Intelli helmet.json', scope)
client = gspread.authorize(credentials)

#Open Google sheet files
spreadsheet_heart = client.open('heart_rate')
spreadsheet_alpha = client.open('sheet_alpha')
spreadsheet_beta = client.open('sheet_beta')

#Upload csv data to google sheet
with open('Output/heart_rate.csv', 'r') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet_heart.id, data=content)
with open('Output/alpha.csv', 'r') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet_alpha.id, data=content)
with open('Output/beta.csv', 'r') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet_beta.id, data=content)
