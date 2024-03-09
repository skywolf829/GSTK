


import React, {useState} from 'react';
import { useWebSocket} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';

const ServerConnection = ({ bringToFront, onClose }) => {
    
    const title = "Server Connection";
    const minConstraints = [220, 115];

    const [serverIp, setServerIp] = useState("localhost");
    const [serverPort, setServerPort] = useState("6789");

    const {
        isVisible, isMinimized, 
        size, position, zIndex,
        toggleVisibility, toggleMinimized,
        handleDragStop, handleFocus,
        handleResize, handleResizeStop,
      } = useWindowSettings(title, minConstraints, bringToFront);


    // Websocket setup (from global context)
    const { connect } = useWebSocket();
          
    const handleConnect = () => {
        console.log('Connect to ' + serverIp + ":"+serverPort);
        connect(serverIp, serverPort);
    };

    return (
        <DraggableResizableWindow
          isVisible={isVisible}
          isMinimized={isMinimized}
          position={position}
          size={size}
          zIndex={zIndex}
          title={title}
          onDragStop={handleDragStop}
          onFocus={handleFocus}
          onResize={handleResize}
          onResizeStop={handleResizeStop}
          onClose={onClose}
          toggleVisibility={toggleVisibility}
          toggleMinimized={toggleMinimized}
          minConstraints={minConstraints}
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


  