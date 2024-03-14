// WebSocketContext.js
import React, { createContext, useContext, 
  useState, useRef, useEffect } from 'react';
import { useModal } from '../components/ModalContext';

const WebSocketContext = createContext(null);

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false); // State to keep track of connection status
  const subscribersRef = useRef([]);
  const { openModal, closeModal } = useModal();
  const [dataReceived, setDataReceived] = useState(0);
  let runningDataReceived = 0;
  const [dataSent, setDataSent] = useState(0);
  let runningDataSent = 0;

  let expectingBinary = false;
  let binarySize = 0;
  let messageType = '';

  const connect = (serverIp, serverPort) => {
    if (ws != null) {
      ws.close(); // Ensure any existing connection is closed
    }
    // Can only support non-encrypted since I dont have SSL
    const socket_type = 'ws'; //window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${socket_type}://${serverIp}:${serverPort}`);
    socket.binaryType = 'blob'; // Ensure binary messages are received as Blob objects

    socket.addEventListener('open', function (event) {
      console.log('Connected to ' + serverIp + ":"+ serverPort);
      setConnected(true); // Set connected state to true when the socket opens
    });

    // Your existing socket.onmessage and other event listeners here...
    
    socket.onclose = () => {
      console.log('WebSocket Disconnected');
      setConnected(false); // Set connected state to false when the socket closes
      setWs(null); // Reset the WebSocket instance in state
      closeModal();
    };

    socket.onmessage = async (event) => {
      if (expectingBinary && event.data instanceof Blob) {
        const blob = event.data;
        const dataSize = blob.size;
        runningDataReceived += dataSize;
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
        const dataSize = new TextEncoder().encode(event.data).length; // Size in bytes
        runningDataReceived += dataSize;
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

  const disconnect = () => {
    if(ws){
      ws.close();
    }
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
    if(ws){
      if (ws.readyState === WebSocket.OPEN) {
        const m = JSON.stringify(message);
        //console.log("Sending: " + m)
        const dataSize = new TextEncoder().encode(m).length; // Size in bytes
        runningDataSent += dataSize;
        ws.send(m);
      } 
      else{
        //console.log('WebSocket not ready: ' + ws.readyState);
      }
    }
    else {
      //console.error('WebSocket not initialized.');
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      const kbps_received = (runningDataReceived / 1024) ; // Convert bytes to kilobytes and divide by time in seconds
      const kbps_sent = (runningDataSent / 1024); // Convert bytes to kilobytes and divide by time in seconds
      setDataReceived(kbps_received);
      setDataSent(kbps_sent);
      runningDataReceived = 0;
      runningDataSent = 0;
    }, 1000); // Update every second

    return () => clearInterval(interval); // Cleanup the interval on unmount
  }, []);

  return (
    <WebSocketContext.Provider value={{ ws, connected, subscribe, send, connect, disconnect, dataSent, dataReceived}}>
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