

import React, {useState, useEffect} from 'react';
import { useWebSocket, useWebSocketListener} from '../utils/WebSocketContext';
import useWindowSettings from '../utils/useWindowSettings';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';
import "../css/Trainer.css"
import { useIconBar } from './IconBarContext';

const RenderSettings = ({ windowKey, windowState, 
    toggleVisibility, toggleMinimized,
    handleDragStop, handleFocus,
    handleResize, handleResizeStop ,
    resetScreenPosition, setTitle})  => {
    
    // Input values states
    const [rendererEnabled, setRendererEnabled] = useState(true); 
    const [resolutionScaling, setResolutionScaling] = useState(1.0); 
    const [fov, setFov] = useState(70.0); 
    const [gaussianSize, setGaussianSize] = useState(1.0); 
    const [jpegQuality, setJpegQuality] = useState(85); 
    const [selectionTransparency, setSelectionTransparency] = useState(0.05); 
    const { registerIcon } = useIconBar();

    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
    
      // Logic to handle the message
    const updateRenderSettings = (message) => {
        setResolutionScaling(message.data.resolutionScaling);
        setFov(message.data.fov);
        setGaussianSize(message.data.gaussianSize);
        setSelectionTransparency(message.data.selectionTransparency);
        setJpegQuality(message.data.jpegQuality);
    };
    const updateRendererToggled = (message) => {
        setRendererEnabled(message.data.rendererEnabled);
    };
    const updateFPS = (message) => {
        setTitle(windowKey, 
            <span>Render Settings
                <span>{message.data.fps.toFixed(2)} FPS
                </span>
            </span>);
        //setTooltip(windowKey, `Render settings\nFPS: ${message.data.fps.toFixed(2)}`);
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
    }, [windowState.isVisible, windowState.isMinimized, windowState.tooltip]);

    // Use the custom hook to listen for messages of type 'test'
    useWebSocketListener(subscribe, 'renderSettings', updateRenderSettings);
    useWebSocketListener(subscribe, 'renderEnabled', updateRendererToggled);
    useWebSocketListener(subscribe, 'rendererFPS', updateFPS);

    const handleClick = () => {
        const message = {
            type: "updateRendererSettings",
            data: {
                resolution_scaling: resolutionScaling,
                fov: fov,
                gaussian_size: gaussianSize,
                selection_transparency: selectionTransparency,
                jpeg_quality: jpegQuality
            }
        };
        send(message);
    };


    const handleRenderToggle = (enabled) => {
        const message = {
            type: "updateRendererEnabled",
            data: {
                enabled: enabled
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
                                    handleRenderToggle(e.target.checked); 
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
                    <div className="info-container">
                        <label>
                            JPEG quality:
                        </label>
                        <div style={{alignItems:"center", flexGrow:1}}>
                            <input 
                                type="range" 
                                min="1" 
                                max="100" 
                                step="1" 
                                value={jpegQuality}
                                onChange={(e) => setJpegQuality(parseFloat(e.target.value))}
                            />
                        </div>
                        {jpegQuality}
                    </div>
                    <button onClick={handleClick}>Update settings</button>
                </div>
            </div>
        </DraggableResizableWindow>)
      );    
};

export default RenderSettings;


  