

import React, {useState, useEffect} from 'react';
import { useWebSocket, useWebSocketListener} from './WebSocketContext';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';
import "../css/Trainer.css"
import { useIconBar } from './IconBarContext';

const Trainer = ({ windowKey, windowState, 
  toggleVisibility, toggleMinimized,
  handleDragStop, handleFocus,
  handleResize, handleResizeStop,
  resetScreenPosition, setTitle }) => {

    // Input values states
    const [training, setTraining] = useState(false);
    const [iterationData, setIterationData] = useState([0, 30000]); 
    const [lossData, setLossData] = useState(0.0); 
    const [trainStepTime, setTrainStepTime] = useState(0.0); 
    const { registerIcon } = useIconBar();

    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
    const { connected } = useWebSocket();

    const getStateColorRGBA = () => {
      const opacity =  windowState.isVisible ? 1.0 : 0.3;
      return training && connected ? `rgba(0, 122, 31, ${opacity})` : `rgba(255, 150, 50, ${opacity})`;
    };
    const getStateColorRGB = () => {
      return training && connected ? `rgba(0, 122, 31)` : `rgba(255, 150, 50)`;
    };

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
      
      
      const iconProps = {
          windowKey: windowKey,
          windowState: windowState, 
          toggleWindowVisible: () => {toggleVisibility(windowKey)},
          contextMenuItems: contextMenuItems,
          contextMenuCallbacks: contextMenuCallbacks,
          backgroundColor: getStateColorRGBA()
      };
      registerIcon(windowKey, iconProps);
  }, [windowState.isVisible, windowState.isMinimized, connected]);

    const updateTrainingInfo = (newIterationData, 
        newLossData, newTrainStepTime) => {
        setIterationData(newIterationData); 
        setLossData(newLossData); 
        setTrainStepTime(newTrainStepTime); 
        updateFPS(newTrainStepTime);
        
    };
    const updateFPS = (stepTime) => {
      if(training){
        setTitle(windowKey, 
            <span>Trainer 
                <span>{(1000.0/stepTime).toFixed(2)} FPS
                </span>
            </span>);
      }
      else{
        setTitle(windowKey, 
          <span>Trainer</span>);
      }
      
  };
      // Logic to handle the message
    const handleStateMessage = (message) => {
        updateTrainingInfo(
            [message.data.iteration, message.data.totalIterations], 
            message.data.loss, message.data.stepTime);
        setTraining(message.data.training);
    };

      // Logic to handle the message
      const handleIsTraining = (message) => {
        setTraining(message.data.training);
    };

    // Use the custom hook to listen for messages of type 'test'
    useWebSocketListener(subscribe, 'trainingState', handleStateMessage);
    useWebSocketListener(subscribe, 'isTraining', handleIsTraining);

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
          barColor={getStateColorRGB()}
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
        </DraggableResizableWindow>)
      );    
};

export default Trainer;


  