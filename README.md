<p align="center">
    <a href="https://store.steampowered.com/app/300/Day_of_Defeat_Source/">
        <img src="/assets/banner.jpg">
    </a>
</p>

# DODS-MATCH-STATS

A **HL Log Standard parser** and **competitive match stats generator** for [Day of Defeat: Source](https://store.steampowered.com/app/300/Day_of_Defeat_Source/).

## Features

### What kind of events does it parse?

It captures every relevant game event in competitive matches, including:

- **Player Actions**: Kills, Deaths, Attacks, Suicides
- **Objective Events**: Flag Captures, Flag Blocks
- **Game Flow**: Round Wins, Tick Scores
- **Player Interactions**: Chat Messages, Connections, Disconnections, Name Changes, Role Changes, Team Changes
- **Special Events**: Domination and Revenge Events

### What kind of stats does it generate?

- **Damage Metrics**: Total Enemy Damage, Total Team Damage, Average Damage per Life
- **Kill Metrics**: Kills, Deaths, Team Kills, Team Deaths, Suicides, Headshots
- **Streaks**: Kill Streaks and Other Streak Stats
- **Objective Metrics**: Flag Captures, Game Score Stats
- **Weapon Stats**: Performance Metrics per Weapon Type

### What kind of output does it generate?

- **HTML Report File**
- **Integration with** [IPB Board](https://invisioncommunity.com)
- **Integration with** [Discord](https://discord.com/)

---

## How It Works

This parser operates within three key scopes:

- **Game Server Scope**: Generates UDP packets containing game event logs.
- **Docker Host Scope**: Receives and routes these logs.
- **Docker Container Scope**: Processes logs, calculates stats, and persists data.

<figure style="text-align: center;">
  <img src="/assets/flowchart.jpg" alt="Flowchart">
  <figcaption>From the left to the right, game servers generate UDP packets containing game events logs, which are received and routed by the Docker host. The Docker host manages one MySQL database container and at least one dods-match-stats parser container. The dods-match-stats containers receive and process the game events logs to calculate the score of the teams and extract individual stats of the players who played the match. In the end of the process, the stats are persisted in the database container and a html report is generated in the docker host.</figcaption>
</figure>

---

## War Reports

Below are examples of the **dods-match-stats** parser output:

<p align="center">
  <a href="https://htmlpreview.github.io/?https://github.com/evandrosouza89/dods-match-stats/blob/master/assets/demo1.html">
    <img src="/assets/demo1.jpg"></a>
</p>
  
  <p align="center">
  <a href="https://htmlpreview.github.io/?https://github.com/evandrosouza89/dods-match-stats/blob/master/assets/demo2.html">
    <img src="/assets/demo2.jpg"></a>
</p>

---

## Requirements

- **Game Server**: A running **Day of Defeat: Source** server
- **Host System**: A Linux system with [**Docker**](https://www.docker.com/) installed
- **Optional**: Integration with **IPB Forum** or **Discord Guild**

---

## Installation

1. Install [**Docker**](https://www.docker.com/) and start it.
2. **Download the dods-match-stats package**: [Download ZIP](https://github.com/evandrosouza89/dods-match-stats/raw/master/assets/dods-match-stats.v1.0.zip)
3. Configure the servers:
   - Edit **servers.txt** to include game server IPs in the format:
     ```
     <game server ip>;<desired dods-match-stats port>
     ```
   - If running on a different machine, open the UDP port for incoming connections.
4. Configure your **game server** by adding:
   ```
   mp_logdetail 3
   logaddress_add <dodstats_ip>:<dodstats_port>
   ```
5. Edit **config\_file.config** and set the **DMS\_OUTPUT\_DIR** variable.

---

## Configuration File Properties

| Property                 | Description                                     |
| ------------------------ | ----------------------------------------------- |
| `DMS_OUTPUT_DIR`         | Directory where HTML reports will be generated  |
| `DMS_EXTERNAL_URL`       | Used in IPB or Discord messages to link reports |
| `DMS_DISCORD_ENABLED`    | Enable/disable Discord integration              |
| `DMS_DISCORD_TOKEN`      | Discord bot token                               |
| `DMS_DISCORD_CHANNEL_ID` | Discord channel for report messages             |
| `DMS_IPB_ENABLED`        | Enable/disable IPB integration                  |
| `DMS_IPB_API_URL`        | IPB API endpoint                                |
| `DMS_IPB_API_KEY`        | IPB API key                                     |
| `DMS_IPB_FORUM_ID`       | Forum ID for new report topics                  |
| `DMS_IPB_AUTHOR_ID`      | Forum bot ID for report posts                   |
| `DMS_IPB_TOPIC_SUFFIX`   | Customizable topic title suffix                 |
| `DMS_IPB_POST_PREFIX`    | Customizable post prefix                        |
| `DMS_IPB_LINK_TEXT`      | Customizable link text                          |

---

## Running the Application

### Start the Parser

```sh
bash start.sh
```

### Stop the Parser

```sh
bash stop.sh
```

### Where Do I Find Generated Reports?

- Reports are stored in `DMS_OUTPUT_DIR` (default: `/var/www/dods-match-stats/html`)
- Match data is also saved in the **MySQL database**

---

## Notes

- **Only stores valid matches.**
- **What is a valid match?**
  - A match using the built-in **war-mode** settings.
  - Once a sequence of valid events is detected, it begins tracking stats.
  - At the match’s end, all stats are stored in the database.

---

## License

**dods-match-stats** is licensed under the **MIT License**, allowing unrestricted use, modification, and distribution with minimal conditions.
