

import React, {useState} from 'react';
import { useWebSocket, useWebSocketListener} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';
import "../css/Trainer.css"

const Trainer = ({ windowKey, windowState, 
  toggleVisibility, toggleMinimized,
  handleDragStop, handleFocus,
  handleResize, handleResizeStop }) => {

    // Input values states
    const [training, setTraining] = useState(false);
    const [iterationData, setIterationData] = useState([0, 30000]); 
    const [lossData, setLossData] = useState(0.0); 
    const [trainStepTime, setTrainStepTime] = useState(0.0); 

    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();

    const updateTrainingInfo = (newTraining, newIterationData, 
        newLossData, newTrainStepTime) => {
        setTraining(newTraining);
        setIterationData(newIterationData); 
        setLossData(newLossData); 
        setTrainStepTime(newTrainStepTime); 
    };

      // Logic to handle the message
    const handleMessage = (message) => {
        updateTrainingInfo(message.data.training, 
            [message.data.iteration, message.data.totalIterations], 
            message.data.loss, message.data.stepTime);
    };

    // Use the custom hook to listen for messages of type 'test'
    useWebSocketListener(subscribe, 'trainingState', handleMessage);

    const handleTrainClick = () => {
        const message = {
            type: 'toggleTraining',
            data: {
              "toggleTrain": true
            }
          };
        send(message);
    };

    return (
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
            <div style={{ padding: "5px" }}>
                <div className="info-container">
                    <div className="item-label">Current iteration:</div>
                    <div className="item-value">{iterationData[0]} / {iterationData[1]}</div>
                </div>
                <div className="info-container">
                    <div className="item-label">Current loss:</div>
                    <div className="item-value">{lossData.toFixed(4)}</div>
                </div>
                <div className="info-container">
                    <div className="item-label">Time per training step:</div>
                    <div className="item-value">{trainStepTime.toFixed(2)}ms</div>
                </div>
                <button onClick={handleTrainClick}>
                    {training ? "Pause training":"Start training"}
                </button>
            </div>
        </DraggableResizableWindow>
      );    
};

export default Trainer;


  