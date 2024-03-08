

// MyComponent.js
import React, {useState, useEffect} from 'react';
import Draggable from 'react-draggable';
import { Resizable } from 'react-resizable';
import 'react-resizable/css/styles.css';

const TrainerSettings = ({ bringToFront }) => {
    const variable_names = [
        "Total iterations",
        "Initial position learning rate",
        "Final position learning rate",
        "Position learning rate delay multiplier",
        "Position learning rate scheduler max steps",
        "Feature learning rate",
        "Opacity learning rate",
        "Scaling learning rate",
        "Rotation learning rate",
        "Percent dense",
        "SSIM loss weight",
        "Densification interval",
        "Opacity reset interval",
        "Densify from iteration",
        "Densify until iteration",
        "Densify gradient threshold"
    ];
    const variable_steps = [
        1,
        0.000000001,
        0.000000001,
        0.000000001,
        1,
        0.000000001,
        0.000000001,
        0.000000001,
        0.000000001,
        0.001,
        0.001,
        1,
        1,
        1,
        1,
        0.0000001,
    ];
    const variable_defaults = [
        30000,
        0.00016,
        0.0000016,
        0.01,
        30000,
        0.0025,
        0.05,
        0.005,
        0.001,
        0.01,
        0.2,
        100,
        300,
        500,
        1500,
        0.0002,
    ];
    // Visible state
    const [isVisible, setIsVisible] = useState(true);
    
    // Size state
    const [size, setSize] = useState({ width: 400, height: 500 });
    const minConstraints = [380, 150];
    const [position, setPosition] = useState({ x: 0, y: 0 });

    // Input values states
    const [floatValues, setFloatValues] = useState(variable_defaults); // Start with two float inputs
    const [textValue, setTextValue] = useState('');
    const [isChecked, setIsChecked] = useState(false);

    // z-index
    const [zIndex, setZIndex] = useState(100);
    

    useEffect(() => {
        // Load the size and position from localStorage when the component mounts
        const savedSize = JSON.parse(localStorage.getItem('trainerWindowSize'));
        const savedPosition = JSON.parse(localStorage.getItem('trainerWindowPosition'));
    
        if (savedSize) {
          setSize(savedSize);
        }
        if (savedPosition) {
          setPosition(savedPosition);
        }
    }, []);

    const handleFocus = () => {
        const newZIndex = bringToFront();
        setZIndex(newZIndex);
    };

    const handleChange = (index, value) => {
        const newFloatValues = [...floatValues];
        newFloatValues[index] = value;
        setFloatValues(newFloatValues);
    };

    const handleDragStop = (e, data) => {
        // Save the new position to localStorage
        const newPosition = { x: data.x, y: data.y };
        localStorage.setItem('trainerWindowPosition', JSON.stringify(newPosition));
        setPosition(newPosition);
    };

    const handleResizeStop = (event, { size }) => {
        // Save the new size to localStorage
        localStorage.setItem('trainerWindowSize', JSON.stringify(size));
        setSize(size);
    };

    const onResize = (event, { element, size }) => {
        setSize({ width: size.width, height: size.height });
    };
    
    const toggleVisibility = () => {
        setIsVisible(!isVisible);
    };
     
    return (
        isVisible && (
            <Draggable handle=".drag-handle" 
            position={position}
            onStop={handleDragStop}
            onStart={handleFocus}>
                <Resizable width={size.width} 
                height={size.height} 
                onResize={onResize}
                onResizeStop={handleResizeStop}
                minConstraints={minConstraints}>
                    <div style={{ width: size.width, height: size.height, padding: 10, 
                        backgroundColor: '#f0f0f0', position: 'absolute', 
                        borderRadius: '8px', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)' ,
                        display: 'flex', flexDirection: 'column', overflow: 'hidden', 
                        zIndex: zIndex}}>
                        
                        <div style={{ width: '100%', display: 'flex'}}>
                            <span className="drag-handle">Trainer settings</span>
                            <button onClick={toggleVisibility} style={{
                                border: 'none',
                                background: 'none',
                                cursor: 'pointer',
                                width: '35px',
                                height: 'auto',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '12px',
                                backgroundColor: '#ccc',
                                //boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                            }}>
                                <span style={{ color: 'white', fontWeight: 'bold' }}>×</span>
                            </button>
                        </div>
                        <br></br>
                        {floatValues.map((floatValue, index) => (
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
                                type="number"
                                step={variable_steps[index]}
                                value={floatValue}
                                style={{ 
                                    //flexGrow: 1, // Input field takes up remaining space
                                    marginLeft: 'auto', // Push input to the right
                                    width: "100%"
                                }}                                
                                onChange={(e) => handleChange(index, parseFloat(e.target.value))}
                            />
                            </div>
                        ))}
                        <div style={{ display: 'flex', alignItems: 'left', marginBottom: '5px', width: '85%' }}>
                            <label style={{ marginRight: '10px' }}>Text:</label>
                            <input 
                                type="text" 
                                value={textValue} 
                                onChange={e => setTextValue(e.target.value)}
                                style={{width:'100%'}}
                            />
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px', width: '85%' }}>
                            <label style={{ marginRight: '10px' }}>Checkbox:</label>
                            <input 
                                type="checkbox" 
                                checked={isChecked} 
                                onChange={e => setIsChecked(e.target.checked)}
                                style={{width:'100%'}}
                            />
                        </div>
                    </div>
                </Resizable>
            </Draggable>
        )
    );
    
};

export default TrainerSettings;


  