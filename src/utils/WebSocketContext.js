// WebSocketContext.js
import React, { createContext, useContext, 
  useState, useRef, useEffect } from 'react';

const WebSocketContext = createContext(null);

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false); // State to keep track of connection status
  const subscribersRef = useRef([]);

  let expectingBinary = false;
  let binarySize = 0;
  let messageType = '';

  const connect = (serverIp, serverPort) => {
    if (ws != null) {
      ws.close(); // Ensure any existing connection is closed
    }

    const socket = new WebSocket(`ws://${serverIp}:${serverPort}`);
    socket.binaryType = 'blob'; // Ensure binary messages are received as Blob objects

    socket.addEventListener('open', function (event) {
      console.log('Connected to WS Server');
      setConnected(true); // Set connected state to true when the socket opens
    });

    // Your existing socket.onmessage and other event listeners here...

    socket.onclose = () => {
      console.log('WebSocket Disconnected');
      setConnected(false); // Set connected state to false when the socket closes
      setWs(null); // Reset the WebSocket instance in state
    };

    socket.onmessage = async (event) => {
      if (expectingBinary && event.data instanceof Blob) {
        const blob = event.data;
        if (blob.size === binarySize) {
          // Notify subscribers interested in binary data of this type
          subscribersRef.current.forEach(({ filter, callback }) => {
            if (filter({ type: messageType })) {
              callback(blob);
            }
          });
        }
        expectingBinary = false;  // Reset for the next messages
      } else if (typeof event.data === 'string') {
        const message = JSON.parse(event.data);
        if (message.type && 'binarySize' in message) {
          // Prepare to receive binary data in the next message
          expectingBinary = true;
          binarySize = message.binarySize;
          messageType = message.type;
        } else {
          // Notify subscribers for non-binary messages
          subscribersRef.current.forEach(({ filter, callback }) => {
            if (filter(message)) {
              callback(message);
            }
          });
        }
      }
    };

    setWs(socket);
  };

  const subscribe = (filter, callback) => {
    const subscriber = { filter, callback };
    subscribersRef.current.push(subscriber);
    // Return an unsubscribe function
    return () => {
      subscribersRef.current = subscribersRef.current.filter(sub => sub !== subscriber);
    };
  };

  // Function to send messages to the server
  const send = (message) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      //console.error('WebSocket is not connected.');
    }
  };

  return (
    <WebSocketContext.Provider value={{ ws, connected, subscribe, send, connect}}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketListener = (subscribe, messageType, callback) => {
  useEffect(() => {
    // Define the message filter based on the messageType parameter
    const messageFilter = (message) => message.type === messageType;
    
    // Subscribe to messages that pass the filter
    const unsubscribe = subscribe(messageFilter, callback);

    // Unsubscribe from messages when the component unmounts
    return () => unsubscribe();
  }, [subscribe, messageType, callback]);
};