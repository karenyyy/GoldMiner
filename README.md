``
<h2>Background:</h2>

<h5>Knowledge bases: Declarative</h5>

Knowledge base = set of sentences (declarations) in a formal language
	
- Adding to the KB
	- Agent Tells the KB what it perceives: $S_i$
	- Inference: derive new statements from $KB + S_i$
- Using the KB
	- Agent Asks the KB what action to take
	- Declaration of the action to take leads to action


<h5>Procedural vs. Declarative Knowledge</h5>

- Agents can be viewed at the knowledge level
	- Behavior is altered by adding knowledge
- Or at the implementation level
	- Procedural rules take KB statements as input
- The agent must be able to:
	- Represent states, actions, etc.
	- Incorporate new percepts
	- Update internal representations of the world
	- Deduce hidden properties of the world
	- Deduce appropriate actions

<h5>Generic knowledge-based agent</h5>

- ![](/home/karen/Pictures/360.png)

<h5>Gold Miner Game description</h5>

![](/home/karen/Pictures/3601.png)

- Environment
	- Squares adjacent to wumpus have strench
	- Squares adjacent to pit have breeze
	- Shooting kills the monster if you are facing it
	- Shooting uses up the only arrow
	- Grabbing picks up gold if in same square

<h5>An example case exploration</h5>
- 1.
 - [1,1] is safe
 -  agent starts in [1,1] 
 -  State detected: [None, None, None, None, None]
 - [1,2] is safe, [2,1] is safe
 - ![](/home/karen/Pictures/3602.png)

- 2.
	- Move to [1,2]
	- State detected: [Breeze, None, None, None, None]
	- ![](/home/karen/Pictures/3604.png)

- 3.
	- Possible Pit in [1,3] or [2,2]
    - ![](/home/karen/Pictures/3605.png)

- 4.

	- Move back to [1,1], then move to [2,1]
	- State detected: [None, None, None, Strench, None]
	- inference: <b>Monster is in [3,1]</b>
    - ![](/home/karen/Pictures/3608.png)

- 5.
	- Move to [2,2]
	- State detected: [None, None, None, None, None]
  	- [2,3] is safe, [3,2] is safe
  	- ![](/home/karen/Pictures/3607.png)


- 6.
	- Move to [3,2]
  	- State detected: [Breeze, Gold, None, Stench, None]
  	- Grab gold-> player win
    - ![](/home/karen/Pictures/3609.png)

<h2>Logic Rules</h2>

 
<h4>Variables:</h4>


$B: Breeze$

$G: Gold$

$S: Strench$

$P: Pit$

$M: Monster$

$x: x \:coordinate \: on \: the \: board$

$y: y \:coordinate \: on \: the \: board$

$ArrowNumber :  $
$$x \:, \: where \:\: x \in\{0, 1\} )$$


$Initial \: state \: in \: each \: cell:$ 
$$S(B, G, P, S, M)=(0,0,0,0,0)$$

$Initial \: state \: of  \: player: $

$$Player(x, y)= (0,0)$$

$Initial \: state \: of  \: player \: direction: $
$$Facing(x), \: where \:\: x \in \{up, down, left, right\}$$


	 
<h4>Rules:</h4>

$\forall x, y \:\: (x \in [0, 3] \wedge x \in \mathbb{Z}) \wedge  (y \in [0,3] \wedge  y \in \mathbb{Z})  \leftrightarrow Valid(x, y)$

$\forall x, y \:\: Valid(x, y) \wedge (S(1)=1) \leftrightarrow Breeze(x, y)$

$\forall x, y \:\: Valid(x, y) \wedge (S(2)=1) \leftrightarrow Gold(x, y)$

$\forall x, y \:\: Valid(x, y) \wedge (S(3)=1)   \leftrightarrow Pit(x, y)$
	
$\forall x, y \:\: Valid(x, y) \wedge (S(4)=1)   \leftrightarrow Strench(x, y)$

$\forall x, y \:\: Valid(x, y) \wedge (S(5)=1)   \leftrightarrow Monster(x, y)$

$\neg Pit(0,0) \wedge \neg Monster(0,0) \rightarrow True$

$\forall x, y \:\: Valid(x, y) \wedge (Player(1)=x)  \wedge (Player(2)=y)   \leftrightarrow PlayerPosition(x, y)$

$\forall x, y \:\: (Valid(x-1, y) \vee Valid(x+1, y) \vee Valid(x, y-1) \vee Valid(x, y+1)) \leftrightarrow HasValidNeighbors(x, y)$

$\forall x, y \:\: Pit(x-1, y) \vee  Pit(x+1, y) \vee Pit(x, y-1) \vee Pit(x, y+1) \leftrightarrow PitAtNeighbors(x, y)$

$\forall x, y \:\: Monster(x-1, y) \vee  Monster(x+1, y) \vee Monster(x, y-1) \vee Monster(x, y+1) \leftrightarrow MonsterAtNeighbors(x, y)$


$\forall x, y \:\: Breeze(x-1, y) \wedge Breeze(x+1, y) \wedge Breeze(x, y-1) \wedge Breeze(x, y+1) \leftrightarrow BreezeAtAllNeighbors(x, y)$

$\forall x, y \:\: Strench(x-1, y) \wedge  Strench(x+1, y) \wedge Strench(x, y-1) \wedge Strench(x, y+1) \leftrightarrow StrenchAtAllNeighbors(x, y)$

$\forall x, y \:\:Gold(x, y) \rightarrow Grab(gold)$

$\forall x, y, k \:\: ((k<x) \wedge (k < y) \wedge (k \in \mathbb{Z}))\wedge Valid(x,y) \wedge PlayerPosition(x,y) \wedge $
$$((Facing(up) \wedge Monster(x,y+k)) \vee (Facing(down) \wedge Monster(x,y-k)) \vee$$
$$(Facing(right) \wedge Monster(x+k,y)) \vee (Facing(left) \wedge Monster(x-k,y)))$$
$$\wedge (ArrowNumber=1) \rightarrow Shoot(monster)$$

$\forall x, y  \:\: Valid(x, y) \wedge Breeze(x,y)  \wedge HasValidNeighbors(x, y) \rightarrow PitAtNeighbors(x, y)$

$\forall x, y  \:\:Valid(x, y) \wedge Strench(x,y) \wedge HasValidNeighbors(x, y) \rightarrow MonsterAtNeighbors(x, y)$

$\forall x, y  \:\:Valid(x, y) \wedge Pit(x,y) \wedge HasValidNeighbors(x, y) \rightarrow BreezeAtAllNeighbors(x, y)$

$\forall x, y  \:\:Valid(x, y) \wedge Monster(x,y) \wedge HasValidNeighbors(x, y)
\rightarrow StrenchAtAllNeighbors(x, y)$

$\forall x, y  \:\:Valid(x,y) \wedge PlayerPosition(x,y) \wedge Monster(x,y) \wedge \neg Shoot(monster) \rightarrow Die(player)$


$\forall x, y  \:\:Valid(x,y) \wedge PlayerPosition(x,y) \wedge Pit(x,y) \rightarrow Die(player)$


$\forall x, y \:\: Valid(x,y) \wedge PlayerPosition(x,y) \wedge Gold(x,y) \wedge Grab(gold) \rightarrow Win(player)$

