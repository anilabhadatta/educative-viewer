# Educative Viewer

## This project is made for easier readability of courses of Educative.io scraped using [Educative.io_Scraper](https://github.com/anilabhadatta/educative.io_scraper)
### Refer Step 6 if you are using release file.

## To run this project:

### Step 1: Install the virtualenv package for python3

#### > pip3 install virtualenv 

### Step 2: Create a virtual environment using:

#### > virtualenv env 

### Step 3: Activate the environment

#### > (For Windows) env\Scripts\activate

#### > (For MacOS/Linux) source env/bin/activate

### Step 4: Install the dependencies using:

#### > pip3 install -r requirements.txt

### Step 5: Run the following command in the virtual environment:

#### > python3 educative-scraper.py

### Step 6: Enter the course folder path in terminal and server will automatically start
#### > Enter localhost:5000 in your desktop browser to open the viewer
#### > Enter local_server_ip:5000 in your mobile browser to open the viewer
#### > Refer the image below to get the course folder path, eg: "/Users/anilabhadatta/Documents/temp-course"
![image](https://i.imgur.com/sQQlJGI.jpg)

### Step 7 (Optional): To build the python application using pyinstaller:

#### > (For Windows) pyinstaller --clean --add-data templates;templates --onefile -i"icon.ico" educative-viewer.py

#### > (For MacOS/Linux) pyinstaller --clean --add-data templates:templates --onefile -i"icon.ico" educative-viewer.py
