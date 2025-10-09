# What is the Dashboard?
Moodle LMS has features for report generation but there were a few issues, namely:
1. It wasn't intuitive.

2. It required sign-in to moodle to access.

3. It there was no feature to send custom reminders to users for not completing their courses and refresh on POSH and Compliance.

There was however a feature that allowed for the report to be sent to the admin periodically. Using ths feature, an idea to build a dashboard that could generate dynamic, accurate and custom reports was born. 

# How does this work?
1. Currently, Moodle is set to email its reports everyday.

2. Using the Gmail API, setup under the academy@healthark account, allowed for the latest report to be downloaded automatically.

3. The report, which is essentially an excel file, is then fetched using pandas and all operations of filtering for courses, sending reminders is carried out through Pandas and the Gmail API.

4. Since the requirement was elaborate monitoring for compliance, inbuilt features for graphs, tables were required.

5. Keeping these in mind along with the fact that the project had low computational requirements, Streamlit was chosen on the frontend for its ease of use, not just for the developer but also the user.

# The Project Folder: Where and Why

## 1. Credentials Folder:
This folder contains all .json files required in this project.

1. config.json: defines the email id of the admin account (i.e. the account that recieves the email from Moodle containing the report). This is the same email id that is used to send reminder emails to all enrolled users.

2. credentials.json: this file is **required by the gmail api and should not be deleted**.

3. token.json: automatically generated once the device has been authorized by the admin account to access it's mails.

## 2. Documents Folder:
This is where all .xlsx and .docx files are stored for use by the application.

1. Healthark Academy User Details.xlsx: the original report from Moodle fetched by the gmail api.

2. Healthark Academy Testing User Details: file used during testing of the app left here for future use if any.

3. POSH_Reminder_data.xlsx: this file was originally generated manually for the yearly POSH reminder feature. It's role and logic has been further discussed in the Logic section.

4. POSH Reminder Mail.docx: created in order to easily modify the body of the reminder email for POSH.

5. Course Reminder Mail.docx: same as POSH but for the Nudge function in the main app (discussed further).

**Note**: The curly brackets in the .docx files signify variables that will be replaced with their actual values when generating the actual email. These are not to be edited whatsoever and is an important instruction for all administrators and developers.

## 3. app.py:
This is the main file that must be run to view the site (command to activate the streamlit site: streamlit run app.py). It is esentially where all the UI has been designed. Outside of this file, the streamlit library has not been called. 

**If the objetive is to change the UI, edit the flow, this is where one needs to come.**

## 4. mail_excel.py:
When app.py is first run, it establishes a connection with the admin's gmail and fetches the latest report. mail_excel contains the logic to do that exactly along with creating a pandas dataframe of the newly downloaded excel report.

**If the subject of the email of the report has been changed on Moodle, this file's query variable (available in the 'fetch_excel_attachment' function) must be modified to be compatible with the new name**

## 5. df_views.py:
This file contains all the functions that determine the look of the dataframe, including the naming of their columns.

## 6. MailSending.py:
Contains logic to send emails, the preperation of its body and Subject. Also determines whose email the mail is sent from.

## 7. posh_reminder.py:
This file contains all logic related to the posh_reminder function in app.py. The functionalities are vast but essentially boil down to generating and managing the POSH_Reminder_data.xlsx file.

**Note:** The 'test.ipynb' file is meant for developer-testing and visualization of data purposes during development. It is not essential for production and has no effect on the application.

# Logic: A Detailed How

## Fetching Report from Admin Inbox:
1. Gmail API requires permission from the admin email address for the device to connect to its inbox.
2. This is done through the google cloud console and the gmail api docs can be referred for the same.
3. Once the user gives the required permissions, the 'fetch_excel_attachment' function accesses the credentials.json file and creates a token.json, establishing a connection between the app and gmail.
4. SCOPES are used to define if the connection can be used to only read emails or send them as well. Currently, the SCOPES have been set to do both.

## Sending Emails:
1. Straightforward as it uses the Gmail API.
2. The important part is to keep in mind the .docx files as they determine the body of the Emails. 
3. **The curly brackets signify variables autofilled with their values from the report and should not be edited. If they are, the changes must be made in the generate_body functions.

## POSH Compliance:
1. One of the requirements for the Dashboard was to send yearly reminders to the users to complete their POSh Compliance.
2. As mentioned earlier, the POSH_Reminder excel file was created to keep a track of the users starting date and the reminder date (exactly 1 year after the date of starting).
3. To do this, initially all starting dates were set to the date of enrollment (this is the case even for new additions) and reminder dates were calculated.
4. 1 year later, once the date of reminders come and the reminders are sent out, the new date of starting becomes the date of reminder a fresh set of reminders are calculated.
5. All this is done when the app boots up and only the **reminders must be sent manually**.