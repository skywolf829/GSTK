

import React, {useState} from 'react';
import { useWebSocket, useWebSocketListener} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';

const DatasetSetup = ({ bringToFront, onClose }) => {
    const variable_names = [
        "Dataset path",
        "Data device",
        "COLMAP executable",
        "ImageMagick executable"
    ];
    const variable_defaults = [
        "",
        "cuda",
        "",
        ""
    ];

    const title = "Dataset Setup";
    const minConstraints = [270, 165];

    // Input values states
    const [values, setValues] = useState(variable_defaults); 
    const [datasetLoaded, setDatasetLoaded] = useState(false);

    const handleChange = (index, value) => {
        const newValues = [...values];
        newValues[index] = value;
        setValues(newValues);
    };

    const {
        isVisible, isMinimized, 
        size, position, zIndex,
        toggleVisibility, toggleMinimized,
        handleDragStop, handleFocus,
        handleResize, handleResizeStop,
      } = useWindowSettings(title, minConstraints, bringToFront);


    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
    
    // Logic to handle the message
    const handleDatasetSettingsMessage = (message) => {
        setValues([message.dataset_path, 
            message.dataset_device, 
            message.colmap_path, 
            message.imagemagick_path]);
    };

    const handleDatasetLoaded = (message) => {

        setDatasetLoaded(message.data.loaded);
    }
    // Use the custom hook to listen for messages of type 'test'
    useWebSocketListener(subscribe, 'datasetSettings', handleDatasetSettingsMessage);
    useWebSocketListener(subscribe, 'datasetLoaded', handleDatasetLoaded);

    const handleInitializeClick = () => {
        
        const message = {
            type: 'datasetInitialize', // Define the message type or structure as needed
            data: {
                "dataset_path": values[0],
                "data_device": values[1],
                "colmap_path": values[2],
                "imagemagick_path": values[3]
            },
          };
          send(message); // Use the send function from the context
    };
    const handleLoadPointsClick = () => {
        console.log("Load points clicked.");
        const message = {
            type: 'initFromPCD', // Define the message type or structure as needed
            data: {}
        };
        send(message); // Use the send function from the context
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
            <div style={{padding:"5px"}}>
            {values.map((value, index) => (
                <div key={index} style={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    marginBottom: '5px', 
                    width: '100%' 
                    }}>
                    <label style={{
                        marginRight: '10px', 
                        flexShrink: 0 // Prevent the label from shrinking
                        }}>{variable_names[index]}: </label>
                    <input
                        type="text"
                        value={values[index]}
                        style={{ 
                            //flexGrow: 1, // Input field takes up remaining space
                            marginLeft: 'auto', // Push input to the right
                            width: "100%"
                        }}                                
                        onChange={(e) => handleChange(index, e.target.value)}
                    />
                </div>
            ))}
                <div>
                    <button onClick={handleInitializeClick}>Load dataset</button>
                    <button onClick={handleLoadPointsClick}>Load point cloud</button>
                </div>
            </div>
        </DraggableResizableWindow>
      );    
};

export default DatasetSetup;


  