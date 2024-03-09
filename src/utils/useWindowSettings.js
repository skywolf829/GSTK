// useWindowSettings.js
import { useState, useEffect, useCallback } from 'react';

const HEADER_HEIGHT = 30; // Assume a fixed header height for minimized view

const useWindowSettings = (storageKey, minConstraints, bringToFront) => {
  // Helper function to get the value from localStorage or return a default
  const getFromStorage = (key, defaultValue) => {
    const storedValue = localStorage.getItem(`${storageKey}${key}`);
    return storedValue !== null ? JSON.parse(storedValue) : defaultValue;
  };

  // Helper function to set a value to localStorage
  const saveToStorage = useCallback((key, value) => {
    localStorage.setItem(`${storageKey}${key}`, JSON.stringify(value));
  }, [storageKey]);

  const [isMinimized, setIsMinimized] = 
    useState(() => getFromStorage('IsMinimized', false));
  const [size, setSize] = useState(() => 
    getFromStorage('Size', { width: minConstraints[0], height: minConstraints[1] }));
  const [originalSize, setOriginalSize] = useState(() => 
    getFromStorage('OriginalSize', size));
  const [position, setPosition] = useState(() => 
    getFromStorage('Position', { x: 0, y: 0 }));
  const [zIndex, setZIndex] = useState(() => 
    getFromStorage('ZIndex', 100));

  const toggleMinimized = useCallback(() => {
    setIsMinimized(m => {
      if (!m) {
        // If we're minimizing, save the current size and set height to header height
        setOriginalSize(size);
        setSize(prevSize => ({ ...prevSize, height: HEADER_HEIGHT }));
      } else {
        // If we're un-minimizing, restore the original size
        setSize(originalSize);
      }
      return !m;
    });
  }, [size, originalSize]);

  // Save position to localStorage
  const handleDragStop = (e, data) => {
    const newPosition = { x: data.x, y: data.y };
    localStorage.setItem(`${storageKey}Position`, JSON.stringify(newPosition));
    setPosition(newPosition);
  };

  // Save size to localStorage
  const handleResizeStop = (event, { size }) => {
    localStorage.setItem(`${storageKey}Size`, JSON.stringify(size));
    setSize(size);
  };

   // Focus handling could be more generalized, depending on the use case
   const handleFocus = () => {
    const newZIndex = bringToFront();
    setZIndex(newZIndex);
};

  // Update size state during resize action
  const handleResize = (event, { size }) => {
    setSize(size);
  };

  // Update localStorage when size, position, or zIndex changes
  useEffect(() => saveToStorage('Size', size), [size, saveToStorage]);
  useEffect(() => saveToStorage('Position', position), [position, saveToStorage]);
  useEffect(() => saveToStorage('OriginalSize', originalSize), [originalSize, saveToStorage]);
  useEffect(() => saveToStorage('ZIndex', zIndex), [zIndex, saveToStorage]);
  useEffect(() => saveToStorage('IsMinimized', isMinimized), [isMinimized, saveToStorage]);

  return {
    isMinimized, setIsMinimized,
    size, setSize,
    position, setPosition,
    zIndex, setZIndex,
    handleFocus,
    toggleMinimized,
    handleDragStop, 
    handleResizeStop, 
    handleResize
  };
};

export default useWindowSettings;