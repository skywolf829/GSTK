
  
// WindowController.js
import React, { useState, useEffect, useCallback } from 'react';
import { windowsConfig } from '../utils/windowsConfig';
import IconBar from './IconBar'; // Update with the correct path

const HEADER_HEIGHT = 30; // Assume a fixed header height for minimized view

const WindowController = () => {
    

    const loadWindowState = (key, config) => {
        const savedWindows = JSON.parse(localStorage.getItem('windows'));
        const defaultState = {
            isVisible: true,
            isMinimized: false,
            size: { width: config.minWidth, height: config.minHeight },
            originalSize: { width: config.minWidth, height: config.minHeight },
            position: { x: 0, y: 0 },
            zIndex: 100,
            // Always use title and minConstraints from config
            title: config.title,
            minConstraints: [config.minWidth, config.minHeight],
        };

        // If saved state exists, spread over defaultState to ensure title and minConstraints remain constant
        return savedWindows && savedWindows[key] ? { ...defaultState, ...savedWindows[key], title: config.title, minConstraints: [config.minWidth, config.minHeight] } : defaultState;
    };

    const initialWindowStates = windowsConfig.reduce((states, config) => ({
        ...states,
        [config.key]: loadWindowState(config.key, config)
    }), {});

    const [windows, setWindows] = useState(initialWindowStates);
  
    // Save to local storage whenever windows state changes
    useEffect(() => {
        localStorage.setItem('windows', JSON.stringify(windows));
    }, [windows]);

    const toggleVisibility = useCallback((key) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                isVisible: !currentWindows[key].isVisible,
            },
        }));
    }, []);

    const toggleMinimized = useCallback((key) => {
        setWindows((currentWindows) => {
            const currentWindow = currentWindows[key];
            let newSize, newOriginalSize;
    
            if (!currentWindow.isMinimized) {
                // Minimizing: save the current size and set height to header height
                newOriginalSize = currentWindow.size;
                newSize = { ...currentWindow.size, 
                    width:currentWindow.size.width, 
                    height: HEADER_HEIGHT };
            } else {
                // Un-minimizing: restore the original size
                currentWindow.originalSize.width = currentWindow.size.width;
                newSize = currentWindow.originalSize || currentWindow.size;
                newOriginalSize = currentWindow.originalSize;

            }
    
            return {
                ...currentWindows,
                [key]: {
                    ...currentWindow,
                    isMinimized: !currentWindow.isMinimized,
                    size: newSize,
                    originalSize: newOriginalSize,
                },
            };
        });
    }, []);

    const setPosition = useCallback((key, position) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                position: position,
            },
        }));
    }, []);

    const setSize = useCallback((key, size) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                size: size,
            },
        }));
    }, []);

    const setOriginalSize = useCallback((key, originalSize) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                originalSize: originalSize,
            },
        }));
    }, []);

    const setZIndex = useCallback((key, zIndex) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                zIndex: zIndex,
            },
        }));
    }, []);
    
    const handleDragStop = useCallback((key, data) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                position: { x: data.x, y: data.y },
            },
        }));
    }, []);
    
    const handleResizeStop = useCallback((key, size) => {
        
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                size: size,
            },
        }));
    }, []);
    
    const handleFocus = useCallback((key) => {
        setWindows((currentWindows) => {
            const highestZIndex = Math.max(...Object.values(currentWindows).map(window => window.zIndex)) + 1;
            return {
                ...currentWindows,
                [key]: {
                    ...currentWindows[key],
                    zIndex: highestZIndex,
                },
            };
        });
    }, []);
    
    const handleResize = useCallback((key, size) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                size: size,
            },
        }));
    }, []);

    return (
        <>
        <IconBar windows={windows} 
            toggleWindowMinimized={toggleMinimized} 
            toggleWindowVisible={toggleVisibility} 
            setWindowPosition={setPosition}
            handleFocus={handleFocus}
            />
        {windowsConfig.map(winConfig => {
            const WindowComponent = winConfig.component;
            return windows[winConfig.key].isVisible && (
            <WindowComponent
                windowKey={winConfig.key}
                windowState={windows[winConfig.key]}
                toggleVisibility={toggleVisibility}                
                toggleMinimized={toggleMinimized}      
                handleDragStop={handleDragStop}          
                handleFocus={handleFocus}                
                handleResize={handleResize}
                handleResizeStop={handleResizeStop}
            />
            );
        })}
        </>
    );
};

export default WindowController;