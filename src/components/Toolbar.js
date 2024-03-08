

// MyComponent.js
import React, {useState, useEffect} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaintBrush, faEraser, faFont} from '@fortawesome/free-solid-svg-icons';
import Draggable from 'react-draggable';

const ToolBar = ({ bringToFront }) => {
    // State data
    const [selectedTool, setSelectedTool] = useState('');

    // Position
    const [position, setPosition] = useState({ x: 100, y: 100 });

    // The tools
    const tools = [
        { id: 'brush', icon: faPaintBrush, name: 'Brush' },
        { id: 'eraser', icon: faEraser, name: 'Eraser' },
        { id: 'text', icon: faFont, name: 'Text' },
    ];

    // z-index
    const [zIndex, setZIndex] = useState(100);

    useEffect(() => {
      // Load the size and position from localStorage when the component mounts
      const savedPosition = JSON.parse(localStorage.getItem('toolsPosition'));
  
      if (savedPosition) {
        setPosition(savedPosition);
      }
    }, []);

    const handleFocus = () => {
      const newZIndex = bringToFront();
      setZIndex(newZIndex);
    };

    const handleDragStop = (e, data) => {
      // Save the new position to localStorage
      const newPosition = { x: data.x, y: data.y };
      localStorage.setItem('toolsPosition', JSON.stringify(newPosition));
      setPosition(newPosition);
    };

    const handleToolClick = (toolId) => {
        setSelectedTool(toolId);
        // You can extend this method to change canvas behavior based on the selected tool
    };
    return (
        <Draggable
          position={position}
          onStop={handleDragStop}
          onStart={handleFocus}>
        <div className="toolbar" style={{zIndex: zIndex}}>
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


  