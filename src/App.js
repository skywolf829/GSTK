import React, { useState, useEffect} from 'react';
import { WebSocketProvider } from './components/WebSocketContext';

import './css/App.css';
import CanvasComponent from './components/CanvasComponent';
import WindowController from './components/windowController';
import { ModalProvider } from './components/ModalContext';
import { IconBarProvider } from './components/IconBarContext';
import IconBar from './components/IconBar';
function App() {
  
  
  const [highestZIndex, setHighestZIndex] = useState(() => {
    const savedZIndex = JSON.parse(localStorage.getItem('highestZIndex'));
    return savedZIndex || 100; // Use saved value, or default to 100 if not found
  });

  useEffect(() => {
    localStorage.setItem('highestZIndex', JSON.stringify(highestZIndex));
  }, [highestZIndex]);


  

  return (
    <ModalProvider>
      <WebSocketProvider>
        <div className="App">
          <IconBarProvider>
            <IconBar />
            <WindowController />
          </IconBarProvider>
          <CanvasComponent />
        </div>
      </WebSocketProvider>
    </ModalProvider>
  );
}

export default App;