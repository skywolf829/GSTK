

// MyComponent.js
import React, {useRef, useEffect, useState} from 'react';
import { useWebSocket } from '../utils/WebSocketContext';
import 'react-resizable/css/styles.css';

const CanvasComponent = () => {
    const canvasRef = useRef(null);

    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
      
    const handleMouseDown = (event) => {
        var button = "";
        var correctButton = false;
        if (event.button === 0) {
            console.log('Left click');
            button="left";
            correctButton=true;
        } else if (event.button === 2) {
            console.log('Right click');
            button="right";
            event.preventDefault(); // Prevent the context menu from appearing
            correctButton=true;
        }
        if(correctButton){
          send(
            { 
              type: 'mouseDown', 
              data: {
                button: button
              } 
            }
          );
        }
    };

    const handleMouseUp = (event) => {
      var button = "";
      var correctButton = false;
      if (event.button === 0) {
          console.log('Left click release');
          button="left";
          correctButton=true;
      } else if (event.button === 2) {
          console.log('Right click release');
          button="right";
          event.preventDefault(); // Prevent the context menu from appearing
          correctButton=true;
      }
      if(correctButton){
        send(
          { 
            type: 'mouseUp', 
            data: {
              button: button
            } 
          }
        );
      }
    };

    const throttle = (func, limit) => {
      let inThrottle;
      return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
          func.apply(context, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      }
    }

    const handleMouseMove = throttle((event) => {
      // calculate mouse position
      console.log("Mouse move");
      const canvas = canvasRef.current;
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;    // scale mouse coordinates after they have
      const scaleY = canvas.height / rect.height;  // been adjusted to be relative to element
      const x = (event.clientX - rect.left) * scaleX;
      const y = (event.clientY - rect.top) * scaleY;
      const mousePos = { x, y };
      // send mouse position to server
      send({ type: 'mouseMove', data: {position: mousePos } });
    }, 16); // Update every 16ms

    const handleScroll = (event) => {
      // +1 is scroll down, -1 is scroll up
        console.log('Scrolling', event.deltaY/100);
        send({ type: 'mouseScroll', data: {delta: event.deltaY/100 }})
        // Use event.deltaY for scroll direction and amount
    };

    // Set up event listeners after the canvas is rendered
    useEffect(() => {
      const canvas = canvasRef.current;
      if (canvas) {
          canvas.addEventListener('mousedown', handleMouseDown);
          canvas.addEventListener('mouseup', handleMouseUp);
          canvas.addEventListener('mousemove', handleMouseMove);
          canvas.addEventListener('wheel', handleScroll);
          
          // Disable the context menu on right-click
          canvas.oncontextmenu = (e) => e.preventDefault();
      }

      // Clean up the event listeners when the component unmounts
      return () => {
          if (canvas) {
              canvas.removeEventListener('mousedown', handleMouseDown);
              canvas.removeEventListener('mouseup', handleMouseUp);
              canvas.removeEventListener('mousemove', handleMouseMove);
              canvas.removeEventListener('wheel', handleScroll);
          }
      };
    }, []);

    
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
        (message) => message.type === 'render', // This will match the JSON header for image messages
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


  