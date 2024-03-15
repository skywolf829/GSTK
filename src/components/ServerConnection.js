


import React, {useState, useEffect } from 'react';
import { useWebSocket, useWebSocketListener} from './WebSocketContext';
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
    const [dataSent, setDataSent] = useState(0);
    const [dataReceived, setDataReceived] = useState(0);
    const [runningDataReceived, setRunningDataReceived] = useState(0);
    const [runningDataSent, setRunningDataSent] = useState(0);

    // Websocket setup (from global context)
    const { subscribe, subscribeSend, connect, connected, disconnect } = useWebSocket();
    
    useWebSocketListener(subscribe, '*', (message) => {
        setRunningDataReceived(runningDataReceived+message.size);
    });
    useWebSocketListener(subscribeSend, '*', (message) => {
        setRunningDataSent(runningDataSent+message.size);
    });

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
        if(connected){
            setTitle(windowKey, 
                <span>Server Connection
                    <span style={{alignContent: 'right', alignItems: 'right'}}>
                        <FontAwesomeIcon icon={faArrowUp} color='rgb(100, 255, 100)' />
                        {(dataSent/1024).toFixed(2)}
                        <FontAwesomeIcon icon={faArrowDown} color='rgb(255, 100, 20)' />
                        {(dataReceived/1024).toFixed(2)}
                    </span>
                </span>);
        }
        else{
            //setTitle(windowKey, <span>Server Connection</span>);
        }
    }, [connected, dataReceived, dataSent]);
    
    
  
    useEffect(() => {
        const interval = setInterval(() => {
            // Use functional updates to ensure you get the latest state
            setRunningDataReceived((currentData) => {
                const kbps_received = (currentData / 1024); // Convert bytes to kilobytes and divide by time in seconds
                setDataReceived(kbps_received);
                return 0; // Reset the running data received for the next interval
            });
            setRunningDataSent((currentData) => {
                const kbps_sent = (currentData / 1024); // Convert bytes to kilobytes and divide by time in seconds
                setDataSent(kbps_sent);
                return 0; // Reset the running data sent for the next interval
            });
        }, 1000); // Update every second
        return () => clearInterval(interval); // Cleanup the interval on unmount
    }, []);

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
            </div>
            </DraggableResizableWindow>
        )
      );
    
};

export default ServerConnection;


  