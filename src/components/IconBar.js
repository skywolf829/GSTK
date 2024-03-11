// IconBar.js
import React, { useState, useEffect} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import styles from '../css/IconBar.module.css'; // Make sure the path to your CSS module is correct
import { windowsConfig } from '../utils/windowsConfig';
import SettingsMenu from './SettingsMenu';
import { useWebSocket } from '../utils/WebSocketContext';
import ContextMenu from './ContextMenu'; // Assuming you have this component

const IconBar = ({ windowVisibleStates, manageWindow }) => {
  const { connected } = useWebSocket(); // Access the connected state from the context
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, windowKey: null });

  const handleRightClick = (event, key) => {
    event.preventDefault();
    setContextMenu({
      visible: true,
      x: 100 + event.clientX - window.innerWidth / 2.0,
      y: event.clientY+20,
      windowKey: key
    });
  };

  // Set up global click listener to close context menu when clicking outside
  useEffect(() => {
    const handleGlobalClick = (e) => {
      if (contextMenu.visible) {
        closeContextMenu();
      }
    };

    // Attach the event listener to document
    document.addEventListener('click', handleGlobalClick);  


    // Cleanup the event listener on component unmount
    return () => {
      document.removeEventListener('click', handleGlobalClick);
    };
  }, [contextMenu.visible]);

  const handleOptionClick = (option, key) => {
    if (!contextMenu) return;
    
    if (option === 'reset') {
      manageWindow("resetPosition", key);
    } else if (option === 'minimize') {
      manageWindow("toggleMinimize", key);
    } else if (option === 'close') {
      manageWindow("toggleVisible", key);
    }
    setContextMenu({ visible: false, x: 0, y: 0, windowKey: null });
  };

  // Close context menu when clicking elsewhere
  const closeContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0, windowKey: null });
  };
  
  return (
    <div>
      <div className={styles.iconBar}>
        {windowsConfig.map(({ key, icon, tooltip }) => {
          // Determine if the icon is for the server connection
          const isServerIcon = key === 'serverConnection';
          const iconStatusClass = connected
            ? styles.serverConnected
            : styles.serverDisconnected;
          return (          
            <div key={key} 
            className={`${styles.icon} ${windowVisibleStates[key] ? styles.active : ''} ${isServerIcon ? iconStatusClass : ''}`} 
            onClick={() => manageWindow("toggleVisible", key)}
            onContextMenu={(e) => handleRightClick(e, key)}
            >
              <FontAwesomeIcon icon={icon} />
              <span className={styles.tooltip}>{tooltip}</span>
            </div>
          );
          })}
        <SettingsMenu />

        {contextMenu.visible && (
        <ContextMenu 
          x={contextMenu.x} 
          y={contextMenu.y} 
          onClose={() => handleOptionClick('close', contextMenu.windowKey)}
          onMinimize={() => handleOptionClick('minimize', contextMenu.windowKey)}
          onResetPosition={() => handleOptionClick('reset', contextMenu.windowKey)}
          currentlyOpen={windowVisibleStates[contextMenu.windowKey]}
        />
      )}
      </div>
    </div>
  );
};

export default IconBar;