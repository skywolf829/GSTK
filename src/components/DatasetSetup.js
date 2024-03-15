

import React, {useState, useEffect} from 'react';
import { useWebSocket, useWebSocketListener} from './WebSocketContext';
import 'react-resizable/css/styles.css';
import DraggableResizableWindow from './DraggableResizableWindow';
import { useModal } from './ModalContext';
import { useIconBar } from './IconBarContext';

const DatasetSetup = ({ windowKey, windowState, 
    toggleVisibility, toggleMinimized,
    handleDragStop, handleFocus,
    handleResize, handleResizeStop,
    resetScreenPosition }) => {

    const { openModal, closeModal } = useModal();
    const { registerIcon } = useIconBar();
    const { connected } = useWebSocket();

    const variable_names = [
        "Data device",
        "COLMAP executable",
        "ImageMagick executable"
    ];
    const variable_defaults = [
        "cuda",
        "",
        ""
    ];

    // Input values states
    const [values, setValues] = useState(variable_defaults); 
    const [datasetPath, setDatasetPath] = useState(""); 
    const [datasetLoaded, setDatasetLoaded] = useState(false);
    const [datasetLoading, setDatasetLoading] = useState(false);
    const [availableDatasets, setAvailableDatasets] = useState([]);
    const [manualEntry, setManualEntry] = useState(true); // New state for manual entry selection

    const getStateColorRGBA = () => {
        const opacity =  windowState.isVisible ? 1.0 : 0.3;
        return datasetLoaded && connected ? `rgba(0, 122, 31, ${opacity})` : 
            datasetLoading && connected ? `rgba(255, 150, 50, ${opacity})` : `rgba(255, 100, 100, ${opacity})`;
    };

    const getStateColorRGB = () => {
        return datasetLoaded && connected ? `rgb(0, 122, 31)` : 
            datasetLoading && connected ? `rgb(255, 150, 50})` : `rgb(255, 100, 100)`;
    };

    useEffect(() => {
        // Define the props for the Icon component
        const contextMenuItems = [
            "Reset position",
            windowState.isMinimized ? "Maximize": "Minimize", 
            windowState.isVisible ? "Close" :"Open"
        ];
        const contextMenuCallbacks = [
            () => {resetScreenPosition(windowKey)},
            () => {toggleMinimized(windowKey)},
            () => {toggleVisibility(windowKey)}
        ];
        const backgroundColor = getStateColorRGBA();
        const iconProps = {
            windowKey: windowKey,
            windowState: windowState, 
            toggleWindowVisible: () => {toggleVisibility(windowKey)},
            contextMenuItems: contextMenuItems,
            contextMenuCallbacks: contextMenuCallbacks,
            backgroundColor: backgroundColor
        };
        registerIcon(windowKey, iconProps);
    }, [windowState.isVisible, windowState.isMinimized, datasetLoading, datasetLoaded, connected]);

    const handleChange = (index, value) => {
        const newValues = [...values];
        newValues[index] = value;
        setValues(newValues);
    };

    // Websocket setup (from global context)
    const { subscribe, send } = useWebSocket();
        
    const handleDatasetSelectionChange = (value) => {
        if (value === "manual") {
            setManualEntry(true);
            setDatasetPath("");
        } else {
            setManualEntry(false);
            setDatasetPath(value);
        }
    };
    // Logic to handle the message
    const handleDatasetSettingsMessage = (message) => {
        setDatasetPath(message.data.datasetPath);
        setValues([
            message.data.datasetDevice, 
            message.data.colmapPath, 
            message.data.imagemagickPath]);
        setDatasetLoaded(message.data.loaded);
        setDatasetLoading(message.data.loading);
        setAvailableDatasets(message.data.availableDatasets);
    };

    const handleDatasetLoading = (message) => {
        const data = message.data;
        setDatasetLoaded(data.loaded);
        setDatasetLoading(!data.loaded);
        if(data.loaded){
            const modalContent = (
                <div>
                    <h3>Dataset Loaded</h3>
                    <p>Your dataset has been successfully loaded.</p>
                    <button onClick={closeModal}>Close</button>
                </div>
            );
            openModal(modalContent);
        }
        else{
            const { header, message: text, percent } = data;        
            const modalContent = (
                <div>
                    <h3>{header}</h3>
                    <p>{text}</p>
                    <progress value={percent} max="100"></progress>
                    {/* If you're using a custom progress bar, replace the above line with your component */}
                </div>
            );
            openModal(modalContent);
        }
    }
    useWebSocketListener(subscribe, 'datasetState', handleDatasetSettingsMessage);
    useWebSocketListener(subscribe, 'datasetLoading', handleDatasetLoading);

    const handleInitializeClick = () => {
        
        const message = {
            type: 'datasetInitialize', // Define the message type or structure as needed
            data: {
                "dataset_path": datasetPath,
                "data_device": values[0],
                "colmap_path": values[1],
                "imagemagick_path": values[2]
            },
          };
          send(message); // Use the send function from the context
    };
    const handleLoadPointsClick = () => {
        console.log("Load points clicked.");
        const message = {
            type: 'initFromPCD', // Define the message type or structure as needed
            data: {}
        };
        send(message); // Use the send function from the context
    };

    return (
        windowState.isVisible && (
        <DraggableResizableWindow
          windowKey={windowKey}
          isMinimized={windowState.isMinimized}
          position={windowState.position}
          size={windowState.size}
          zIndex={windowState.zIndex}
          title={windowState.title}
          handleDragStop={handleDragStop}
          handleFocus={handleFocus}
          handleResize={handleResize}
          handleResizeStop={handleResizeStop}
          handleClose={toggleVisibility}
          toggleMinimized={toggleMinimized}
          minConstraints={windowState.minConstraints}
          barColor={getStateColorRGB()}
        >
            <div style={{padding:"5px"}}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px', width: '100%' }}>
                    <label style={{ marginRight: '10px', flexShrink: 0 }}>Dataset path: </label>
                    <select
                        onChange={(e) => handleDatasetSelectionChange(e.target.value)}
                        value={manualEntry ? "manual" : datasetPath}
                        style={{ flexGrow: 1, marginRight: '10px' }}
                    >
                        <option value="manual">Manual Entry</option>
                        {availableDatasets.map((dataset, index) => (
                            <option key={index} value={dataset}>
                                {dataset}
                            </option>
                        ))}
                    </select>
                    <input
                        type="text"
                        disabled={!manualEntry}
                        value={datasetPath}
                        onChange={(e) => setDatasetPath(e.target.value)}
                        placeholder="Enter path or select..."
                        style={{ flexGrow: 1, display: manualEntry ? 'block' : 'none', width: "100%"}}
                    />
                </div>
            {values.map((value, index) => (
                <div key={index} style={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    marginBottom: '5px', 
                    width: '100%' 
                    }}>
                    <label style={{
                        marginRight: '10px', 
                        flexShrink: 0 // Prevent the label from shrinking
                        }}>{variable_names[index]}: </label>
                    <input
                        type="text"
                        value={values[index]}
                        style={{ 
                            //flexGrow: 1, // Input field takes up remaining space
                            marginLeft: 'auto', // Push input to the right
                            width: "100%"
                        }}                                
                        onChange={(e) => handleChange(index, e.target.value)}
                    />
                </div>
            ))}
                <div>
                    <button onClick={handleInitializeClick}>Load dataset</button>
                    <button onClick={handleLoadPointsClick}>Load point cloud</button>
                </div>
            </div>
        </DraggableResizableWindow>)
    );    
};

export default DatasetSetup;


  