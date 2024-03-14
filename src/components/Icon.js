import React, { useState, useEffect} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import styles from '../css/IconBar.module.css'; // Make sure the path to your CSS module is correct

const Icon = ({ windowKey,
    windowState, 
    toggleWindowVisible,
    contextMenuItems,
    contextMenuCallbacks,
    handleRightClick,
    backgroundColor = `rgba(255, 255, 255, 1.0)`
    }) => {
        
  
  return (
    <div>
        <div 
        key={windowKey} 
        className={`${styles.icon}`} 
        onClick={() => toggleWindowVisible(windowKey)}
        onContextMenu={(e) => handleRightClick(e, windowKey, contextMenuItems, contextMenuCallbacks)}
        style={{backgroundColor: backgroundColor}}      
        >
            <FontAwesomeIcon icon={windowState.icon} />
            <span className={styles.tooltip}>{windowState.tooltip}</span>
        </div>
      </div>
  );
};

export default Icon;