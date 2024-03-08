

// MyComponent.js
import React, {useState, useEffect} from 'react';
import { useWebSocket } from './WebSocketContext';
import Draggable from 'react-draggable';
import { Resizable } from 'react-resizable';
import 'react-resizable/css/styles.css';

const ServerConnection = ({ bringToFront }) => {
    
    // Visible state
    const [isVisible, setIsVisible] = useState(true);
    const [serverIp, setServerIp] = useState('localhost');
    const [serverPort, setServerPort] = useState('6789');

    // Size state
    const [size, setSize] = useState({ width: 100, height: 115 });
    const minConstraints = [90, 115];
    const [position, setPosition] = useState({ x: 0, y: 0 });

    // z-index
    const [zIndex, setZIndex] = useState(100);

    // Websocket setup (from global context)
    const { subscribe, connect} = useWebSocket();
    

    const handleConnect = () => {
        connect(serverIp, serverPort);
    };

    useEffect(() => {
        // Load the size and position from localStorage when the component mounts
        const savedSize = JSON.parse(localStorage.getItem('serverConnectionWindowSize'));
        const savedPosition = JSON.parse(localStorage.getItem('serverConnectionPosition'));
    
        if (savedSize) {
          setSize(savedSize);
        }
        if (savedPosition) {
          setPosition(savedPosition);
        }
        // Define the message filter and callback for subscription
        const messageFilter = (message) => message.type === 'connection';
        const messageCallback = (message) => {
            /* Do something with message/message.data */
            console.log(message);
        };

        // Subscribe to messages that pass the filter
        const unsubscribe = subscribe(messageFilter, messageCallback);

        // Unsubscribe from messages when the component unmounts
        return () => unsubscribe();
    }, [subscribe]);

    const handleFocus = () => {
        const newZIndex = bringToFront();
        setZIndex(newZIndex);
    };

    const handleDragStop = (e, data) => {
        // Save the new position to localStorage
        const newPosition = { x: data.x, y: data.y };
        localStorage.setItem('serverConnectionWindowPosition', JSON.stringify(newPosition));
        setPosition(newPosition);
    };

    const handleResizeStop = (event, { size }) => {
        // Save the new size to localStorage
        localStorage.setItem('serverConnectionWindowSize', JSON.stringify(size));
        setSize(size);
    };

    const onResize = (event, { element, size }) => {
        setSize({ width: size.width, height: size.height });
    };
    
    const toggleVisibility = () => {
        setIsVisible(!isVisible);
    };
     
    return (
        isVisible && (
            <Draggable handle=".drag-handle" 
            position={position}
            onStop={handleDragStop}
            onStart={handleFocus}>
                <Resizable width={size.width} 
                height={size.height} 
                onResize={onResize}
                onResizeStop={handleResizeStop}
                minConstraints={minConstraints}>
                    <div style={{ width: size.width, height: size.height, padding: 10, 
                        backgroundColor: '#f0f0f0', position: 'absolute', 
                        borderRadius: '8px', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)' ,
                        display: 'flex', flexDirection: 'column', overflow: 'hidden', 
                        zIndex: zIndex}}>
                        
                        <div style={{ width: '100%', display: 'flex'}}>
                            <span className="drag-handle">Example</span>
                            <button onClick={toggleVisibility} style={{
                                border: 'none',
                                background: 'none',
                                cursor: 'pointer',
                                width: '35px',
                                height: 'auto',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '12px',
                                backgroundColor: '#ccc',
                                //boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                            }}>
                                <span style={{ color: 'white', fontWeight: 'bold' }}>×</span>
                            </button>
                        </div>
                        <br></br>
                        <div>
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
                    </div>
                </Resizable>
            </Draggable>
        )
    );
    
};

export default ServerConnection;


  