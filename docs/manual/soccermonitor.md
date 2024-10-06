# Soccer Monitor

## Introduction

Soccer monitor provides a visual interface. Using the monitor, we can watch a game vividly and control the proceeding of the game.

By cooperating with logplayer, soccermonitor can replay games, so that it becomes very convenient to analyze and debug clients.

## Getting started

To connect the soccer monitor with the soccer server, you can use the command following:

```bash
$ rcssmonitor
```

By specifying the options, you can modify the parameters of soccer monitor instead of modifying monitor configuration file. You can find available options by:

```bash
$ rcssmonitor --help
```

If you use script **rcsoccersim** to start the server, a monitor will be automatically started and connected with the server:

```bash
$ rcsoccersim
```

### Total number of monitor clients

By default, there is no restriction on the number of monitor clients. You can restrict the number of monitor connections by changing the value of `server::max_monitor` parameter. This feature is useful when you want to reduce the load by limiting arbitrary connections from others.

If the value of `server::max_monitor` is negative integer (default:-1), no restriction. If the value is positive integer, the total number of monitor clients that can connect to the rcssserver is restricted within that number.

Suppose a new monitor client tries to connect to the server after the number of connected monitors has reached the server limit (max_monitor). In that case, the server will refuse the connection and send **(error no_more_monitor)** back to the monitor's client.

## Communication from Server to Monitor

Soccer monitor and rcssserver are connected via UDP/IP on port 6000 (default). When the server is connected with the monitor, it will send information to the monitor every cycle. rcssserver-15 provides four different formats (version 1 ~ 4). The server will decide which format is used according to the initial command sent by the monitor (see [sec-commandsfrommonitor](#-sec-commandsfrommonitor)). The detailed data structure information can be found in appendix [sec-appendixmonitorstructs](#-sec-appendixmonitorstructs).

### Version 1

rcssserver sends `dispinfo_t` structs to the soccer monitor. `dispinfo_t` contains a union with three different types of information:

- `showinfo_t`: information needed to draw the scene
- `msginfo_t`: contains the messages from the players and the referee shown in the bottom windows
- `drawinfo_t`: information for monitor to draw circles, lines or points (not used by the server)

The size of `dispinfo_t` is determined by its largest subpart (msg) and is 2052 bytes (the union causes some extra network load and may be changed in future versions). In order to keep compatibility between different platforms, values in `dispinfo_t` are represented by network byte order. Which information is included is determined by the mode information. 

NO_INFO indicates no valid info contained (never sent by the server), BLANK_MODE tells the monitor to show a blank screen (used by logplayer)

#### Showinfo

A `showinfo_t` struct is passed every cycle (100 ms) to the monitor and contains the state and positions of players and the ball:

```c
typedef struct {
   char   pmode ;
   team_t team[2] ;
   pos_t  pos[MAX_PLAYER * 2 + 1] ;
   short  time ;
} showinfo_t ;
```

- `pmode`: currently active playmode of the game
- `team`: information about the teams. Index 0 is for team playing from left to right
- `pos`: position information of ball and players. Index 0 represents the ball, indices 1 to 11 is for team[0] (left to right) and 12 to 22 for team[1]
- `time`: current game time

Values of the elements can be:

- `enable`: state of the object.
- `side`: side the player is playing on. LEFT means from left to right, NEUTRAL is the ball
- `unum`: uniform number of a player ranging from 1 to 11
- `angle`: angle the agent is facing ranging from -180 to 180 degrees
- `x`, `y`: position of the ball or player on the screen

#### Messageinfo

Information containing the messages of players and the referee:

```c
typedef struct {
  short board ;
  char  message[2048] ;
} msginfo_t;
```

- `board`: indicates the type of message
- `message`: zero terminated string containing the message

#### Drawinfo

Allows specifying information for the monitor to draw circles, lines or points.

### Version 2

rcssserver sends `dispinfo_t2` structs to the soccer monitor instead of `dispinfo_t` structs which is used in version 1. `dispinfo_t2` contains a union with five different types of information (the data structures are printed in appendix [sec-appendixmonitorstructs](#-sec-appendixmonitorstructs)):

- `showinfo_t2`: information needed to draw the scene.
- `msginfo_t`: contains the messages from the players and the referee.

  - **team graphic**: The team graphic format requires a 256x64 image to be broken up into 8x8 tiles and has the form:
  
        ```text
        (team_graphic_{l|r} (<X> <Y> "<XPM line>" ... "<XPM line>"))
        ```

  - **substitutions**: substitutions are now explicitly recorded in the message board in the form:
  
        ```text
        (change_player_type {l|r} <unum> <player_type>)
        ```

- `player_type_t`: information describing different player's abilities and tradeoffs
- `server_params_t`: parameters and configurations of soccerserver
- `player_params_t`: parameters of players

Which information is contained in the union is determined by the mode field.

#### Comments from Monitor:
The monitor can send to the server the following commands

```c
(dispinit) | (dispinit version <version>)
```

sent to the server as the first message to register as a monitor (opposed to a player, that connects on port 6000 as well)
"(dispinit)" is for information version 1, while "(dispinit version 2)" is for version 2.
You can change the version by setting the according monitor parameter.

**TODO: [12.0.0 pre-20071217] accept some coach commands from monitor**

## How to record and playback a game

To record games, you can call the server with the argument:

```bash
server::game_logging = true
```

This parameter can be set in `server.conf` file. The logfile is recorded under **server::game_log_dir** directory. The default logfile name contains the datetime and the result of the game. You can use the fixed file name by using **server::game_log_fixed** and **server::game_log_fixed_name**.

```bash
server::game_log_fixed : true
server::game_log_fixed_name : 'rcssserver'
```

To specify the logfile version, you can call the server with the argument:

```bash
server::game_log_version [1/2/3/4/5]
```

or set the parameter in server.conf file:

```bash
server::game_log_version : 5
```

You can replay recorded games using logplayer applications. The latest rcssmonitor (version 16 or later) can work as a logplayer. To replay logfiles, just call rcssmonitor with the logfile name as an argument, and then use the buttons on the window to start, stop, play backward, or play stepwise.

### Protocol Versions

#### Version 1

Logfiles of version 1 (server versions up to 4.16) are a stream of consecutive dispinfo_t chunks.

#### Version 2

Version 2 logfile protocol tries to avoid redundant or unused data for the price of not having uniform data structs. The format is as follows:

- **head of the file**: the head of the file is used to autodetect the version of the logfile. If there is no head, Unix-version 1 is assumed. 3 chars 'ULG' : indicating that this is a Unix logfile (to distinguish from Windows format).
- **char version**: version of the logfile format
- **body**: the rest of the file contains the data in chunks of the following format:

  - `short mode`: this is the mode part of the `dispinfo_t` struct

     - If mode is SHOW_MODE, a `showinfo_t` struct is following.
     - If mode is MSG_MODE, next bytes are

        ```c
        short board: containing the board info
        short length: containing the length of the message (including zero terminator)
        string msg: length chars containing the message
        ```

Other info such as DRAW_MODE and BLANK_MODE are not saved to log files.

#### Version 3

The version 3 logfile protocol contains player parameter information for heterogenous players and optimizes space. The format is as follows:

- **head of the file**: Just like version 2, the file starts with the magic characters 'ULG'.
- **char version**: version of the logfile format, i.e. 3
- **body**: The rest of the file contains shorts that specify which data structures will follow.

#### Version 4

The version 4 logfile protocol is a text-based format, that may be readable for humans.

#### Version 5

The version 5 logfile protocol is adopted in rcssserver version 13 or later. Its grammar is almost the same as the version 4 protocol.

## Settings and Parameters

rcssmonitor has various modifiable parameters. You can check available options by calling rcssmonitor with `--help` argument:

```bash
rcssmonitor --help
```

Several parameters can be modified from `View` menu after invoking rcssmonitor.

Some parameters are recorded in `~/.rcssmonitor.conf`, and rcssmonitor will reuse them in the next execution. Of course, you can directly edit this configuration file.

## Team Graphic

**TODO**

## What’s New

16.0:
- Support illegal defense information.
- Integrate a log player feature.
- Implement a time-shift reply feature.
- Remove a buffering mode.
- Change the default tool kit to Qt5.
- Support CMake.

15.0:
- Support v15 server parameters.

14.1:
- Support an auto reconnection feature.

14.0:
- Reimplement using Qt4.
- Support players' card status.
- Implement a buffering mode.

13.1:
- Support a team_graphic message.

13.0:
- Support the monitor protocol version 4.
- Support stamina capacity information.

12.1:
- Support pointto information.
- Implement an auto reconnection feature.

12.0:
- Support the monitor protocol version 3.

11.0.2:
- Support penalty kick scores.

11.0:
- Support 64bits OS.

10.0:
- Ported to OS X.

9.1:
- Support a keepaway field.

8.03:
- The server supports compressed communication to monitors.
- Player substitution information is added to the message log.
- Team graphics information is added to the message log.

7.07:
- The logplayer did not send server param, player param, and player type messages.
- Fixed logging so that the last cycle of a game is logged.

7.05:
- “Skipped” cycles by the logplayer have occasionally caused issues, and this has been addressed to some extent.
- The server now records full-length messages received from players and coach.

7.04:
- Rounded angles are now sent instead of truncated as in previous versions.
- Changes made to all values in the `dispinfo_t` structure for the monitors and logfiles.

7.02:
- Added a new command to the monitor protocol:

```text
(dispplayer side unum posx posy ang)
```

7.00:
- Included the head angle into the display of the soccermonitor.
- Visualization effect for collisions with the ball or other players.
- Introduced monitor protocol version 2 and logging protocol version 3.
