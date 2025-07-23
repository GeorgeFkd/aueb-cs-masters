
## SOS Game Implementation in Ethereum Blockchain

### General Approach
What can easily be noticed is that the implementation in both CryptoSOS and MultiSOS, is similar.
This is intentional, in order to reuse the same architecture for both scenarios and avoid duplication.
The general architecture is each address gets mapped to a GameID which in turn gets mapped(with an array)
to an actual game.
This might not serve the purpose for the current edition but provides flexibility and
allows us to extend the game further and add other features.
Events are used in order to notify users about the current state of the game being played.
They could also be used by a GUI app.

### CryptoSOS
The main logic for joining the one game that can be played is based on a state machine with
2 states. For value 0 there is no initialised game and for value 1 there is an initialised game.
### MultiSOS
The difference between the two, implementation wise, is that the matchmaking step differs significantly.
Here the logic is that because of the global ordering of transactions that blockchain enforces
through consensus mechanisms we can be sure that no two transactions are executed in parallel.
Thus we can make the assumption that every time a player joins, we only need to check if the last 
game has a player 1 and a player 2. Otherwise more complex mechanisms would have to be put in place.
The limit is only 50 in order to minimise the financial risk of the whole game operation.

The game is initialised with an empty game, and every time a game gets full, a new empty game
is created.

### Security Considerations
The game, incentives wise, is not too complicated as there is no complex interaction with funds.
As also indicated below, to ensure people can properly refund there could be an extra withdrawal
mechanism.

### Areas for Improvement
When time allows, a better system for refunds will be implemented in order to avoid situations 
where players run out of gas when checking if they won or something in general goes wrong 
regarding transactions. 
Currently malicious behaviour is handled by using send without checking the result value
and reverting when false. It is assumed to be malicious behaviour when a user send fails.

Generally this implementation could be optimised further in terms of gas usage to minimise
expenses.

Matchmaking normally would be better modelled with a Queue, and the user could be notified
he is in the waiting queue. This topic requires more sophisticated data structures than
just a mapping and an array to achieve exhaustive correctness, scalability and memory
efficiency.

Automated Testing would assist in ensuring that proper game scenarios can run smoothly. 

Ideally this Ethereum App to be complete should also come with a GUI that communicates
with the Ethereum Blockchain.
