import React, { useState, useEffect} from 'react';
import { WebSocketProvider } from './utils/WebSocketContext';

import './css/App.css';
import CanvasComponent from './components/CanvasComponent';
import WindowController from './components/windowController';
import { ModalProvider } from './components/ModalContext';

function App() {
  
  
  const [highestZIndex, setHighestZIndex] = useState(() => {
    const savedZIndex = JSON.parse(localStorage.getItem('highestZIndex'));
    return savedZIndex || 100; // Use saved value, or default to 100 if not found
  });

  useEffect(() => {
    localStorage.setItem('highestZIndex', JSON.stringify(highestZIndex));
  }, [highestZIndex]);


  const bringToFront = () => {
    setHighestZIndex(highestZIndex + 1);
    return highestZIndex + 1;
  };

  

  return (
    <WebSocketProvider>
      <ModalProvider>
        <div className="App">
          <WindowController bringToFront={bringToFront}/>
          <CanvasComponent />
        </div>
      </ModalProvider>
    </WebSocketProvider>
  );
}

export default App;