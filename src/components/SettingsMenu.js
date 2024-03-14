



  

// MyComponent.js
import React, {useState, useEffect} from 'react';
import styles from '../css/SettingsButton.module.css'; // Ensure you have the appropriate styles
import { useModal } from './ModalContext';
import { useWebSocket} from '../utils/WebSocketContext';

const SettingsMenu = () => {  

    // State variables
    const [isMenuVisible, setIsMenuVisible] = useState(false);
    const [filePath, setFilePath] = useState('');
    const [dropDownSelect, setDropDownSelect] = useState("");
    const { openModal, closeModal } = useModal();
    const [availableModels, setAvailableModels] = useState(null);
    const [modalContent, setModalContent] = useState(null); // State to hold modal content
    const [isLoadModalVisible, setLoadModalVisible] = useState(false);
    const [isSaveModalVisible, setSaveModalVisible] = useState(false);

    const { subscribe, send } = useWebSocket();

    useEffect(() => {
        const unsubscribe = subscribe(
          (message) => message.type === 'availableModels', // Adjust this according to your message protocol
          (data) => {
            handleNewModels(data.data.models); // Adjust according to the shape of your response
          }
        );
      
        return () => unsubscribe();
      }, [subscribe]);

    const handleChange = (value) => {
        setFilePath(value);
    };

    const handleNewModels = (newModels) => {
        setAvailableModels(newModels);
    };

    const handleLoadModal = () => {
        setIsMenuVisible(false);
        send({ type: 'requestAvailableModels', data: {} });   
        setLoadModalVisible(true);
    };

    const handleSaveModal = () => {
        setIsMenuVisible(false);
        setSaveModalVisible(true);
    };
      
    const resetModal = () => {
        setLoadModalVisible(false);
        setSaveModalVisible(false);
        setModalContent(null);
        setFilePath('');
        setDropDownSelect('');
        closeModal();
    }

    const loadModel = () => {
        // Do load
        let path = filePath;
        if(dropDownSelect !== ""){
            path = dropDownSelect;
        }
        send({ type: 'loadModel', data: { modelPath: path}});
        resetModal();
    }

    const saveModel = () => {
        // Do save
        send({ type: 'saveModel', data: { modelPath: filePath}});
        resetModal();
    }
    
    // Update modal content whenever availableModels changes
    
    useEffect(() => {
        if (isLoadModalVisible) {
            const content = (
                <div>
                <h3>Load model</h3>
                {availableModels === null ? (
                    <p>Loading models...</p>
                ) : availableModels.length === 0 ? (
                    <p>No models saved</p>
                ) : (
                    <>
                    <select
                        onChange={(e) => setDropDownSelect(e.target.value)}
                        placeholder='Select a model'
                        value={dropDownSelect}
                    >
                        <option value="">Select a model</option>
                        {availableModels.map((model, index) => (
                        <option key={index} value={model}>
                            {model}
                        </option>
                        ))}
                    </select>
                    <br />
                    <input
                        type='text'
                        onChange={(e) => handleChange(e.target.value)}
                        placeholder='enter/path/to/model.ply'
                    />
                    <br />
                    <button onClick={loadModel}>Load</button>
                    <button onClick={resetModal}>Cancel</button>
                    </>
                )}
                </div>
            );
            setModalContent(content);
        }
        else if(isSaveModalVisible){
            
            const content = (
            <div>
              <h3>Save model</h3>
              <input type='text' 
              onChange={(e) => handleChange(e.target.value)} 
              placeholder='Model name'
              />
              <br></br>
              <button onClick={saveModel}>Save</button>
              <button onClick={resetModal}>Cancel</button>
            </div>
          );
          setModalContent(content);
        }
    }, [availableModels, filePath, dropDownSelect, isLoadModalVisible, isSaveModalVisible]);
    
    useEffect(() => {
        if(isSaveModalVisible || isLoadModalVisible){
            if(modalContent){
                openModal(modalContent);
            }
            else{
                closeModal();
            }
        }
    }, [modalContent]);

    // Items in the file selection
    const modelItems = [
        { name: 'Load', callback: () => handleLoadModal() },
        { name: 'Save', callback: () => handleSaveModal() },
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
            {isSubMenuVisible && 
            (<SubMenu items={items} />)}
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
            <MenuItem title="Model" items={modelItems} />
            <MenuItem title="Edit" items={editItems} />
            {/* Additional menu items can be added here */}
            </div>
        )}
        </div>
    );    
};

export default SettingsMenu;


  