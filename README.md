# Educative Viewer

## This project is made for easier readability of Educative.io courses downloaded using [Educative.io_Scraper](https://github.com/anilabhadatta/educative.io_scraper).

### Refer cloudflared tunneling docs to tunnel local servers via cloudflared generated urls or custom domains.

      Repo Version : 4.0.5
      Folder named "instance" contains the db.sqlite file, delete it from v4.0.4
      This Viewer is Designed for Educative.io Courses scraped in DARK Mode.

## To Run this project using git clone and python:

### Prerequisites:

      Git
      Python 3.9+
      OS: Win/Mac(Intel)/Linux(ARM/AMD)

### Step 1: Download & cd this project dir.

      git clone https://github.com/anilabhadatta/educative-viewer.git
      cd educative-viewer

### Step 2: Install the virtualenv package for python3 and create a virtual environment.

      pip3 install virtualenv
      virtualenv env

### Step 3: Activate the virtual env and install dependencies and set Env variables.

#### > (For Windows)

      env\Scripts\activate
      pip install -r requirements.txt
      cd ..
      set course_dir=<path to course folder>
      set FLASK_APP=educative-viewer
      set authtoken=<any random keystring>
      

#### > (For MacOS/Linux)

      source env/bin/activate
      pip3 install -r requirements.txt
      cd ..
      export course_dir=<path to folder>
      export FLASK_APP=educative-viewer
      export authtoken=<any random keystring>
      

### Step 4: Start the viewer using the following commands:

      flask run --host=0.0.0.0 --port=5000

      OR

      gunicorn --workers=2 -b 0.0.0.0:5000 'educative-viewer:create_app()' --access-logfile ./educative-viewer/access.log --error-logfile ./educative-viewer/error.log --timeout 120000

#### > Enter local_server_ip:5000/edu-viewer in your desktop/mobile browser to open the viewer.

     local_server_ip: Refers to the local ip in your ethernet/wifi adapter set by your router. eg: 192.168.1.111

#### > Refer the image below to get the course folder path, eg: "/Users/anilabhadatta/Documents/temp-course"

![image](https://i.imgur.com/sQQlJGI.jpg)

### (Optional) To build educative-viewer executable using pyinstaller:

#### Activate the Virtual Environment and Install the required modules for the project (Refer Step 2, 3, 4 above).

#### Install the pyinstaller package and run the following commands

      pip3 install pyinstaller

#### > (For Windows)

      pyinstaller --clean --add-data templates;templates --add-data static;static --onefile -i"icon.ico" educative-viewer.py

#### > (For MacOS/Linux)

      pyinstaller --clean --add-data templates:templates --add-data static:static --onefile -i"icon.ico" educative-viewer.py
