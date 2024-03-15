

// MyComponent.js
import React, {useState, useEffect} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaintBrush, faEraser, faFont, faCircleMinus, faCirclePlus} from '@fortawesome/free-solid-svg-icons';
import Draggable from 'react-draggable';
import { useIconBar } from './IconBarContext';
import { useWebSocket, useWebSocketListener} from './WebSocketContext';
import { toolsConfig } from '../toolsConfig';
import AddPointsTool from './EditTools/AddPointsTool';

const ToolBar = ({ windowKey, windowState, 
  toggleVisibility, toggleMinimized,
  handleDragStop, handleFocus,
  resetScreenPosition })  => {
    // State data
    const [editorEnabled, setEditorEnabled] = useState(false);
    const [selectedTool, setSelectedTool] = useState('');
    const { subscribe, send, connected } = useWebSocket();
    const { registerIcon } = useIconBar();

    // Edit window data
    const [editWindowTitle, setEditWindowTitle] = useState("");
    const [editWindowPosition, setEditWindowPosition] = useState([0,0])
    const [editWindowSize, setEditWindowSize] = useState([0,0])
    const [editWindowContent, setEditWindowContent] = useState(null);


    const handleToolClick = (toolId) => {
      const message = {
        type: "editorButtonClick",
        data: {
          button_clicked: toolId
        }
      };
      send(message);
    };

    const handleEditorState = (message) => {
      console.log("Editor state", message)
      setEditorEnabled(message.data.editorEnabled);
      setSelectedTool(message.data.editType);
    };
    useWebSocketListener(subscribe, 'editorState', handleEditorState);
    
    useEffect(() => {
      const message = {
        type: "editorButtonClick",
        data: {
          button_clicked: ''
        }
      };
      send(message);
    }, [connected]);
    
    useEffect(() => {
      
    }, [selectedTool]);


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
            onStart={() => handleFocus(windowKey)}
            handle=".drag-handle" 
            >
          <div className="toolbar-container" style={{zIndex: windowState.zIndex}}>
            <div className="toolbar drag-handle">
              {toolsConfig.map((tool) => (
                  <div key={tool.key} className={`tool-icon ${selectedTool === tool.key ? 'selected' : ''}`} onClick={() => handleToolClick(tool.key)}>
                    <FontAwesomeIcon icon={tool.icon} title={tool.tooltip} />
                  </div>
              ))}
            </div >
            {editorEnabled && (
              <div className='toolbar-window'>
                {React.createElement(
                  toolsConfig.find(tool => tool.key === selectedTool)?.component || 'div',
                  {
                    // Pass props here                    
                  }
                )}
              </div>
              )
            }
          </div>
        </Draggable>            
      )
      
    );
};

export default ToolBar;


  