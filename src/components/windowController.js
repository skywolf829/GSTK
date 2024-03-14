
  
// WindowController.js
import React, { useState, useEffect, useCallback } from 'react';
import { windowsConfig } from '../utils/windowsConfig';
import IconBar from './IconBar'; // Update with the correct path
import { IconBarProvider } from './IconBarContext';

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
            title: config.title,
            tooltip: config.tooltip,
            icon: config.icon,
            minConstraints: [config.minWidth, config.minHeight],
        };

        // If saved state exists, spread over defaultState to ensure title and minConstraints remain constant
        return savedWindows && savedWindows[key] ? { 
            ...defaultState, ...savedWindows[key], 
            title: config.title, 
            minConstraints: [config.minWidth, config.minHeight],
            icon: config.icon,
            tooltip: config.tooltip
        } : defaultState;
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

    
    const resetScreenPosition = (windowKey) => {
        const midscreen = { x: window.innerWidth / 2.0 - windows[windowKey].size.width / 2.0, 
                            y: window.innerHeight / 2.0 - windows[windowKey].size.height / 2.0
                        };
        setPosition(windowKey, midscreen);
        handleFocus(windowKey);
    }

    const toggleVisibility = useCallback((key) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                isVisible: !currentWindows[key].isVisible,
            },
        }));
        handleFocus(key);
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

    const setTooltip = useCallback((key, tooltip) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                tooltip: tooltip,
            },
        }));
    }, []);

    const setTitle = useCallback((key, title) => {
        setWindows((currentWindows) => ({
            ...currentWindows,
            [key]: {
                ...currentWindows[key],
                title: title,
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
        <IconBarProvider>
            <IconBar />
            {windowsConfig.map(winConfig => {
                const WindowComponent = winConfig.component;
                return <WindowComponent
                    windowKey={winConfig.key}
                    windowState={windows[winConfig.key]}
                    setWindowPosition={setPosition}
                    toggleVisibility={toggleVisibility}                
                    toggleMinimized={toggleMinimized}   
                    resetScreenPosition={resetScreenPosition}   
                    handleDragStop={handleDragStop}          
                    handleFocus={handleFocus}                
                    handleResize={handleResize}
                    handleResizeStop={handleResizeStop}
                    setTooltip={setTooltip}
                    setTitle={setTitle}
                />
            })}
            </IconBarProvider>
         </>
    );
};

export default WindowController;