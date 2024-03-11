


import React, {useState} from 'react';
import { useWebSocket} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';

const ServerConnection = ({ windowKey, windowState, 
    toggleVisibility, toggleMinimized,
    handleDragStop, handleFocus,
    handleResize, handleResizeStop }) => {
    

    const [serverIp, setServerIp] = useState("localhost");
    const [serverPort, setServerPort] = useState("10789");

    // Websocket setup (from global context)
    const { connect } = useWebSocket();
          
    const handleConnect = () => {
        console.log('Connect to ' + serverIp + ":"+serverPort);
        connect(serverIp, serverPort);
    };

    return (
        <DraggableResizableWindow
          windowKey={windowKey}
          isMinimized={windowState.isMinimized}
          position={windowState.position}
          size={windowState.size}
          zIndex={windowState.zIndex}
          title={windowState.title}
          handleDragStop={handleDragStop}
          handleFocus={handleFocus}
          handleResize={handleResize}
          handleResizeStop={handleResizeStop}
          handleClose={toggleVisibility}
          toggleMinimized={toggleMinimized}
          minConstraints={windowState.minConstraints}
        >
        <div style={{alignItems:"center", padding:"10px"}}>
            <input
                type="text"
                value={serverIp}
                style={{width:"100%"}}
                onChange={(e) => setServerIp(e.target.value)}
                placeholder="Server IP"
            />
            <input
                type="text"
                value={serverPort}
                style={{width: "100%"}}
                onChange={(e) => setServerPort(e.target.value)}
                placeholder="Server Port"
            />
            <button onClick={handleConnect}>Connect</button>
        </div>
        </DraggableResizableWindow>
      );
    
};

export default ServerConnection;


  