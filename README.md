# Educative Viewer

## This project is made for easier readability of Educative.io courses downloaded using [Educative.io_Scraper](https://github.com/anilabhadatta/educative.io_scraper)
### Refer Step 4 if you are using Releases.
### Refer cloudflared tunneling docs to tunnel local servers via cloudflared generated url / custom domain.
## To Run/Build this project:

### Step 1: Install the virtualenv package for python3 and create a virtual environment

      
      pip3 install virtualenv 
      virtualenv env 
      

### Step 2: Activate the environment
#### > (For Windows) 
      
      env\Scripts\activate
      
#### > (For MacOS/Linux) 
      
      source env/bin/activate
      
### Step 3: Install the required modules and start the educative-viewer using the following commands:
      
      pip3 install -r requirements.txt
      python3 educative-viewer.py
      

### Step 4: Enter the course folder path in terminal and server will automatically start
#### > Enter local_server_ip:5000 in your desktop/mobile browser to open the viewer
#### > Refer the image below to get the course folder path, eg: "/Users/anilabhadatta/Documents/temp-course"
![image](https://i.imgur.com/sQQlJGI.jpg)

### Step 5 (Optional): To build the educative-viewer using pyinstaller:
#### Install the pyinstaller package and run the following commands
      
      pip3 install pyinstaller
      
#### > (For Windows) 
      
      pyinstaller --clean --add-data templates;templates --add-data static;static --onefile -i"icon.ico" educative-viewer.py
      
#### > (For MacOS/Linux) 
      
      pyinstaller --clean --add-data templates:templates --add-data static:static --onefile -i"icon.ico" educative-viewer.py
      
