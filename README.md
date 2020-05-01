# DODS-MATCH-STATS
A HL Log Standard parser and competitive match stats generator for Day of Defeat Source game.

## Requirements
  - Day of Defeat Source game server
  - Python3
  - pymysql
  - A MySQL database (configured with utf8-general_ci collation) 

## Instalation
  - Clone or download zip file of this repository
  - Install **Python3** for your current SO
  - Install **pip3** for your current SO
  - Navigate to the folder where you cloned/zip-extracted this project
  - Execute command:
  ```
  pip3 install -r requirements.txt
  ```
  - Execute command: 
  ```
  python3 -m pip install PyMySQL
  ```
  - Edit **config_file.properties** and carefully fulfill all the fields with correct information, remember that, if the game server isn`t in the same machine as the dods-matchs-stats you will have to open your **loglistener.port** UDP port for incoming conections in your network/firewall
  
 ## How to run
   - Execute command:
   ```
   python3 __main__.py
   ```
 
 ## How do I see the generated match content?
   - Check your provided MySQL database, everything will be there.
 
 ## Quick notes about this program
   - It only stores events and stats of valid matches.
   
   - What is a valid match? A valid match is any match that uses the game built-in war-mode settings. After the program capture a sequence of valid events it will start recording the match events and at the end of the match it will store it on provided database.
