

// MyComponent.js
import React, {useState, useEffect} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaintBrush, faEraser, faFont} from '@fortawesome/free-solid-svg-icons';
import Draggable from 'react-draggable';

const ToolBar = ({ windowKey, windowState, 
  toggleVisibility, toggleMinimized,
  handleDragStop, handleFocus,
  handleResize, handleResizeStop })  => {
    // State data
    const [selectedTool, setSelectedTool] = useState('');

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
    return (
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
      </Draggable>
    );
};

export default ToolBar;


  