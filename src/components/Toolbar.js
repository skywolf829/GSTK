

// MyComponent.js
import React, {useState, useEffect} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaintBrush, faEraser, faFont} from '@fortawesome/free-solid-svg-icons';
import Draggable from 'react-draggable';
import { useIconBar } from './IconBarContext';

const ToolBar = ({ windowKey, windowState, 
  toggleVisibility, toggleMinimized,
  handleDragStop, handleFocus,
  handleResize, handleResizeStop, resetScreenPosition })  => {
    // State data
    const [selectedTool, setSelectedTool] = useState('');

    const { registerIcon } = useIconBar();

    // The tools
    const tools = [
        { id: 'brush', icon: faPaintBrush, name: 'Brush' },
        { id: 'eraser', icon: faEraser, name: 'Eraser' },
        { id: 'text', icon: faFont, name: 'Text' },
    ];


    const handleToolClick = (toolId) => {
        setSelectedTool(toolId);
        // You can extend this method to change canvas behavior based on the selected tool
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
  }, [windowState.isVisible, windowState.isMinimized]);
  
    return (
      windowState.isVisible && (
        <Draggable
          position={windowState.position}
          onStop={(e, data) => handleDragStop(windowKey, data)}
          onStart={() => handleFocus(windowKey)}>
        <div className="toolbar" style={{zIndex: windowState.zIndex}}>
          {tools.map((tool) => (
            <div key={tool.id} className={`tool-icon ${selectedTool === tool.id ? 'selected' : ''}`} onClick={() => handleToolClick(tool.id)}>
              <FontAwesomeIcon icon={tool.icon} title={tool.name} />
            </div>
          ))}
        </div>
      </Draggable>)
    );
};

export default ToolBar;


  