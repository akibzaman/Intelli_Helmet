from flask import Flask, render_template, url_for, request, redirect
from flask_mysqldb import MySQL
import pandas as pd
import numpy as np
import os.path
import pickle
import statistics
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)


#Create Output Folder
yourpath="Report"
parent_dir = os.path.abspath(os.path.join(yourpath, os.pardir))
path = os.path.join(parent_dir, yourpath)

try:
    os.makedirs(path, exist_ok = True)
    print("Directory '%s' created successfully" % yourpath)
except OSError as error:
    print("Directory '%s' can not be created" % yourpath)

col_names = ['index','Time','Attention', 'Mediation','Blinkstrength', 'Delta','Theta', 'Alphalow', 'AlphaHigh',
             'Betalow', 'Betahigh', 'GamaLow', 'GamaMid','Heartrate','Status']

user_data='Output/Output_3/model_input.csv'
user_data='Output/model_input.csv'
dataset = pd.read_csv(user_data, header=None, names=col_names)

dataset = dataset.iloc[1:]
# print(dataset.head())
# read_data = pd.read_csv('Output/Output_3/model_input.csv')
read_data = pd.read_csv('Output/model_input.csv')
# print(read_data)

feature_cols = ['Time','Attention', 'Mediation','Blinkstrength', 'Delta','Theta', 'Alphalow', 'AlphaHigh',
             'Betalow', 'Betahigh', 'GamaLow', 'GamaMid','Heartrate']
df = pd.DataFrame(dataset)

for x in range(len(feature_cols)):
    df[feature_cols[x]] = pd.to_numeric(df[feature_cols[x]],errors='coerce')

X_test = df[feature_cols]
Updated_Status=[]

def update_status(s):
    length=len(s)
    for x in range(length):
        col=[]
        if(s[x]== 0):
            col.append(dataset.Time[x+1])
            col.append('No')
            col.append('0')
        else:
            col.append(dataset.Time[x+1])
            col.append('Yes')
            col.append('1')
        Updated_Status.append(col)
    return Updated_Status
model = pickle.load(open('model_F.pkl','rb'))
y_pred_user = model.predict(X_test)
# print(y_pred_user)
user_status=update_status(y_pred_user)
# print(dataset)
min_hr = min(dataset.Heartrate)
max_hr= max(dataset.Heartrate)
avg_hr = sum(dataset.Heartrate)/len(dataset.Heartrate)
print(min_hr)
print(max_hr)
print(avg_hr)
status_col = ['time','status','status_id']
df2 = pd.DataFrame(user_status, columns=status_col)

merged_status = pd.DataFrame(df2)
merged_status = merged_status.merge(read_data, left_index=True, right_index=True)

hours_to_add = 6 #Defining the time zone UTC+06
merged_status['timestampNs'] = pd.to_datetime(merged_status.timestampNs, unit='ns')
merged_status['timestampNs'] = merged_status['timestampNs'] + timedelta(hours = hours_to_add) #Converting to local time zone
merged_status['time'] = merged_status['timestampNs'].dt.strftime('%H:%M:%S')

merged_status.to_csv("Report/Status.csv", index= None, columns=['time','status_id'])

df1=pd.read_csv(user_data)

df3 = pd.concat([df1, df2], axis=1, join="inner")

df3.to_csv("Report/user_data_up.csv",index=None)


dataset02 = pd.read_csv("Report/Status.csv")
yes_count= (len(dataset02[dataset02['status_id'] == 1]))
no_count= (len(dataset02[dataset02['status_id'] == 0]))
total=yes_count+no_count
yes_percent = (yes_count/total)*100
no_percent = (no_count/total)*100
yes_min= 15 * yes_count / 60
# print(yes_min)
no_min= 15 * no_count / 60
# print(no_min)
tot_min = yes_min + no_min

if(no_count>=yes_count):
    user_status=0
else:
    user_status=1

recomm=[]
# Recommendation for heart rate
if (avg_hr<=75):
    recomm.append(6)
elif  (avg_hr>75 and avg_hr<=90):
    recomm.append(5)
elif  (avg_hr>90 and avg_hr<=100):
    recomm.append(2)
else:
    recomm.append(7)

# Recommendation for status
if (user_status):
    recomm.append(1)
else:
    recomm.append(8)

# Recommendation for stress level
if (yes_percent>=90):
    recomm.append(3)
elif  (yes_percent>=75):
    recomm.append(9)
elif  (user_status):
    recomm.append(10)




# no_min=11
data = [["Stressed",yes_percent],["Not Stressed",no_percent]]
df_up = pd.DataFrame(data, columns=['','percentage'])
df_up.to_csv("Report/stat_perc.csv",index=None)


#Initialize the connection with google sheet
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('Intelli helmet.json', scope)
client = gspread.authorize(credentials)

#Open Google sheet files
spreadsheet_stress_line = client.open('Stress_line')
spreadsheet_stress_pie = client.open('Stress_pie')

#Upload csv data to google sheet
with open('Report/Status.csv', 'r') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet_stress_line.id, data=content)
with open('Report/stat_perc.csv', 'r') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet_stress_pie.id, data=content)



@app.route('/', methods=['GET', 'POST'])
def index():
    cur_id = mysql.connection.cursor()
    mem_id = cur_id.execute("SELECT persno, name from members")
    if mem_id > 0:
        mem_val = cur_id.fetchall()
    return render_template('index2.php', mem_val = mem_val)


@app.route('/status', methods=['POST', 'GET'])
def show_status():
    one_str=str(1)
    if request.method == 'POST' or request.method == 'GET':
        # Fetch form data
        val_pers = request.form['select_pers']
        p_no = str(val_pers)

        cur = mysql.connection.cursor()
        cur.execute("UPDATE status SET sta_id = %s WHERE persno =  %s and %s",  (user_status, val_pers, one_str) )
        mysql.connection.commit()
        cur.close()
        # Select Details
        show_st = mysql.connection.cursor()
        st_exec = show_st.execute("SELECT * from status findings WHERE persno = %s and %s",  (val_pers, one_str) )
        # tex="HELLO"
        if st_exec > 0:
            # tex="IF"
            # shr_val = show_hr.fetchall()
            updt_st = mysql.connection.cursor()
            # updt_st.execute("UPDATE `findings` SET `Avg HR` = %s,`Max HR`= %s,`Min HR`= %s,`Stressed`= %s,`Not Stressed`= %s,`Total`= %s WHERE persno= %s", (avg_hr, max_hr, min_hr, yes_min, no_min, tot_min, p_no))
            updt_st.execute("UPDATE status SET sta_id = %s WHERE persno =  %s and %s",  (user_status, val_pers, one_str) )
            mysql.connection.commit()
            updt_st.close()
        else:
            # tex="ELSE"
            insr_st = mysql.connection.cursor()
            insr_st.execute("INSERT INTO `status` (`persno`, `sta_id`) VALUES (%s, %s)", (p_no, user_status))
            mysql.connection.commit()
            insr_st.close()
            # # end select
        # mysql.connection.commit()
        show_st.close()

        rec_cur = mysql.connection.cursor()
        # for x in recomm:
            # recc=str(recomm[x])
        rec_cur.execute("INSERT INTO `member_x_recomm` (`persno`, `rec_id`) VALUES (%s, %s) ",  (val_pers, recomm[0]) )
        mysql.connection.commit()
        rec_cur.close()

        rec_cur = mysql.connection.cursor()
        # for x in recomm:
            # recc=str(recomm[x])
        rec_cur.execute("INSERT INTO `member_x_recomm` (`persno`, `rec_id`) VALUES (%s, %s)",  (val_pers, recomm[1]) )
        mysql.connection.commit()
        rec_cur.close()

        rec_cur = mysql.connection.cursor()
        # for x in recomm:
            # recc=str(recomm[x])
        rec_cur.execute("INSERT INTO `member_x_recomm` (`persno`, `rec_id`) VALUES (%s, %s) ",  (val_pers, recomm[2]) )
        mysql.connection.commit()
        rec_cur.close()

        # Select Details
        show_hr = mysql.connection.cursor()
        shr_exec = show_hr.execute("SELECT * from findings findings WHERE persno = %s and %s",  (val_pers, one_str) )
        tex="HELLO"
        if shr_exec > 0:
            tex="IF"
            shr_val = show_hr.fetchall()
            updt_hr = mysql.connection.cursor()
            updt_hr.execute("UPDATE `findings` SET `Avg HR` = %s,`Max HR`= %s,`Min HR`= %s,`Stressed`= %s,`Not Stressed`= %s,`Total`= %s WHERE persno= %s", (avg_hr, max_hr, min_hr, yes_min, no_min, tot_min, p_no))
            mysql.connection.commit()
            updt_hr.close()
        else:
            tex="ELSE"
            insr_hr = mysql.connection.cursor()
            insr_exec = insr_hr.execute("INSERT INTO `findings` (`persno`, `Avg HR`, `Max HR`, `Min HR`, `Stressed`, `Not Stressed`, `Total`) VALUES (%s, %s, %s, %s, %s, %s, %s)", (p_no, avg_hr, max_hr, min_hr, yes_min, no_min, tot_min))
            mysql.connection.commit()
            insr_hr.close()
            # # end select
        # mysql.connection.commit()
        show_hr.close()




    csv1 = pd.read_csv("status_1.csv")

    # print(csv1)
    val_list = csv1.values.tolist()
    yes_count = val_list.count("Yes")
    # yes_count = 5
    # print(val_list)


    # Select name
    stat_id = mysql.connection.cursor()
    stat_exec = stat_id.execute("SELECT m.name, st.sta_name from members m natural join status natural join status_name st")
    if stat_exec > 0:
        stat_val = stat_id.fetchall()
    #end select

    # return render_template('show_status.php', val_list = stat_val, stat_val=stat_val, wng=user_status, typeQ=type(val_list), num=p_no, yes_count=yes_min, no_count=no_min, avg= avg_hr, max = max_hr, min = min_hr, tot = tot_min, ltr = tex)
    return render_template('show_status.php', val_list = recomm,  wng=user_status, typeQ=type(val_list), num=p_no, yes_count=yes_min, no_count=no_min, avg= avg_hr, max = max_hr, min = min_hr, tot = tot_min, ltr = tex)



if __name__ == '__main__':
 app.run(debug=True)
