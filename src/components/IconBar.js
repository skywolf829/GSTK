// IconBar.js
import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import styles from '../css/IconBar.module.css'; // Make sure the path to your CSS module is correct
import { windowsConfig } from '../utils/windowsConfig';
import SettingsMenu from './SettingsMenu';
import { useWebSocket } from '../utils/WebSocketContext';
import ContextMenu from './ContextMenu'; // Assuming you have this component

const IconBar = ({ windowStates, toggleWindow, resetWindowPosition, minimizeWindow, closeWindow }) => {
  const { connected } = useWebSocket(); // Access the connected state from the context
  const [contextMenu, setContextMenu] = useState(null);

  const handleRightClick = (e, key) => {
    e.preventDefault();
    setContextMenu({
      x: 100 + e.clientX - window.innerWidth / 2.0,
      y: e.clientY,
      key: key
    });
  };


  const handleOptionClick = (option, key) => {
    if (!contextMenu) return;
    
    if (option === 'reset') {
      resetWindowPosition(key);
    } else if (option === 'minimize') {
      minimizeWindow(key);
    } else if (option === 'close') {
      closeWindow(key);
    }
    setContextMenu(null); // Close context menu after action
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
            className={`${styles.icon} ${windowStates[key] ? styles.active : ''} ${isServerIcon ? iconStatusClass : ''}`} 
            onClick={() => toggleWindow(key)}
            onContextMenu={(e) => handleRightClick(e, key)}
            >
              <FontAwesomeIcon icon={icon} />
              <span className={styles.tooltip}>{tooltip}</span>
            </div>
          );
          })}
        <SettingsMenu />
      </div>
    </div>
  );
};

export default IconBar;