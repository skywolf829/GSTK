// IconBar.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import styles from '../css/IconBar.module.css'; // Make sure the path to your CSS module is correct
import { windowsConfig } from '../utils/windowsConfig';
import SettingsMenu from './SettingsMenu';
import { useWebSocket } from '../utils/WebSocketContext';

const IconBar = ({ windowStates, toggleWindow }) => {
  const { connected } = useWebSocket(); // Access the connected state from the context

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
            <div key={key} className={`${styles.icon} ${windowStates[key] ? styles.active : ''} ${isServerIcon ? iconStatusClass : ''}`} onClick={() => toggleWindow(key)}>
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