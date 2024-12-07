// todo: SPDX licence
pragma solidity ^0.8.26;


contract CryptoSOS {
    address private owner;
    //todo Events
    // StartGame(address,address)
    // Move(address, uint8, uint8)
    // Winner(address)
    // Tie(address, address)
    //todo understand memory in Ethereum
    struct SoSBoard {
        // should be initialised with S,O,X-> for empty cells
        uint8[9] values;
        //default value is address(0) so i can check if they have joined
        address player1;
        address player2;
        bool player1Plays; 
    }
    uint8[9] default_game = [0,0,0,0,0,0,0,0,0];

    SoSBoard[] AvailableGames;
    uint128 gamesCounter = 0;
    mapping(address => uint128) private GameForPlayer;
    // mapping(uint128 => SoSBoard) private BoardOfGame;
    constructor () {
        owner = msg.sender;
    }


    // In order to start playing, a player must call the join() function of CryptoSOS. Then he
    // enters the waiting lobby, until a second player calls join() too, at which point a new game
    // starts between these two players. If a third player calls join(), this will fail (i.e., revert()
    // with a message that a game is already in progress). Of course, after a game has ended, it
    // should be possible for any two players to join and start a new game.
    function join() public payable {
        require(msg.value == 1 ether);
        if (gamesCounter == 1) {
            GameForPlayer[msg.sender] = 1;
        } else if(gamesCounter == 0) {
            SoSBoard memory newGame = SoSBoard(default_game,msg.sender,address(0),true);
            AvailableGames.push(newGame);
            gamesCounter++;
            GameForPlayer[msg.sender] = gamesCounter;
        } else {
            //
            revert();
        }
        
    }

    // If a player joins, and within 2 minutes no other player has joined, he is allowed to get a full
    // reimbursement (1 ether) by calling the cancel() function
    function cancel() public {

    }

    // While a game is in progress, if the player whose turn it is to play delays his move by 1 minute
    // or more, the other player (i.e., the one who made the last move) is allowed to call the
    // tooslow() function, and get 1.5 ether back, leaving the remaining 0.5 in the assets of the
    // CryptoSOS smart contract, and terminating the game. In this case, the player who
    // successfully called the tooslow() function is considered a winner, therefore the
    // Winner(address) event should be emitted normally, as described earlier.
    function tooslow() public {

    }   
    // At any point, anyone may call the getGameState() function, which should return a 9-
    // character-long string, in which each character is one of {-,S,O}
    function getGameState() public view returns (SoSBoard memory) {
        require(gamesCounter == 1);
        return AvailableGames[1];
    }

    function getGameOfPlayer(address pl) public view returns (SoSBoard memory) {
        return AvailableGames[GameForPlayer[pl]];
    }

    function placeS(uint8 choice) public view {
        SoSBoard memory game = getGameOfPlayer(msg.sender);
        //the cell should be empty
        require(game.values[choice] == 0);
        game.values[choice] = 1;
    }

    function placeO(uint8 choice) public view {
        SoSBoard memory game = getGameOfPlayer(msg.sender);
        require(game.values[choice] == 0);
        game.values[choice] = 1;
    }



}