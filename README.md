<p align="center">
  <img src="/assets/banner.jpg">
</p>


# DODS-MATCH-STATS
A HL Log Standard parser and competitive match stats generator for Day of Defeat Source game.

What kind of events does it store?
Every game event that makes sense in a competitive match, including:

- Kills / Deaths / Attacks / Flag captures / Flag blocks / Round win events / Tick scores / Chat messages / Connections / Disconnections / Name changes / Role changes / Domination events / Revenge events / Joined team events / Suicide events

What kind of stats does it generate and store?

- Total Enemy damage / Total team damage / Average damage per life
- Kills / Deaths / Team kills / Team killed / Suicides / Headshots
- Streak stats
- Flag capture stats, including game score stats
- Weapon stats

What kind of output does it generate?
- HTML report file
- Integration with IPB board

## License
dods-match-stats is licensed under the MIT License. A short and simple permissive license with conditions only requiring preservation of copyright and license notices. Licensed works, modifications, and larger works may be distributed under different terms and without source code.

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
 ### Listening to remote logs using [config_file.properties](config_file.properties)
 Use this one if you want to track one game server only
   - Configure all properties in [config_file.properties](config_file.properties)
   - Execute command:
   ```
   python3 __main__.py
   ```
 ### Listening to remote logs using command line arguments
 Use this if you want to run multiple dods-match-stats instances for tracking multiple servers
   - Configure DatabaseSection properties in [config_file.properties](config_file.properties)
   - Execute command:
   ```
   python3 __main__.py -t "remote.adress.ip" -p localport -l "/path/to/logdir" -n "instancename"
   ```
 ### Run once providing server's log files
 Use this if you want to feed the database with past log files or missing log files. It accepts wild cards. For example "../logs/l*.log" 
   - Configure DatabaseSection properties in [config_file.properties](config_file.properties)
   - Execute command:
   ```
   python3 __main__.py -i "/path/to/input/log.file"  
   ``` 
 ## How do I see the generated match content?
   - Check your provided MySQL database, everything will be there.
 
 ## Quick notes about this program
   - It only stores events and stats of valid matches.
   
   - What is a valid match? A valid match is any match that uses the game built-in war-mode settings. After the program capture a sequence of valid events it will start recording the match events and at the end of the match it will store it on provided database.
