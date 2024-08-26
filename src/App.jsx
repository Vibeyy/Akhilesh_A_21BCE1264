import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [gameState, setGameState] = useState([]);
  const [currentTurn, setCurrentTurn] = useState("A");
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [validMoves, setValidMoves] = useState([]);
  const [moveHistory, setMoveHistory] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
  
    const ws = new WebSocket('ws://localhost:1245');
    
    
    ws.onopen = () => {
      console.log('WebSocket connected'); /*to check log*/
      setSocket(ws);
      initializeGame(ws);
    };

   
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.game_state) {
        setGameState(data.game_state);
        setCurrentTurn(data.current_turn);
      } else if (data.status === 'move_successful') {
        setGameState(data.game_state);
        setCurrentTurn(data.current_turn);
        setMoveHistory((prevHistory) => [...prevHistory, `${data.character_name} moved to (${data.new_position})`]);
      } else {
        alert("Move failed!");
      }
    };

  
    ws.onclose = () => {
      console.log('WebSocket disconnected'); /*to check*/
    };

  
    return () => {
      ws.close();
    };
  }, []);


  const initializeGame = (socket) => {
    socket.send(JSON.stringify({ action: 'state' }));
  };

 
  const handleCharacterClick = async (x, y) => {
    const selected = gameState[x][y];
    if (selected && selected.player === currentTurn) {
      setSelectedCharacter({ name: selected.name, x, y });

     
      socket.send(JSON.stringify({
        action: 'valid_moves',
        name: selected.name,
        position: [x, y]
      }));
    }
  };

 
  const handleMoveClick = (x, y) => {
    if (selectedCharacter) {
      socket.send(JSON.stringify({
        action: 'move',
        player_id: currentTurn,
        character_name: selectedCharacter.name,
        new_position: [x, y]
      }));
    }
  };

  return (
    <div className="game-container">
      <h1>Pawns And Heroes</h1>
      <h2>Current Turn: Player {currentTurn}</h2>

      <div className="board">
        {gameState.map((row, i) =>
          row.map((cell, j) => (
            <div
              key={`${i}-${j}`}
              className="cell"
              onClick={() => handleCharacterClick(i, j)}
            >
              {cell ? cell.name : ''}
            </div>
          ))
        )}
      </div>

      {selectedCharacter && (
        <div className="valid-moves">
          <h3>Valid Moves for {selectedCharacter.name}</h3>
          {validMoves.map(([x, y]) => (
            <button key={`${x}-${y}`} onClick={() => handleMoveClick(x, y)}>
              Move to ({x}, {y})
            </button>
          ))}
        </div>
      )}

      <div className="move-history">
        <h3>Move History</h3>
        <ul>
          {moveHistory.map((move, index) => (
            <li key={index}>{move}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
