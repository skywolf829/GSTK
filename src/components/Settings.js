



  

// MyComponent.js
import React, {useState} from 'react';

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
        <div className="submenu">
        {items.map((item, index) => (
            <a key={index} href="#!" onClick={item.callback}>
            {item.name}
            </a>
        ))}
        </div>
    );
    };

    const MenuItem = ({ title, items }) => {
        const [isSubMenuVisible, setIsSubMenuVisible] = useState(false);

        return (
            <div className="menu-item"
                onMouseEnter={() => setIsSubMenuVisible(true)}
                onMouseLeave={() => setIsSubMenuVisible(false)}>
            {title}
            {isSubMenuVisible && <SubMenu items={items} />}
            </div>
        );
    };

    return (
        <div className="settings-container">
        <button className="settings-button" onClick={() => setIsMenuVisible(!isMenuVisible)}>
            ☰ {/* This is a simple representation of a settings icon */}
        </button>
        {isMenuVisible && (
            <div className="menu">
            <MenuItem title="File" items={fileItems} />
            <MenuItem title="Edit" items={editItems} />
            {/* Additional menu items can be added here */}
            </div>
        )}
        </div>
    );    
};

export default SettingsMenu;


  