

// MyComponent.js
import React from 'react';
import { useWebSocket, useWebSocketListener} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';

const ExampleWindow = ({ bringToFront, onClose  }) => {
    
    const title = "Example";
    const minConstraints = [180, 115];

    const {
        isVisible, isMinimized, 
        size, position, zIndex,
        toggleVisibility, toggleMinimized,
        handleDragStop, handleFocus,
        handleResize, handleResizeStop,
      } = useWindowSettings(title, minConstraints, bringToFront);


    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
    

    const sendTestData = () => {
        const message = {
          type: 'customType', // Define the message type or structure as needed
          data: "test",
        };
        send(message); // Use the send function from the context
    };
    
      // Logic to handle the message
    const handleMessage = (message) => {
        console.log(message);
        // ... other actions based on the message
    };

    // Use the custom hook to listen for messages of type 'test'
    useWebSocketListener(subscribe, 'test', handleMessage);

    
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
          {/* Your unique content here */}
          <p style={{ padding: 10 }}>Unique content for MyComponent</p>
          {/* ...other unique content */}
        </DraggableResizableWindow>
      );
    
};

export default ExampleWindow;


  