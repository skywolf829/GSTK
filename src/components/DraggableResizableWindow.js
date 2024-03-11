// DraggableResizableWindow.js
import React from 'react';
import Draggable from 'react-draggable';
import { Resizable } from 'react-resizable';
import 'react-resizable/css/styles.css';
import styles from '../css/WindowStyles.module.css'; // Ensure you have the appropriate styles
import HEADER_HEIGHT from '../utils/useWindowSettings'

const DraggableResizableWindow = ({
  isMinimized,
  position,
  size,
  zIndex,
  title,
  onDragStop,
  onFocus,
  onResize,
  onResizeStop,
  onClose,
  toggleMinimized,
  minConstraints,
  children, // The unique content of each window will be passed as children
}) => {
    //if (!isVisible) {
    //    return null;
    //}

    const handleMinimizeClick = () => {
        // Your minimize logic here
        toggleMinimized();
        
        // Remove focus from the button after clicking
        if (document.activeElement instanceof HTMLElement) {
            document.activeElement.blur();
        }
    };

    const resizableProps = isMinimized ? {
        height: HEADER_HEIGHT, // Minimized height (same as in the hook)
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
            onStop={onDragStop} 
            onStart={onFocus}>
        <Resizable
            {...resizableProps}
            onResize={onResize}
            onResizeStop={onResizeStop}
            minConstraints={minConstraints}
        >
            <div className={styles.window} 
                style={{ width: size.width, height: size.height, zIndex }}
                onClick={onFocus}>
            <div className={`${styles.windowHeader} drag-handle`}>
                <span>{title}</span>
                <div>
                    <button onClick={handleMinimizeClick} className={styles.minimizeButton}>-</button>
                    <button onClick={onClose} className={styles.closeButton}>×</button>
                </div>            
            </div>
            {!isMinimized && children}
            </div>
        </Resizable>
        </Draggable>
    );
};

export default DraggableResizableWindow;