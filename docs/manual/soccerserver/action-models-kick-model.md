# Kick Model

The *kick* command takes two parameters: the kick power the player client wants to use (between **server::minpower** and **server::maxpower**) and the angle the player kicks the ball to. The angle is given in degrees and has to be between **server::minmoment** and **server::maxmoment** (see [Ball and Kick Model Parameters](#param-kick) for current parameter values).

Once the *kick* command arrives at the server, the kick will be executed if the ball is kickable for the player and the player is not marked offside. The ball is kickable for the player if the distance between the player and the ball is between 0 and **kickable_margin**. Heterogeneous players can have different kickable margins. For the calculation of the distance during this section, it is important to know that when we talk about the distance between the player and the ball, we refer to the minimal distance between the outer shape of both player and ball. So the distance in this section is the distance between the center of both objects *minus* the radius of the ball *minus* the radius of the player.

The first thing to be calculated for the kick is the effective kick power ep:

\[ 
\mathrm{ep} = \mathrm{kick\_power} \cdot \mathrm{kick\_power\_rate} 
\]

If the ball is not directly in front of the player, the effective kick power will be reduced by a certain amount dependent on the position of the ball with respect to the player. Both angle and distance are important.

If the relative angle of the ball is \(0^\circ\) with respect to the body direction of the player client - i.e., the ball is in front of the player - the effective power will stay as it is. The larger the angle gets, the more the effective power will be reduced. The worst case is if the ball is lying behind the player (angle \(180^\circ\)): the effective power is reduced by 25%.

The second important variable for the effective kick power is the distance from the ball to the player: it is quite obvious that - should the kick be executed - the distance between ball and player is between 0 and player's **kickable margin**. If the distance is 0, the effective kick power will not be reduced again. The further the ball is away from the player client, the more the effective kick power will be reduced. If the ball distance is player's **kickable margin**, the effective kick power will be reduced by 25% of the original kick power.

The overall worst case for kicking the ball is if a player kicks a distant ball behind itself: 50% of kick power will be used. For the effective kick power, we get the formula:

\[ 
\mathrm{ep} = \mathrm{ep} \cdot \left(1 - 0.25 \cdot \frac{\mathrm{dir\_diff}}{180^\circ} - 0.25 \cdot \frac{\mathrm{dist\_ball}}{\mathrm{kickable\_margin}}\right) 
\]

(where dir_diff means the absolute direction difference between ball and the player’s body direction, dist_diff means the absolute distance between ball and player.) \(0\le\mathrm{dir\_diff}\le180^\circ\land0\le\mathrm{dist\_diff}\le\mathrm{kickable\_margin}\)

The effective kick power is used to calculate \(\vec{a}_{{n}_{i}}\), an acceleration vector that will be added to the global ball acceleration \(\vec{a}_{n}\) during cycle \(n\) (remember that we have a multi-agent system and *each* player close to the ball can kick it during the same cycle).

There is a server parameter, **server::kick_rand**, that can be used to generate some noise to the ball acceleration. For the default players, **kick_rand** is 0.1. For heterogeneous players, **kick_rand** depends on **player::kick_rand_delta_factor** in `player.conf` and on the actual kickable margin.
  
- **TODO: new kick/tackle noise model.**
- **TODO: heterogeneous kick power rate.**

During the transition from simulation step \(n\) to simulation step \(n+1\) acceleration \(\vec{a}_{n}\) is applied:

1. \(\vec{a}_{n}\) is normalized to a maximum length of **server::ball_accel_max**.
2. \(\vec{a}_{n}\) is added to the current ball speed \(\vec{v}_{n}\). \(\vec{v}_{n}\) will be normalized to a maximum length of **server::ball_speed_max**.
3. Noise \(\vec{n}\) and wind \(\vec{w}\) will be added to \(\vec{v}_{n}\). Both noise and wind are configurable in `server.conf`. The responsible parameter for the noise is **server::ball_rand**. Both direction and length of the noise vector are within the interval \([-|\vec{v}_{n}| \cdot \mathrm{ball\_rand} \ldots |\vec{v}_{n}| \cdot \mathrm{ball\_rand}]\).
4. The new position of the ball \(\vec{p}_{n+1}\) is the old position \(\vec{p}_{n}\) plus the velocity vector \(\vec{v}_{n}\) (i.e., the maximum distance difference for the ball between two simulation steps is **server::ball_speed_max**).
5. **server::ball_decay** is applied to the velocity of the ball: \(\vec{v}_{n+1} = \vec{v}_{n} \cdot \mathrm{ball\_decay}\). Acceleration \(\vec{a}_{n+1}\) is set to zero.

With the current settings, the ball covers a distance up to 50, assuming an optimal kick. 55 cycles after an optimal kick, the distance from the kick-off position to the ball is about 48, the remaining velocity is smaller than 0.1. 18 cycles after an optimal kick, the ball covers a distance of 34 - 34 and the remaining velocity is slightly smaller than 1.

Implications from the kick model and the current parameter settings are that it still might be helpful to use several small kicks for a compound kick -- for example stopping the ball, kicking it to a more advantageous position within the kickable area, and kicking it to the desired direction. It would be another possibility to accelerate the ball to maximum speed without putting it to relative position \((0,0^{\circ})\) using a compound kick.

### Ball and Kick Model Parameters
<table>
  <tr>
    <th>Default Parameters</th>
    <th>Default Value (Range)</th>
    <th>Heterogeneous Player Parameters</th>
    <th>Value</th>
  </tr>
  <tr>
    <td>server::minpower</td>
    <td>-100</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::maxpower</td>
    <td>100</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::minmoment</td>
    <td>-180</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::maxmoment</td>
    <td>180</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::kickable_margin</td>
    <td>0.7 ([0.6, 0.8])</td>
    <td>player::kickable_margin_delta_min</td>
    <td>-0.1</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>player::kickable_margin_delta_max</td>
    <td>0.1</td>
  </tr>
  <tr>
    <td>server::kick_power_rate</td>
    <td>0.027</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::kick_rand</td>
    <td>0.1 ([0.0, 0.2])</td>
    <td>player::kick_rand_delta_factor</td>
    <td>1</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>player::kickable_margin_delta_min</td>
    <td>-0.1</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>player::kickable_margin_delta_max</td>
    <td>0.1</td>
  </tr>
  <tr>
    <td>server::ball_size</td>
    <td>0.085</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::ball_decay</td>
    <td>0.94</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::ball_rand</td>
    <td>0.05</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::ball_speed_max</td>
    <td>3.0</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::ball_accel_max</td>
    <td>2.7</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::wind_force</td>
    <td>0.0</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::wind_dir</td>
    <td>0.0</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>server::wind_rand</td>
    <td>0.0</td>
    <td></td>
    <td></td>
  </tr>
</table>