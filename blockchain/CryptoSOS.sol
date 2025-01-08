//SPDX-License-Identifier: GPL-1.0-or-later
pragma solidity ^0.8.26;


contract CryptoSOS {
    address private owner;
    
    //adding the last parameter in order to have the same code with
    //the multiplayer version
    //might remove it when im done with both
    event StartGame(address,address,uint128);
    event Move(address,uint8,uint8,uint128);
    event Winner(address,uint128);
    event Tie(address,address,uint128);

    //todo understand memory in Ethereum
    struct SoSBoard {
        // should be initialised with S,O,X-> for empty cells
        uint8[9] values;
        //default value is address(0) so i can check if they have joined
        address payable player1;
        uint256 player1JoinedAtTimestamp;
        address payable player2;
        bool player1Plays; 
        uint256 lastTurnTimeStamp;
    }
    uint8[9] default_game = [0,0,0,0,0,0,0,0,0];

    SoSBoard[] AvailableGames;
    uint128 gamesCounter = 0;
    mapping(address => uint128) private GameForPlayer;
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
            SoSBoard memory board = getGameOfPlayer(msg.sender);
            board.player2 = payable(msg.sender);
            emit StartGame(board.player1,board.player2,1);
        } else if(gamesCounter == 0) {
            SoSBoard memory newGame = SoSBoard(default_game,payable(msg.sender),block.timestamp,payable(address(0)),true,uint256(0));
            AvailableGames.push(newGame);
            gamesCounter++;
            GameForPlayer[msg.sender] = gamesCounter;
        } else {
            //emit Message that there is already a game being played
            revert();
        }
        
    }

    // If a player joins, and within 2 minutes no other player has joined, he is allowed to get a full
    // reimbursement (1 ether) by calling the cancel() function
    function cancel() public {
        //check if the map has his address
        //if not refund him from the balance
        //reset the game by emptying the hash map or moving the index back to 0
        require(gamesCounter == 1,"There is no current game being played");
        require(GameForPlayer[msg.sender] != uint128(0x0),"The sender has not joined the game");
        SoSBoard memory board = getGameOfPlayer(msg.sender);
        require(board.player1 == msg.sender);
        uint256 currentTime = block.timestamp;
        if ( (currentTime - board.player1JoinedAtTimestamp) > 2 minutes  ) {
            if (board.player1.send(1 ether)) {
                gamesCounter = 0;
            } else {
                revert();
            }
        }
        
    }

    // While a game is in progress, if the player whose turn it is to play delays his move by 1 minute
    // or more, the other player (i.e., the one who made the last move) is allowed to call the
    // tooslow() function, and get 1.5 ether back, leaving the remaining 0.5 in the assets of the
    // CryptoSOS smart contract, and terminating the game. In this case, the player who
    // successfully called the tooslow() function is considered a winner, therefore the
    // Winner(address) event should be emitted normally, as described earlier.
    //If none of the players have played for 5 minutes, then the owner is allowed to call
    //tooslow(), ending the game ahead of time
    function tooslow() public payable {
        require(gamesCounter == 1, "There is no current game being played");
        require(GameForPlayer[msg.sender] != uint128(0x0),"The sender has not joined the game");
        uint256 currentTime = block.timestamp;
        SoSBoard memory board = getGameOfPlayer(msg.sender);
        if ( (currentTime - board.lastTurnTimeStamp) > 1 minutes ) {
            address sendMoneyTo = address(0);
            if (board.player1Plays) {
                //means player2 gets the money bcs player1 was slow
                sendMoneyTo = board.player2;
            } else {
                sendMoneyTo = board.player1;
            }

            //get him 1.5 ether back
            if (board.player1.send(1.5 ether)) {
                //clear the game being played and the related index
                gamesCounter = 0;
                //emit Winner
            } else {
                revert();
            }
        }

    }   
    // At any point, anyone may call the getGameState() function, which should return a 9-
    // character-long string, in which each character is one of {-,S,O}
    function getGameState() public view returns (SoSBoard memory) {
        //for the non-concurrent version we just return the first (and only available) game
        require(gamesCounter == 1, "There is no current game being played");
        return AvailableGames[1];
    }

    function getGameOfPlayer(address pl) public view returns (SoSBoard memory) {
        return AvailableGames[GameForPlayer[pl]];
    }

    function checkTripletForSoS(uint8 box1,uint8 box2,uint8 box3) private pure returns (bool) {
        return box1 == 1 && box2 == 2 && box3 == 1;
    }

    function checkBoardPositions(SoSBoard memory board,uint8 pos1,uint8 pos2,uint8 pos3) private pure returns (bool) {
        return checkTripletForSoS(board.values[pos1-1],board.values[pos2-1],board.values[pos3-1]);
    }

    function boardIsFull(SoSBoard memory board) private pure returns (bool) {
        //loop will probably be unrolled anyway, i could do it myself
        for (uint8 i = 0; i < board.values.length; i++) {
            if (board.values[i] == 0) return false;
        }
        return true;
    }

    function checkForWinnerInGame(SoSBoard memory board,address payable whoJustPlayed) public payable {
        bool isGameFinished = //check horizontaly -> 1,2,3 | 4,5,6 | 7,8,9
                      checkBoardPositions(board,1,2,3) || 
                      checkBoardPositions(board,4,5,6) || 
                      checkBoardPositions(board,7,8,9) ||
                      //check vertically -> 1,4,7 | 2,5,8 | 3,6,9
                      checkBoardPositions(board,1,4,7) ||
                      checkBoardPositions(board,2,5,8) || 
                      checkBoardPositions(board,3,6,9) ||
                      //check diagonally -> 1,5,9 | 3,5,7
                      checkBoardPositions(board,1,5,9) ||
                      checkBoardPositions(board,3,5,7);
        if (isGameFinished) {
            emit Winner(whoJustPlayed,1);
            if (whoJustPlayed.send(1.8 ether)){
                //do something
            } else {
                revert("Something went wrong when sending the 1.8 ether to the winner address");
            }
        } else {
            if (boardIsFull(board)) {
                emit Tie(board.player1,board.player2,1);
                //send 0.95 to each account
                if (board.player1.send(0.95 ether) && board.player2.send(0.95 ether)) {
                    
                } else {
                    revert("Error in transfers for TIE result");
                }
            }
        }
        
        

    }


    function placeThing(uint8 thing,uint8 position) private {
        //this should probably be storage
        SoSBoard memory game = getGameOfPlayer(msg.sender);
        //the cell should be empty
        require(game.values[position] == 0,"the position you chose is not empty");
        if (game.player1Plays && msg.sender == game.player1) {
            //p1 turn and the msg was by p1
            game.player1Plays = !game.player1Plays;
            game.values[position] = thing;
            game.lastTurnTimeStamp = block.timestamp;
            checkForWinnerInGame(game,game.player1);
        } else if (!game.player1Plays && (msg.sender == game.player2)){
            //p2 turn and the msg was by p2
            game.player1Plays = !game.player1Plays;
            game.values[position] = thing;
            game.lastTurnTimeStamp = block.timestamp;
            checkForWinnerInGame(game,game.player2);
        } else {
            //wrong player sent message dont do anything
        }
    }

    function placeS(uint8 choice) public {
        placeThing(1,choice);
        
        
    }

    function placeO(uint8 choice) public {
        placeThing(2,choice);
    }



}