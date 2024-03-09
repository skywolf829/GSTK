
  
// WindowController.js
import React, { useState, useEffect } from 'react';
import { windowsConfig } from '../utils/windowsConfig';
import IconBar from './IconBar'; // Update with the correct path

const WindowController = ({bringToFront}) => {
    // Initialize window state using the config
    const [windowStates, setWindowStates] = useState(() => {
        const savedStates = JSON.parse(localStorage.getItem('windowStates'));
        return savedStates || windowsConfig.reduce((states, winConfig) => {
        states[winConfig.key] = true; // Initialize all windows as open, or customize as needed
        return states;
        }, {});
    });

    useEffect(() => {
        localStorage.setItem('windowStates', JSON.stringify(windowStates));
    }, [windowStates]);

    const toggleWindow = (windowKey) => {
        setWindowStates(prevStates => ({
        ...prevStates,
        [windowKey]: !prevStates[windowKey],
        }));
    };


    return (
        <>
        <IconBar windowStates={windowStates} toggleWindow={toggleWindow} />
        {windowsConfig.map(winConfig => {
            const WindowComponent = winConfig.component;
            return windowStates[winConfig.key] && (
            <WindowComponent
                key={winConfig.key}
                bringToFront={bringToFront}
                onClose={() => toggleWindow(winConfig.key)}
            />
            );
        })}
        </>
    );
};

export default WindowController;