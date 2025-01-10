//SPDX-License-Identifier: GPL-1.0-or-later
pragma solidity ^0.8.26;


contract CryptoSOS {
    address payable private owner;
    uint private totalProfits;
    //adding the last parameter in order to have the same code with
    //the multiplayer version

    event StartGame(address,address,uint128);
    event Move(address,uint8,uint8,uint128);
    event Winner(address,uint128);
    event Tie(address,address,uint128);
    event GameCancelled(address,uint128);
    struct SoSBoard {
        
        uint8[9] values;
        address payable player1;
        uint256 player1JoinedAtTimestamp;
        address payable player2;
        bool player1Plays; 
        uint256 lastTurnTimeStamp;
    }
    //0 means empty cell,1->S,2->O
    uint8[9] default_game = [0,0,0,0,0,0,0,0,0];

    SoSBoard[] AvailableGames;
    uint8 CurrentState = 0;
    mapping(address => uint128) private GameForPlayer;
    constructor () {
        owner = payable(msg.sender);
    }


   


    // In order to start playing, a player must call the join() function of CryptoSOS. Then he
    // enters the waiting lobby, until a second player calls join() too, at which point a new game
    // starts between these two players. If a third player calls join(), this will fail (i.e., revert()
    // with a message that a game is already in progress). Of course, after a game has ended, it
    // should be possible for any two players to join and start a new game.
    function join() public payable {
        require(msg.value == 1 ether);
        if (CurrentState == 1) {
            GameForPlayer[msg.sender] = 1;
            SoSBoard storage board = getGameOfPlayer(msg.sender);
            board.player2 = payable(msg.sender);
            emit StartGame(board.player1,board.player2,1);
        } else if(CurrentState == 0) {
            SoSBoard memory newGame = SoSBoard(default_game,payable(msg.sender),block.timestamp,payable(address(0)),true,uint256(0));
            AvailableGames.push(newGame);
            CurrentState = 1;
            GameForPlayer[msg.sender] = 1;
        }
        
    }

    // If a player joins, and within 2 minutes no other player has joined, he is allowed to get a full
    // reimbursement (1 ether) by calling the cancel() function
    function cancel() public {
        //reset the game by emptying the hash map or moving the index back to 0
        require(CurrentState == 1,"There is no current game being played");
        require(GameForPlayer[msg.sender] != uint128(0x0),"The sender has not joined the game");
        SoSBoard memory board = getGameOfPlayer(msg.sender);
        require(board.player1 == msg.sender);
        uint256 currentTime = block.timestamp;
        if ( (currentTime - board.player1JoinedAtTimestamp) > 2 minutes  ) {
            board.player1.send(1 ether);
            CurrentState = 0;
            emit GameCancelled(board.player1,1);
        }
        
    }
    // The owner of CryptoSOS (i.e., the account that deployed the
    // CryptoSOS smart contract) can claim the assets collected by CryptoSOS, by calling the
    // sweepProfit(uint amount) function, which should send the requested amount to
    // the owner’s account, assuming the balance is sufficient, and that there is enough money left
    // to pay off prizes or return amounts.
    function sweepProfit(uint amount ) public {
        require(msg.sender == owner,"The profits are for running CryptoSOS");
        if(owner.send(amount)) {
            totalProfits -= amount;
        }
    }

    // While a game is in progress, if the player whose turn it is to play delays his move by 1 minute
    // or more, the other player (i.e., the one who made the last move) is allowed to call the
    // tooslow() function, and get 1.5 ether back, leaving the remaining 0.5 in the assets of the
    // CryptoSOS smart contract, and terminating the game. In this case, the player who
    // successfully called the tooslow() function is considered a winner, therefore the
    // Winner(address) event should be emitted normally, as described earlier.
    // If none of the players have played for 5 minutes, then the owner is allowed to call
    // tooslow(), ending the game ahead of time
    function tooslow() public payable {
        require(CurrentState == 1, "There is no current game being played");
        require(GameForPlayer[msg.sender] != uint128(0x0),"The sender has not joined the game");
        uint256 currentTime = block.timestamp;
        SoSBoard memory board = getGameOfPlayer(msg.sender);
        if ( (currentTime - board.lastTurnTimeStamp) > 1 minutes ) {
            address payable sendMoneyTo = payable(address(0));
            if (board.player1Plays) {
                //means player2 gets the money bcs player1 was slow
                sendMoneyTo = payable(board.player2);
            } else {
                sendMoneyTo = payable(board.player1);
            }

            totalProfits += 0.5 ether;
            //No checking of the result to discourage malicious behaviour 
            sendMoneyTo.send(1.5 ether);
            //clear the game being played and the related index
            CurrentState = 0;
            emit Winner(sendMoneyTo,1);
                
            
        }

    }   

    function checkGameState() public view returns (SoSBoard memory) {
        require(CurrentState == 1, "There is no current game being played");
        return AvailableGames[0];
    }

    //each value of the board is is one of {-,S,O} => {0,1,2}
    function getGameState() private view returns (SoSBoard storage) {
        //for the non-concurrent version we just return the first (and only available) game
        require(CurrentState == 1, "There is no current game being played");
        return AvailableGames[0];
    }

    function getGameOfPlayer(address pl) private view returns (SoSBoard storage) {
        require(CurrentState == 1, "There is no current game being played");
        return AvailableGames[0];
    }

    function checkTripletForSoS(uint8 box1,uint8 box2,uint8 box3) private pure returns (bool) {
        return box1 == 1 && box2 == 2 && box3 == 1;
    }

    function checkBoardPositions(SoSBoard storage board,uint8 pos1,uint8 pos2,uint8 pos3) private view returns (bool) {
        return checkTripletForSoS(board.values[pos1-1],board.values[pos2-1],board.values[pos3-1]);
    }

    function boardIsFull(SoSBoard storage board) private view returns (bool) {
        //loop will probably be unrolled anyway, i could do it myself
        for (uint8 i = 0; i < board.values.length; i++) {
            if (board.values[i] == 0) return false;
        }
        return true;
    }

    //i want a way to only have it be storage in here, not everywhere
    function checkForWinnerInGame(SoSBoard storage board,address payable whoJustPlayed) private {
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
                totalProfits += 0.2 ether;
            } else {
                //something else
            }
        } else {
            if (boardIsFull(board)) {
                emit Tie(board.player1,board.player2,1);
                board.player1.send(0.95 ether);
                board.player2.send(0.95 ether);
                totalProfits += 0.1 ether;
                
            }
        }
        
        

    }

    function whoPlays() public view returns (bool) {
        return AvailableGames[0].player1Plays;
    }


    function placeThing(uint8 thing,uint8 position) private {
        SoSBoard storage game = getGameOfPlayer(msg.sender);
        require(game.values[position] == 0,"the cell you chose is not empty");
        if (game.player1Plays && msg.sender == game.player1) {
            //p1 turn and the msg was by p1
            game.player1Plays = false;
            game.values[position] = thing;
            game.lastTurnTimeStamp = block.timestamp;
            checkForWinnerInGame(game,game.player1);
        } else if (!game.player1Plays && msg.sender == game.player2){
            //p2 turn and the msg was by p2
            game.player1Plays = true;
            game.values[position] = thing;
            game.lastTurnTimeStamp = block.timestamp;
            checkForWinnerInGame(game,game.player2);
        } else {
            revert("It is not your turn currently");
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