The Automated Referee sends messages to the players so that players know the actual play mode of the game. The rules and the behavior for the automated referee are described in Sec. [Overview Referee](#sec-overview-referee). Players receive the referee messages as hear messages. A player can hear referee messages in every situation independent of the number of messages the player heard from other players.

## Play Modes and Referee Messages

The change of the play mode is announced by the referee. Additionally, there are some referee messages announcing events like a goal or a foul. If you have a look into the server source code, you will notice some additional play modes that are currently not used. Both play modes and referee messages are announced using (referee String), where String is the respective play mode or message string. The play modes are listed in Table 1, for the messages see Table 2.

### Table 1: Play Modes

| Play Mode                     | tc   | Subsequent Play Mode  | Comment                                                                 |
|-------------------------------|------|-----------------------|-------------------------------------------------------------------------|
| before_kick_off               | 0    | kick_off_*Side*       | at the beginning of a half                                             |
| play_on                       |      |                       | during normal play                                                     |
| time_over                     |      |                       | End of the game                                                        |
| kick_off_*Side*               |      |                       | announce start of play (after pressing the Kick Off button)            |
| kick_in_*Side*                |      |                       |                                                                         |
| free_kick_*Side*              |      |                       |                                                                         |
| corner_kick_*Side*            |      |                       | when the ball goes out of play over the goal line, without a goal being scored and having last been touched by a member of the defending team. |
| goal_kick_*Side*              |      | play_on               | play mode changes once the ball leaves the penalty area                |
| goal_*Side*                   |      |                       | currently unused                                                       |
| drop_ball                     | 0    | play_on               |                                                                         |
| offside_*Side*                | 30   | free_kick_*Side*      | See detailed offside rules                                             |
| penalty_kick_*Side*           |      |                       | When the game ends in a draw of 6,000 cycles and overtime, the winner will be determined by penalty kicks. |
| foul_charge_*Side*            |      |                       | Pushing the opposing player                                            |
| back_pass_*Side*              |      |                       | Goalkeeper rules explained                                              |
| free_kick_fault_*Side*        |      |                       | Player free kick rules explained                                        |
| indirect_free_kick_*Side*     |      |                       | Player indirect free kick rules explained                               |
| illegal_defense_*Side*        |      |                       |                                                                         |

where Side is either the character *l* or *r*, OSide means opponent’s side. tc is the time (in number of cycles) until the subsequent play mode will be announced.

### Table 2: Referee Messages

| Message                     | tc   | Subsequent Play Mode  | Comment                                         |
|-----------------------------|------|-----------------------|-------------------------------------------------|
| goal_*Side*_*n*             | 50   | kick_off_*OSide*      | announce the *n* th goal for a team             |
| foul_*Side*                 | 0    | free_kick_*OSide*     | announce a foul                                 |
| yellow_card_*Side*_*Unum*   | 0    |                       | announce a yellow card information              |
| red_card_*Side*_*Unum*      | 0    |                       | announce a red card information                 |
| goalie_catch_ball_*Side*    | 0    | free_kick_*OSide*     |                                                 |
| time_up_without_a_team      | 0    | time_over             | sent if there was no opponent until the end of the second half |
| time_up                     | 0    | time_over             | sent once the game is over                      |
| half_time                   | 0    | before_kick_off       |                                                 |
| time_extended               | 0    | before_kick_off       |                                                 |

where Side is either the character `l` or `r`, OSide means opponent’s side. tc is the time (in number of cycles) until the subsequent play mode will be announced.

## Time Referee

**TODO**

- Judges the game time
- server::half_time
- [12.1.3] server::extra_half_time
- [13.0.0] change a length of overtime

## Offside Referee

The offside referee is a module that observes the field, particularly passes, to check whether the offside foul happens. This module determines offside lines every cycle, then specifies several candidates from players which would result in an offside if they receive a pass.

The referee is configurable by some parameters in server.conf file. Some useful parameters are explained below.

```
server::use_offside = true  // true: enable, false: disable
```

This parameter determines whether the offside referee is enabled or disabled.

```
server::offside_active_area_size = 2.5
```

This parameter determines the radius of an area around a candidate pass receiver. If the ball enters the area and the candidate performs a kick or tackle command, the offside foul is called. Offside is also called if the candidate collides with the ball.

```
offside_kick_margin = 9.15
```

This parameter determines the radius of the area that every player in the team which has done offside foul must stay out when the other team wants to free-kick. If there is a player in that area, the server moves them out of that.

![Offside Example](./images/offside-example)

## FreeKick Referee

Free kicks are detected automatically by the soccer server in many relevant cases. The Free kick referee is a module that observes the play mode, to check whether the free kick foul happens and what teams should do. Some methods are explained below.

```
void FreeKickRef::kickTaken
```

This method is executed when a foul has occurred by the player. This method checks whether the kick is correctly done or not.

```
void FreeKickRef::tackleTaken
```

This method is executed when a tackle foul has occurred by the player.

```
void FreeKickRef::ballTouched
```

This method checks whether the ball has been touched by an unauthorized player.

```
void FreeKickRef::analyse
```

This method checks the game play mode and removes unauthorized players from the foul area due to the situation.

```
void FreeKickRef::playModeChange
```

This method provides the free kick conditions according to the game mode and occurs when the mode has changed.

```
void FreeKickRef::callFreeKickFault
```

This method is for calling the free kick and receives the side and the foul location as inputs.

```
bool FreeKickRef::goalKick
```

If the right or left goal kick has occurred, the output value of this method is true.

```
bool FreeKickRef::freeKick
```

If a foul occurs, the output value of this method is true.

```
bool FreeKickRef::ballStopped
```

If the ball stops moving, the output value of this method is true.

```
bool FreeKickRef::tooManyGoalKicks
```

If the value of the goal kick count is greater than maxGoalKicks the output value of this method is true.

```
void FreeKickRef::placePlayersForGoalkick
```

This method sends the opponent players out of the penalty area if a goal kick occurs.

## Touch Referee

**TODO**

- Judge the goal
- [14.0.0] golden goal option, server::golden_goal

Checking for goals, out of bounds and within the penalty area complies with FIFA regulations. For a goal to be scored the ball must be totally within the goal:

```math
|ball.x| > FIELD_LENGTH \cdot 0.5 + ball_radius
```

Similarly, the ball must be completely out of the pitch before it is considered out:

```math
|ball.x| &> FIELD_LENGTH \cdot 0.5 + ball_radius \: ||\\
|ball.y| &> FIELD_WIDTH \cdot 0.5 + ball_radius
```

Lastly, the ball is within the penalty area (and thus catchable) if the ball is at least partially within the penalty area:

```math
|ball.y| &<= PENALTY_WIDTH \cdot 0.5 + ball_radius \: \&\&\\
|ball.x| &<= FIELD_LENGTH \cdot 0.5 + ball_radius \: \&\&\\
|ball.x| &>= FIELD_LENGTH \cdot 0.5 - (PENALTY_LENGTH \cdot 0.5 + ball_radius)
```

## Catch Referee

**TODO**

- Judges the goalie's catch behavior
- [12.0.0 pre-20071217] change the rules of back pass and catch fault
- [12.0.0 pre-20071217] change the rule of goalies' catch violation
- [12.1.1] fix the back pass rule

## Foul Referee

**TODO**

- Judges the foul
- [14.0.0] foul model and intentional foul option
- [14.0.0] foul information in sense_body/fullstate
- [14.0.0] red/yellow card message

If an intentional and dangerous foul is detected, the referee penalizes the player and sends the yellow/red card message to clients. The message format is similar to playmode messages. Side and uniform number information of penalized player are appended to the card message:

```
(referee TIME yellow_card_[lr]_[1-11]) or (referee TIME red_card_[lr]_[1-11])
```

## Ball Stuck Referee

**TODO: server::ball_stuck_area. [11.0.0] in NEWS**

## Illegal Defense Referee

From the server version 16, a new referee module has been added to control the number of defensive players. Four new variables in **server_param** change the parameters of this referee.

```
server::illegal_defense_duration = 20
```

This parameter determines the number of cycles that illegal defense situation would have to remain before calling a free kick.

```
server::illegal_defense_number = 0
```

This parameter determines how many players would need to be in the specified zone before the illegal defense situation countdown starts. If the value is set to 0, the referee never detects illegal defense situations.

```
server::illegal_defense_dist_x = 16.5
```

This parameter determines the distance from the field's goal lines for detecting defensive players.

```
server::illegal_defense_width = 40.32
```

This parameter determines the horizontal distance from the horizontal symmetry line for detecting defensive players.

## Keepaway Referee

**TODO**

- [9.1.0] keepaway mode

## Penalty Shootouts Referee

**TODO**

- [9.3.0] penalty shootouts
- [9.4.0] pen_coach_moves_players

## Rules

If defensive players exist within the rectangle defined by **illegal_defense_dist_x** and **illegal_defense_width**, they are marked as an illegal state. If the number of marked players becomes greater than or equal to **illegal_defense_number** and this continues for **illegal_defense_duration** cycles, then play mode will change to **free_kick_[lr]** for the offensive team.

A team is considered as the offensive team when their player is the latest player to kick the ball. If both teams perform a kick on the same cycle, neither team is considered as offensive, and the countdown resets. The above rule applies to the tackle action too. The change of play mode does not affect cycles of illegal defense situations.