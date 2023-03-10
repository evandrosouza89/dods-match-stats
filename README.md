<p align="center">
  <a href="https://store.steampowered.com/app/300/Day_of_Defeat_Source/">
  <img src="/assets/banner.jpg">
</p>

# DODS-MATCH-STATS
  A HL Log Standard parser and competitive match stats generator for [Day of Defeat Source game](https://store.steampowered.com/app/300/Day_of_Defeat_Source/).

  What kind of events does it parse?

  Every game event that makes sense in a competitive match, including:

  - Kills / Deaths / Attacks / Suicide
  - Flag captures / Flag blocks
  - Round win events / Tick scores
  - Chat messages
  - Player connections / Player disconnections 
  - Player name changes / Player Role changes / Player team changes 
  - Domination events / Revenge events

  What kind of stats does it generate?

  - Total Enemy damage / Total team damage / Average damage per life
  - Kills / Deaths / Team kills / Team killed / Suicides / Headshots
  - Streak stats
  - Flag capture stats, including game score stats
  - Weapon stats

  What kind of output does it generate?
  - HTML report file
  - Integration with [IPB board](https://invisioncommunity.com/files/)
  
## How this works
  This parser flow can be divided in three main scopes: 
  - Game server scope
  - Docker host scope
  - Docker container scope

<p align="center">
  <img src="/assets/flowchart.jpg">
  <figcaption>From the left to the right, game servers generate UDP packets containing game events logs, which are received and routed by the Docker host. The Docker host manages one MySQL database container and at least one dods-match-stats parser container. The dods-match-stats containers receive and process the game events logs to calculate the score of the teams and extract individual stats of the players who played the match. In the end of the process, the stats are persisted in the database container and a html report is generated in the docker host.</figcaption>
</p>

## What are war reports?
  Below two output examples of dods-match-stats parser job:

<p align="center">
  <a href="https://htmlpreview.github.io/?https://github.com/evandrosouza89/dods-match-stats/blob/master/assets/demo1.html">
  <img src="/assets/demo1.jpg">
</p>
  
  <p align="center">
  <a href="https://htmlpreview.github.io/?https://github.com/evandrosouza89/dods-match-stats/blob/master/assets/demo2.html">
  <img src="/assets/demo2.jpg">
</p>

## Requirements
  - Day of Defeat Source game server
  - Linux host with [Docker tool](https://www.docker.com/) installed
    
## Installation
  - Install [Docker](https://www.docker.com/) and start it
  - [Download dods-match-stats scripts](https://github.com/evandrosouza89/dods-match-stats/raw/master/assets/dods-match-stats.v1.0.zip)
  - Edit **servers.txt**, remove the example entries and carefully fulfill all the fields with one <game server ip>;<desired dods-match-stats port> per line. Notice that if the game server isn`t in the same machine as the dods-matchs-stats you will have to open your UDP <desired dods-match-stats port> for incoming conections in your network/firewall
  
## How to run
  - Execute command:
  ```
  bash start.sh
  ```
 
## How to stop
  - Execute command:
  ```
  bash stop.sh
  ``` 
 
## Where do I see the generated match content?
  - This app outputs war reports at ```/var/www/dods-match-stats/html folder```
  - Check your provided MySQL database, everything will be there
 
## Quick notes about this program
  - It only stores events and stats of valid matches
   
  - What is a valid match? A valid match is any match that uses the game built-in war-mode settings. After the program capture a sequence of valid events it will start recording the match events and at the end of the match it will store it on provided database
    
## License
  dods-match-stats is licensed under the MIT License. A short and simple permissive license with conditions only requiring preservation of copyright and license notices. Licensed works, modifications, and larger works may be distributed under different terms and without source code.
