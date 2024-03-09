

import React, {useState} from 'react';
import { useWebSocket, useWebSocketListener} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';

const TrainerSettings = ({ bringToFront, onClose }) => {
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

    const title = "Trainer Settings";
    const minConstraints = [370, 490];

    // Input values states
    const [floatValues, setFloatValues] = useState(variable_defaults); // Start with two float inputs

    const handleChange = (index, value) => {
        const newFloatValues = [...floatValues];
        newFloatValues[index] = value;
        setFloatValues(newFloatValues);
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
    const handleMessage = (message) => {
        console.log(message);
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

    const handleClick = () => {
        console.log("Update trainer settings.");
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
            type: "trainingSettings",
            data: data
        }
        send(message);
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
        </DraggableResizableWindow>
      );    
};

export default TrainerSettings;


  