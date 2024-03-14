// IconBar.js
import React, { useState, useEffect} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import styles from '../css/IconBar.module.css'; // Make sure the path to your CSS module is correct
import { windowsConfig } from '../utils/windowsConfig';
import SettingsMenu from './SettingsMenu';
import { useWebSocket } from '../utils/WebSocketContext';
import ContextMenu from './ContextMenu'; // Assuming you have this component

const IconBar = ({ windows, toggleWindowVisible, toggleWindowMinimized, setWindowPosition, handleFocus }) => {
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
      const midscreen = {x:window.innerWidth / 2.0 - windows[key].size.width / 2.0, 
      y:window.innerHeight / 2.0 - windows[key].size.height / 2.0};
      setWindowPosition(key, midscreen);
      handleFocus(key);
    } else if (option === 'minimize') {
      toggleWindowMinimized(key);
    } else if (option === 'close') {
      toggleWindowVisible(key);
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
            className={`${styles.icon} ${windows[key].isVisible ? styles.active : ''} ${isServerIcon ? iconStatusClass : ''}`} 
            onClick={() => toggleWindowVisible(key)}
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
          currentlyOpen={windows[contextMenu.windowKey].isVisible}
          currentlyMinimized={windows[contextMenu.windowKey].isMinimized}
        />
      )}
      </div>
    </div>
  );
};

export default IconBar;