

import React, {useState} from 'react';
import { useWebSocket, useWebSocketListener} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';
import "../css/Trainer.css"

const RenderSettings = ({ bringToFront, onClose }) => {
    
    const title = "Render settings";
    const minConstraints = [340, 192];

    // Input values states
    const [rendererEnabled, setRendererEnabled] = useState(true); 
    const [resolutionScaling, setResolutionScaling] = useState(1.0); 
    const [fov, setFov] = useState(70.0); 
    const [gaussianSize, setGaussianSize] = useState(1.0); 
    const [selectionTransparency, setSelectionTransparency] = useState(0.05); 

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
    const updateRenderSettings = (message) => {
        console.log(message);
        setResolutionScaling(message.data.resolutionScaling);
        setFov(message.data.fov);
        setGaussianSize(message.data.gaussianSize);
        setSelectionTransparency(message.data.selectionTransparency);
    };
    const updateRendererToggled = (message) => {
        console.log(message);
        setRendererEnabled(message.data.rendererEnabled);
    };

    // Use the custom hook to listen for messages of type 'test'
    useWebSocketListener(subscribe, 'renderSettings', updateRenderSettings);
    useWebSocketListener(subscribe, 'renderEnabled', updateRendererToggled);

    const handleClick = () => {
        console.log("Update render settings.");
        const message = {
            type: "renderSettings",
            data: {
                resolutionScaling: resolutionScaling,
                fov: fov,
                gaussianSize: gaussianSize,
                selectionTransparency: selectionTransparency
            }
        };
        send(message);
    };


    const handleRenderToggle = () => {
        console.log("Toggle rendering");
        const message = {
            type: "rendererEnabled",
            data: {
                enabled: rendererEnabled
            }
        };
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
                <div>
                    <div className="info-container">
                        <label>
                            Renderer Enabled:
                        </label>
                        <div style={{alignItems:"center", flexGrow:1}}>
                            <input 
                                type="checkbox" 
                                checked={rendererEnabled}
                                onChange={(e) => {
                                    setRendererEnabled(e.target.checked);
                                    handleRenderToggle(); 
                                }}
                            />
                        </div>
                            
                    </div>
                    <div className="info-container">
                        <label>
                            Resolution Scaling:                        
                        </label>
                        <div style={{alignItems:"center", flexGrow:1}}>
                        <input 
                                type="range" 
                                min="0.0" 
                                max="1.0" 
                                step="0.01" 
                                value={resolutionScaling}
                                onChange={(e) => setResolutionScaling(parseFloat(e.target.value))}
                            />
                        </div>   
                        {resolutionScaling} 
                    </div>
                    <div className="info-container">
                        <label className="item-label">
                            Field of View (FOV):                            
                        </label>
                        <div style={{alignItems:"center", flexGrow:1}}>
                            <input 
                                type="range" 
                                min="30" 
                                max="120" 
                                step="0.5" 
                                value={fov}
                                onChange={(e) => setFov(parseFloat(e.target.value))}
                            />
                        </div>
                        {fov}
                            
                    </div>
                    <div className="info-container">
                        <label>
                            Gaussian Size:
                        </label>
                        <div style={{alignItems:"center", flexGrow:1}}>
                            <input 
                                type="range" 
                                min="0.0" 
                                max="1.0" 
                                step="0.01" 
                                value={gaussianSize}
                                onChange={(e) => setGaussianSize(parseFloat(e.target.value))}
                            />
                        </div>    
                        {gaussianSize}
                    </div>
                    <div className="info-container">
                        <label>
                            Selection Transparency:
                        </label>
                        <div style={{alignItems:"center", flexGrow:1}}>
                            <input 
                                type="range" 
                                min="0.0" 
                                max="1.0" 
                                step="0.01" 
                                value={selectionTransparency}
                                onChange={(e) => setSelectionTransparency(parseFloat(e.target.value))}
                            />
                        </div>
                        {selectionTransparency}
                    </div>
                    <button onClick={handleClick}>Update settings</button>
                </div>
            </div>
        </DraggableResizableWindow>
      );    
};

export default RenderSettings;


  