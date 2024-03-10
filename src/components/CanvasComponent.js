

// MyComponent.js
import React, {useRef, useEffect, useState} from 'react';
import { useWebSocket, useWebSocketListener} from '../utils/WebSocketContext';
import 'react-resizable/css/styles.css';

const CanvasComponent = () => {
    const canvasRef = useRef(null);

    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
      

    // Set up event listeners after the canvas is rendered
    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const handleMouseDown = (event) => {
          var button = "";
          var correctButton = false;
          if (event.button === 0) {
              button="left";
              correctButton=true;
          } else if (event.button === 2) {
              button="right";
              event.preventDefault(); // Prevent the context menu from appearing
              correctButton=true;
          }
          if(correctButton){
            const message ={ 
                type: 'mouseDown', 
                data: {
                  button: button
                } 
              };
            send(message);
          }
      };

      const handleMouseUp = (event) => {
        var button = "";
        var correctButton = false;
        if (event.button === 0) {
            button="left";
            correctButton=true;
        } else if (event.button === 2) {
            button="right";
            event.preventDefault(); // Prevent the context menu from appearing
            correctButton=true;
        }
        if(correctButton){
          const message ={ 
            type: 'mouseUp', 
            data: {
              button: button
            } 
          };
          send(message);
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
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;    // scale mouse coordinates after they have
        const scaleY = canvas.height / rect.height;  // been adjusted to be relative to element
        const x = (event.clientX - rect.left) * scaleX;
        const y = (event.clientY - rect.top) * scaleY;
        const mousePos = { x, y };
        // send mouse position to server
        const message ={ 
          type: 'mouseMove', 
          data: {
            position: mousePos
          } 
        };
        send(message);
      }, 16); // Update every 16ms

      const handleScroll = (event) => {
        // +1 is scroll down, -1 is scroll up
          const message ={ 
            type: 'mouseScroll', 
            data: {
              delta: event.deltaY/100
            } 
          };
          send(message);
          // Use event.deltaY for scroll direction and amount
      };
      
      canvas.addEventListener('mousedown', handleMouseDown);
      canvas.addEventListener('mouseup', handleMouseUp);
      canvas.addEventListener('mousemove', handleMouseMove);
      canvas.addEventListener('wheel', handleScroll);
      
      // Disable the context menu on right-click
      canvas.oncontextmenu = (e) => e.preventDefault();
      

      // Clean up the event listeners when the component unmounts
      return () => {
          canvas.removeEventListener('mousedown', handleMouseDown);
          canvas.removeEventListener('mouseup', handleMouseUp);
          canvas.removeEventListener('mousemove', handleMouseMove);
          canvas.removeEventListener('wheel', handleScroll);
      };
    }, [send]);

    
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
            }
          }
        }
      );
  
      return () => unsubscribe(); // Unsubscribe when the component unmounts
    }, [subscribe]);

    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;
    
      let timeoutId = null;
      let pendingResize = false;
    
      const sendResizeMessage = (width, height) => {
        // Clear any pending timeout to avoid sending an outdated size
        if (timeoutId !== null) {
          clearTimeout(timeoutId);
          timeoutId = null;
        }
        send({ 
          type: 'updateResolution', 
          data: { 
            width: width, 
            height:height 
          } 
        });
        pendingResize = false;
      };
    
      const handleResize = (entries) => {
        for (let entry of entries) {
          const { width, height } = entry.contentRect;
          sendResizeMessage(width, height);
        }
      };
    
      const resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(canvas);
    
      // Clean up
      return () => {
        resizeObserver.unobserve(canvas);
        if (timeoutId !== null) {
          clearTimeout(timeoutId);
        }
      };
    }, [send]); // Ensure `send` is included in dependency array if it's not defined inside the effect

    return (
        <div className="canvas-container">
          <canvas ref={canvasRef}  />
        </div>
    );
    
};

export default CanvasComponent;


  