import React, {useState, useEffect} from 'react';
import { useIconBar } from './IconBarContext';
import SettingsMenu from './SettingsMenu';
import styles from '../css/IconBar.module.css'; // Make sure the path to your CSS module is correct
import Icon from './Icon';
import ContextMenu from './ContextMenu'; // Assuming you have this component

const IconBar = () => {
  const { icons } = useIconBar();

  const [contextMenu, setContextMenu] = useState(
    { 
      visible: false, 
      x: 0, 
      y: 0, 
      windowKey: null,
      items: [],
      callbacks: []
    });

  const handleRightClick = (event, key, contextMenuItems, contextMenuCallbacks) => {
    event.preventDefault();
    setContextMenu({
      visible: true,
      x: 100 + event.clientX - window.innerWidth / 2.0,
      y: event.clientY+20,
      windowKey: key,
      items: contextMenuItems,
      callbacks: contextMenuCallbacks
    });
  };

  const closeContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0, windowKey: null });
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
  
  return (
    <div>
      <div className={styles.iconBar}>
        {Object.keys(icons).map(key => (
          <div key={key}>
              < Icon {...icons[key]} handleRightClick={handleRightClick} />
          </div>
        ))}
      
        {contextMenu.visible && (
              <ContextMenu 
              x={contextMenu.x} 
              y={contextMenu.y} 
              items={contextMenu.items}
              callbacks={contextMenu.callbacks}
              />
        )}
        <SettingsMenu />
      </div>
    </div>
  );
};

export default IconBar;