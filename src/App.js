import React, { useState } from 'react';
import { WebSocketProvider } from './components/WebSocketContext';

import './App.css';
import ToolBar from './components/Toolbar'; // Adjust the path as necessary
import TrainerSettings from './components/TrainerSettings';
import SettingsMenu from './components/Settings';
import ExampleWindow from './components/ExampleWindow';
import CanvasComponent from './components/CanvasComponent';
import ServerConnection from './components/ServerConnection';

function App() {
  
  const [highestZIndex, setHighestZIndex] = useState(100);

  const bringToFront = () => {
    setHighestZIndex(highestZIndex + 1);
    return highestZIndex + 1;
  };

  

  return (
    <WebSocketProvider>
      <div className="App">
        <SettingsMenu bringToFront={bringToFront}/>
        <ExampleWindow bringToFront={bringToFront}/>
        <ToolBar bringToFront={bringToFront}/>
        <TrainerSettings bringToFront={bringToFront}/>
        <ServerConnection bringToFront={bringToFront}/>
        <CanvasComponent />
      </div>
    </WebSocketProvider>
  );
}

export default App;