# Intelli_Helmet
Intelli-Helmet is a stress monitoring system using the brain wave data form EEG headset and physiological data (Heart Rate) from wearable device.

Required Libries:
1. pip install flask
2. pip install flask_mysqldb \n
3. pip install pandas \n
4. pip install numpy
5. pip install datetime
6. pip install gspread
7. from oauth2client.service_account import ServiceAccountCredentials

Follow the instruction to proceed:

****************This is a set of python programs to update the database and UI data basing on input**********

1. Install python version>=3.7.
2. Install the requirements.
3. Get data:
	a. from 'MIFit' app for heart rate. Rename it as "heart_input.csv" and store in 'Input' folder.
	b. from 'eegID' app for brainwaves. Store it in 'Input' folder as "eegIDRecord.csv".
4. Run the "Process_&_Upload.py" from python console.
	Command: 
		python Process_&_Upload.py
5. Run the "app_flask_mysql.py" from python console with the xampp server on. It will start hosting a MySQL server.
	Command: 
		python app_flask_mysql.py
6. The home page will open at "http://127.0.0.1:5000/" or "http://localhost:5000/".
7. Select the name of the person whose data is taken. Click submit. The database is updated.

