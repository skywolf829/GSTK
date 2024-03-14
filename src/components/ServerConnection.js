


import React, {useState, useEffect } from 'react';
import { useWebSocket } from '../utils/WebSocketContext';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';
import { useIconBar } from './IconBarContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowUp, faArrowDown } from '@fortawesome/free-solid-svg-icons';

const ServerConnection = ({ windowKey, windowState, 
    toggleVisibility, toggleMinimized,
    handleDragStop, handleFocus,
    handleResize, handleResizeStop,
    resetScreenPosition, setTitle}) => {
    

    const [serverIp, setServerIp] = useState("localhost");
    const [serverPort, setServerPort] = useState("10789");
    const { registerIcon } = useIconBar();
    // Websocket setup (from global context)
    const { connect, connected, disconnect, dataSent, dataReceived} = useWebSocket();

    const getStateColorRGBA = () => {
        const opacity =  windowState.isVisible ? 1.0 : 0.3;
        return connected ? `rgba(0, 122, 31, ${opacity})` : `rgba(255, 100, 100, ${opacity})`;
    };
    const getStateColorRGB = () => {
        return connected ? `rgb(0, 122, 31)` : `rgb(255, 100, 100)`;
    };
    useEffect(() => {
        // Define the props for the Icon component
        const contextMenuItems = [
            "Reset position",
            windowState.isMinimized ? "Maximize": "Minimize", 
            windowState.isVisible ? "Close" :"Open"
        ];
        const contextMenuCallbacks = [
            () => {resetScreenPosition(windowKey)},
            () => {toggleMinimized(windowKey)},
            () => {toggleVisibility(windowKey)}
        ];
        if(connected){
            contextMenuItems.unshift("Disconnect");
            contextMenuCallbacks.unshift(() => {disconnect()});
        }
        
        const backgroundColor = getStateColorRGBA();
        const iconProps = {
            windowKey: windowKey,
            windowState: windowState, 
            toggleWindowVisible: () => {toggleVisibility(windowKey)},
            contextMenuItems: contextMenuItems,
            contextMenuCallbacks: contextMenuCallbacks,
            backgroundColor: backgroundColor
        };
        registerIcon(windowKey, iconProps);
    }, [windowState.isVisible, windowState.isMinimized, connected]);
   
    useEffect(() => {
        if(windowState.isMinimized){
            setTitle(windowKey, 
                <span>Server Connection
                    <span style={{alignContent: 'right', alignItems: 'right'}}>
                        <FontAwesomeIcon icon={faArrowUp} color='rgb(100, 255, 100)' />
                        {(dataSent/1024).toFixed(2)}
                        <FontAwesomeIcon icon={faArrowDown} color='rgb(255, 100, 100)' />
                        {(dataReceived/1024).toFixed(2)}
                    </span>
                </span>);
        }
        else{
            setTitle(windowKey, <span>Server Connection</span>);
        }
    }, [windowState.isMinimized, dataReceived, dataSent]);
      
    const handleConnect = () => {
        if(connected){
            disconnect();
        }
        else{
            connect(serverIp, serverPort);
        }
    };

    return (
        windowState.isVisible && (
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
            barColor={getStateColorRGB()}
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
                <button onClick={handleConnect}>{ connected ? "Disconnect" : "Connect"}</button>
                {connected && (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: 0, padding: '5px 0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', margin: 0 }}>
                      <FontAwesomeIcon icon={faArrowUp} color="green" />
                      <p style={{ marginLeft: '8px', margin: 0 }}>Data sent: {(dataSent / 1024).toFixed(2)} MB/s</p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', margin: '4px 0' }}>
                      <FontAwesomeIcon icon={faArrowDown} color="red" />
                      <p style={{ marginLeft: '8px', margin: 0 }}>Data received: {(dataReceived / 1024).toFixed(2)} MB/s</p>
                    </div>
                  </div>
                )}
            </div>
            </DraggableResizableWindow>
        )
      );
    
};

export default ServerConnection;


  