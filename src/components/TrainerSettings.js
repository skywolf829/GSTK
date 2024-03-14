

import React, {useState, useEffect} from 'react';
import { useWebSocket, useWebSocketListener} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';
import { useIconBar } from './IconBarContext';

const TrainerSettings = ({ windowKey, windowState, 
    toggleVisibility, toggleMinimized,
    handleDragStop, handleFocus,
    handleResize, handleResizeStop, resetScreenPosition}) => {
    const variable_names = [
        "Total iterations",
        "Initial position learning rate",
        "Final position learning rate",
        "Position learning rate delay multiplier",
        "Position learning rate scheduler max steps",
        "Feature learning rate",
        "Opacity learning rate",
        "Scaling learning rate",
        "Rotation learning rate",
        "Percent dense",
        "SSIM loss weight",
        "Densification interval",
        "Opacity reset interval",
        "Densify from iteration",
        "Densify until iteration",
        "Densify gradient threshold"
    ];
    const variable_steps = [
        1,
        0.000000001,
        0.000000001,
        0.000000001,
        1,
        0.000000001,
        0.000000001,
        0.000000001,
        0.000000001,
        0.001,
        0.001,
        1,
        1,
        1,
        1,
        0.0000001,
    ];
    const variable_defaults = [
        30000,
        0.00016,
        0.0000016,
        0.01,
        30000,
        0.0025,
        0.05,
        0.005,
        0.001,
        0.01,
        0.2,
        100,
        300,
        500,
        1500,
        0.0002,
    ];

    // Input values states
    const [floatValues, setFloatValues] = useState(variable_defaults); // Start with two float inputs

    const { registerIcon } = useIconBar();

    const handleChange = (index, value) => {
        const newFloatValues = [...floatValues];
        newFloatValues[index] = value;
        setFloatValues(newFloatValues);
    };

    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
    
      // Logic to handle the message
    const handleMessage = (message) => {
        const newValues = [
            message.data.total_iterations,
            message.data.position_lr_init,
            message.data.position_lr_final,
            message.data.position_lr_delay_mult,
            message.data.position_lr_max_steps,
            message.data.feature_lr,
            message.data.opacity_lr,
            message.data.scaling_lr,
            message.data.rotation_lr,
            message.data.percent_dense,
            message.data.lambda_dssim,
            message.data.densification_interval,
            message.data.opacity_reset_interval,
            message.data.densify_from_iter,
            message.data.densify_until_iter,
            message.data.densify_grad_threshold

        ]
        setFloatValues(newValues);
    };

    // Use the custom hook to listen for messages of type 'test'
    useWebSocketListener(subscribe, 'trainingSettings', handleMessage);

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
        
        const opacity =  windowState.isVisible ? 1.0 : 0.0;
        const backgroundColor =`rgba(200, 200, 200, ${opacity})`
        
        const iconProps = {
            windowKey: windowKey,
            windowState: windowState, 
            toggleWindowVisible: () => {toggleVisibility(windowKey)},
            contextMenuItems: contextMenuItems,
            contextMenuCallbacks: contextMenuCallbacks,
            backgroundColor: backgroundColor
        };
        registerIcon(windowKey, iconProps);
    }, [windowState.isVisible, windowState.isMinimized]);

    const handleClick = () => {
        const data = {
            total_iterations: floatValues[0],
            position_lr_init: floatValues[1],
            position_lr_final: floatValues[2],
            position_lr_delay_mult: floatValues[3],
            position_lr_max_steps: floatValues[4],
            feature_lr: floatValues[5],
            opacity_lr: floatValues[6],
            scaling_lr: floatValues[7],
            rotation_lr: floatValues[8],
            percent_dense: floatValues[9],
            lambda_dssim: floatValues[10],
            densification_interval: floatValues[11],
            opacity_reset_interval: floatValues[12],
            densify_from_iter: floatValues[13],
            densify_until_iter: floatValues[14],
            densify_grad_threshold: floatValues[15]
        }
        const message = {
            type: "updateTrainingSettings",
            data: data
        }
        send(message);
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
        >
            <div style={{padding:"5px"}}>
            {floatValues.map((floatValue, index) => (
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
                        type="number"
                        step={variable_steps[index]}
                        value={floatValue}
                        style={{ 
                            //flexGrow: 1, // Input field takes up remaining space
                            marginLeft: 'auto', // Push input to the right
                            width: "100%"
                        }}                                
                        onChange={(e) => handleChange(index, parseFloat(e.target.value))}
                    />
                </div>
            ))}
            <button onClick={handleClick}>Update</button>
            </div>
        </DraggableResizableWindow>)
      );    
};

export default TrainerSettings;


  