

// MyComponent.js
import React, {useRef, useEffect, useState} from 'react';
import { useWebSocket } from './WebSocketContext';
import 'react-resizable/css/styles.css';

const CanvasComponent = () => {
    const canvasRef = useRef(null);

    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
    

    const sendTestData = () => {
        const message = {
          type: 'customType', // Define the message type or structure as needed
          data: "test",
        };
        send(message); // Use the send function from the context
      };
      useEffect(() => {
        // Setup canvas
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        // Clear canvas for simplicity
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.fillStyle = "#fff0f0"; // Replace with any color you like
        context.fillRect(0, 0, canvas.width, canvas.height);
      }, []);

      useEffect(() => {
        const unsubscribe = subscribe(
          (message) => message.type === 'image', // This will match the JSON header for image messages
          async (data) => {
            if (data instanceof Blob) {
              // Handle the binary image data
              const imageBitmap = await createImageBitmap(data);
              const canvas = canvasRef.current;
              const ctx = canvas.getContext('2d');
              if (canvas && ctx && imageBitmap) {
                canvas.width = imageBitmap.width;
                canvas.height = imageBitmap.height;
                ctx.drawImage(imageBitmap, 0, 0);
                console.log("Update image");
              }
            }
          }
        );
    
        return () => unsubscribe(); // Unsubscribe when the component unmounts
      }, [subscribe]);

    return (
        <div className="canvas-container">
          <canvas ref={canvasRef}  />
        </div>
    );
    
};

export default CanvasComponent;


  