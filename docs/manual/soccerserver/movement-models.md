## Basics

In each simulation step, the movement of each object is calculated in the following manner:

\[ 
\begin{align*}
(u_x^{t+1},u_y^{t+1}) &= (v_x^t,v_y^t)+(a_x^t,a_y^t) : \text{accelerate} \\
(p_x^{t+1},p_y^{t+1}) &= (p_x^t,p_y^t)+(u_x^{t+1},u_y^{t+1}) : \text{move} \\
(v_x^{t+1},v_y^{t+1}) &= \text{decay} \times (u_x^{t+1},u_y^{t+1}) : \text{decay speed} \\
(a_x^{t+1},a_y^{t+1}) &= (0,0) : \text{reset acceleration}
\end{align*}
\]

where, \((p_x^t,p_y^t)\), and \((v_x^t,v_y^t)\) are respectively position and velocity of the object in timestep \(t\). Decay is a decay parameter specified by `ball_decay` or `player_decay`. \((a_x^t,a_y^t)\) is acceleration of the object, which is derived from the Power parameter in `dash` (in the case the object is a player) or `kick` (in the case of a ball) commands in the following manner:

\[ 
(a_x^{t},a_y^{t}) = \text{Power} \times \text{power\_rate} \times (\cos(\theta^t),\sin(\theta^t))
\]

where \(\theta^t\) is the direction of the object in timestep \(t\) and `power_rate` is `dash_power_rate` or is calculated from `kick_power_rate` as described in Sec. [sec-kickmodel](sec-kickmodel.md). In the case of a player, this is just the direction the player is facing. In the case of a ball, its direction is given as the following manner:

\[ 
\theta^t_{ball} = \theta^t_{kicker} + \text{Direction}
\]

where \(\theta^t_{ball}\) and \(\theta^t_{kicker}\) are directions of the ball and kicking player respectively, and *Direction* is the second parameter of a **kick** command.

## Movement Noise Model

In order to reflect unexpected movements of objects in the real world, `rcssserver` adds noise to the movement of objects and parameters of commands.

Concerning movements, noise is added into Eqn. \[ \eqref{eq:u-t} \] as follows: **TODO: new noise model. See [12.0.0 pre-20071217] in NEWS**

\[ 
(u_x^{t+1},u_y^{t+1}) = (v_x^{t}, v_y^{t}) + (a_x^{t}, a_y^{t}) + (\tilde{r}_{\mathrm rmax},\tilde{r}_{\mathrm rmax})
\]

where \(\tilde{r}_{\mathrm rmax}\) is a random number whose distribution is uniform over the range \([-{\mathrm rmax},{\mathrm rmax}]\). \({\mathrm rmax}\) is a parameter that depends on the amount of velocity of the object as follows:

\[ 
{\mathrm rmax} = {\mathrm rand} \cdot |(v_x^{t}, v_y^{t})|
\]

where \({\mathrm rand}\) is a parameter specified by **server::player_rand** or **server::ball_rand**.

Noise is added also into the *Power* and *Moment* arguments of a command as follows:

\[ 
\text{argument} = (1 + \tilde{r}_{\mathrm rand}) \cdot \text{argument}
\]

## Collision Model

### Collision with other movable objects

If at the end of the simulation cycle, two objects overlap, then the objects are moved back until they do not overlap. Then the velocities are multiplied by -0.1. Note that it is possible for the ball to go through a player as long as the ball and the player never overlap at the end of the cycle.

### Collision with goal posts

Goal posts are circular with a radius of 6cm and they are located at:

\[ 
\begin{align*}
x &= \pm (\text{FIELD\_LENGTH} \cdot 0.5 - 6cm)\\
y &= \pm (\text{GOAL\_WIDTH} \cdot 0.5 + 6cm)
\end{align*}
\]

The goal posts have different collision dynamics than other objects. An object collides with a post if its path gets within object.size + 6cm of the center of the post. An object that collides with the post bounces off elastically.