Project Proposal
Fundamentals of Software Engineering

Project Overview
Project Title: Evidentia
Project Type: Desktop Application
Target Audience: Digital forensic investigators, legal professionals, and cybersecurity analysts.
What it is: A simple tool for computers that helps people organize digital files into a clear timeline to see exactly when things happened.

2. Problem Statement
Right now, if you are a student or a junior investigator trying to sort through hundreds of digital files for a case, it is a total nightmare because everything is so unorganized. You end up with a huge mess of folders and files scattered all over your computer, and you have to click on every single one just to see when it was made or last changed. Doing this manually takes a really long time and it is incredibly boring, which makes it easy to get tired and make mistakes. You might miss a really important photo or a document just because it was hidden in a subfolder you didn't see. Most people try to use basic search bars or just write down dates on a piece of paper to keep track of what happened, but that doesn't help you see the "big picture." Without a proper way to see everything on a timeline, it is hard to tell a clear story of what happened first and what happened last. This makes the whole investigation move slowly and can cause people to reach the wrong conclusions because they couldn't see how all the files connect together. It's frustrating to work this way when you're under a deadline.
3. Problem Solution
Our project, Evidentia, is designed to fix this headache by taking all those messy files and automatically putting them into one neat, clickable timeline on your screen. Instead of the user having to open every single file to find its details, our app does the hard work for you by "reading" the hidden metadata inside the files, like the exact second a photo was taken or when a Word doc was edited. We are building this in three clear steps so we don't get overwhelmed. First, we will make the part that lets you upload a folder and pulls out all that hidden info. Second, we will build the actual timeline view where all the files show up as points on a map of time so you can scroll through them easily. Finally, we will add tools to search through the timeline and save a final report that summarizes everything. By the end of our work, an investigator will be able to just drag a folder into Evidentia and immediately see a full history of the digital evidence without doing any manual typing. This saves a lot of time and makes the whole job much more accurate.
4. Scope
Since we only have three iterations of two weeks each, we have to be very clear about what we are actually building. Evidentia is strictly a desktop application, so it won’t work on phones or as a website. We are focusing only on common file types that students and investigators use every day, like .docx, .pdf, .jpg, and .txt. The app will only look at files that are already sitting on your computer or a plugged-in USB drive. We are not including advanced "hacker" features, so the app won't be able to open files that have passwords or recover files that were deleted a long time ago. We also aren't connecting it to the internet, so it won't track live social media or cloud data; it is just for organizing the files you already have in front of you. By keeping the scope small, we can make sure the timeline and the report-making features actually work perfectly by the end of the third iteration.








Basic Features

Bulk Folder Upload 
You can drag and drop a whole folder of files into the "Evidence Management" area. This makes it fast to start working without having to select every single file one by one.
Metadata Overview Table 
The app automatically "reads" files and fills a table with their ID, Name, and Date. This helps you see the hidden details of every piece of evidence in one clean list.
Interactive Timeline Grid 
There is a visual bar that shows the progress of a case from "Evidence Collected" to "Closed". It maps out your investigation milestones so you can see the sequence of events at a glance.
Evidence Status Tracking 
Using the sidebar, you can check boxes to filter files by their status, such as "Analyzed," "Pending," or "Flagged". This helps you keep track of what work is finished and what still needs to be checked.
Risk Level Visualization 
The app creates a bar chart that shows how many files are "Low," "Medium," or "High" risk. This allows an investigator to focus on the most dangerous or important evidence first.
Recent Activity Feed 
This feature shows a live list of the latest actions taken, like when a meeting was held or evidence was uploaded. It works like a history log so you never lose track of what you did recently.
Investigation Type Sorting 
You can categorize your projects into different types, such as "Financial Fraud" or "Cybercrime". This helps keep your various cases organized and separate from each other.
Quick Stats Dashboard 
A summary screen that shows how many total files you have, how many are analyzed, and how many team members are working. It gives you a "big picture" view of the whole investigation.

Automated Final Report 
With one click, the app takes all your charts, timelines, and file details and turns them into a PDF. This is used for handing in the final results of your work in a professional format.
Global Search & Filter 
There is a search bar and file-type filters (like PDF, Image, or Email) to help you find specific files. It saves a lot of time when you are looking for one specific document in a large case.

Project Plan

Modular Breakdown
The project is divided into three modules, each taking two weeks. Each iteration will result in a working version of the product that adds more detail to the investigation.

#This is a table 
Iteration | Module Name | Deliverable | Features & User Stories Included
Iteration 1 (Weeks 1-2) | Evidence Engine |
A functional app that can import and read file data.
1. Bulk Folder Upload: As a user, I want to drag a folder in so I don't have to pick files one by one.

2. Metadata Table: As a user, I want to see a list of file names and dates automatically so I don't have to type them.

3. Case Type Sorting: As a user, I want to label my case (e.g., "Financial Fraud") to keep my workspace organized.

Iteration 2 (Weeks 3-4) | Timeline & Analytics
An interactive version of the app with sorting and mapping.
4. Timeline Grid: As a user, I want to see my case milestones on a bar so I can see the order of events.

5. Evidence Status Tracking: As a user, I want to check boxes (Analyzed/Pending) to keep track of my progress.

6. Risk Level Charts: As a user, I want to see a bar chart of High/Low risk files to know what to check first.

7. Global Search: As a user, I want to search by filename to find evidence quickly.


Iteration 3 (Weeks 5-6)
Reporting & History
The final product with history logs and PDF exporting.
8. Recent Activity Feed: As a user, I want to see a list of my last actions so I remember what I did.

9. Quick Stats Dashboard: As a user, I want to see a total count of my files and team members on one screen.

10. Automated Final Report: As a user, I want to click a button to save my findings as a professional PDF.


Role Assignment
Since our team consists of two people, we have divided the roles to ensure all project requirements are met.

Gul-e-Zara
Group Lead, Developer & Tester
Acts as the main point of contact for submission. Works on coding the backend engine and tests the app for bugs at the end of each iteration.

Rumesha Naveed
Requirement Engineer, Developer & Tester
Ensures every feature we build matches our problem statement. Works on coding the user interface and charts, and performs final testing.
Shared
Testers
Both members will test the features at the end of each iteration to make sure there are no bugs before submission


Prototype 
Attached pictures of Pencil Tool design








