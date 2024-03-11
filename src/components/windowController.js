
  
// WindowController.js
import React, { useState, useEffect } from 'react';
import { windowsConfig } from '../utils/windowsConfig';
import IconBar from './IconBar'; // Update with the correct path

const WindowController = ({bringToFront}) => {
    // Initialize window state using the config
    const [windowVisibleStates, setWindowVisibleStates] = useState(() => {
        const savedStates = JSON.parse(localStorage.getItem('windowVisibleStates'));
        return savedStates || windowsConfig.reduce((states, winConfig) => {
        states[winConfig.key] = true; // Initialize all windows as open, or customize as needed
        return states;
        }, {});
    });

    useEffect(() => {
        localStorage.setItem('windowVisibleStates', JSON.stringify(windowVisibleStates));
    }, [windowVisibleStates]);

    const manageWindow = (action, windowKey) => {
        if(action == "toggleVisible"){
            setWindowVisibleStates(prevStates => ({
            ...prevStates,
            [windowKey]: !prevStates[windowKey],
            }));
        }
    };


    return (
        <>
        <IconBar windowVisibleStates={windowVisibleStates} manageWindow={manageWindow} />
        {windowsConfig.map(winConfig => {
            const WindowComponent = winConfig.component;
            return windowVisibleStates[winConfig.key] && (
            <WindowComponent
                key={winConfig.key}
                bringToFront={bringToFront}
                onClose={() => manageWindow("toggleVisible", winConfig.key)}
            />
            );
        })}
        </>
    );
};

export default WindowController;