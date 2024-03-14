// DraggableResizableWindow.js
import React from 'react';
import Draggable from 'react-draggable';
import { Resizable, ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css';
import styles from '../css/WindowStyles.module.css'; // Ensure you have the appropriate styles

const DraggableResizableWindow = ({
    windowKey,
    isMinimized,
    position,
    size,
    zIndex,
    title,
    handleDragStop,
    handleFocus,
    handleResize,
    handleResizeStop,
    handleClose,
    toggleMinimized,
    minConstraints,
    barColor = 'rgb(224, 224, 224)',
    children, // The unique content of each window will be passed as children
}) => {

    const handleMinimizeClick = () => {
        // Your minimize logic here
        toggleMinimized(windowKey);
        
        // Remove focus from the button after clicking
        if (document.activeElement instanceof HTMLElement) {
            document.activeElement.blur();
        }
    };

    const resizableProps = isMinimized ? {
        height: size.height, // Minimized height (same as in the hook)
        width: size.width, // Keep the current width
        resizeHandles: ['e', 'w'] // Only allow horizontal resizing
      } : {
        width: size.width,
        height: size.height,
        resizeHandles: ['s', 'w', 'e', 'n', 'sw', 'nw', 'se', 'ne']
      };

    return (
        <Draggable 
            handle=".drag-handle" 
            position={position} 
            onStop={(e, data) => handleDragStop(windowKey, data)}
            onStart={() => handleFocus(windowKey)}>
        <Resizable
            {...resizableProps}
            onResize={(e, data) => {
                handleResize(windowKey, data.size);
            }}
            onResizeStop={(e, data) => handleResizeStop(windowKey, data.size)}
            minConstraints={minConstraints}
        >
            <div className={styles.window} 
                style={{ width: size.width, height: size.height, zIndex }}
                onClick={() => handleFocus(windowKey)}
                >
            <div className={`${styles.windowHeader} drag-handle`}
                style={{backgroundColor: barColor}}
            >
                {title}
                <div>
                    <button onClick={() => handleMinimizeClick(windowKey)} 
                        className={styles.minimizeButton}>-</button>
                    <button onClick={() => handleClose(windowKey)} 
                        className={styles.closeButton}>×</button>
                </div>            
            </div>
            {!isMinimized && children}
            </div>
        </Resizable>
        </Draggable>
    );
};

export default DraggableResizableWindow;