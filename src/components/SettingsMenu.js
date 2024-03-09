



  

// MyComponent.js
import React, {useState} from 'react';
import styles from '../css/SettingsButton.module.css'; // Ensure you have the appropriate styles

const SettingsMenu = () => {  

    // State variables
    const [isMenuVisible, setIsMenuVisible] = useState(false);

    // Items in the file selection
    const fileItems = [
        { name: 'New', callback: () => console.log('New File') },
        { name: 'Open', callback: () => console.log('Open File') },
        { name: 'Save', callback: () => console.log('Save File') },
    ];

    // Items in the edit selection
    const editItems = [
        { name: 'Undo', callback: () => console.log('Undo') },
        { name: 'Redo', callback: () => console.log('Redo') },
    ];

    const SubMenu = ({ items }) => {
    return (
        <div className={styles.submenu}>
        {items.map((item, index) => (
            <a 
            key={index} href="#!" onClick={item.callback}>
            {item.name}
            </a>
        ))}
        </div>
    );
    };

    const MenuItem = ({ title, items }) => {
        const [isSubMenuVisible, setIsSubMenuVisible] = useState(false);

        return (
            <div className={styles.menuItem}
                onMouseEnter={() => setIsSubMenuVisible(true)}
                onMouseLeave={() => setIsSubMenuVisible(false)}>
            {title}
            {isSubMenuVisible && <SubMenu items={items} />}
            </div>
        );
    };

    return (
        <div className={styles.settingsContainer}>
        <button className={styles.settingsButton} onClick={() => setIsMenuVisible(!isMenuVisible)}>
            ☰ {/* This is a simple representation of a settings icon */}
        </button>
        {isMenuVisible && (
            <div className={styles.menu}>
            <MenuItem title="File" items={fileItems} />
            <MenuItem title="Edit" items={editItems} />
            {/* Additional menu items can be added here */}
            </div>
        )}
        </div>
    );    
};

export default SettingsMenu;


  