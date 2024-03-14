import React, { createContext, useContext, useState } from 'react';

const IconBarContext = createContext();

export const useIconBar = () => useContext(IconBarContext);

export const IconBarProvider = ({ children }) => {
  const [icons, setIcons] = useState({}); // Stores the state and content of each icon

  // Register an icon and its state
  const registerIcon = (key, iconContent) => {
    setIcons(prevIcons => ({ ...prevIcons, [key]: iconContent }));
  };

  // Update the state of an icon
  const updateIconState = (key, iconState) => {
    setIcons(prevIcons => ({
      ...prevIcons,
      [key]: { ...prevIcons[key], state: iconState },
    }));
  };

  return (
    <IconBarContext.Provider value={{ icons, registerIcon, updateIconState }}>
      {children}
    </IconBarContext.Provider>
  );
};