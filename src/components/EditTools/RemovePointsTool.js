import React, { useState } from 'react';

const RemovePointsTool = ({ onRemovePoints }) => {
  const [invertSelection, setInvertSelection] = useState(false);
  const [percentage, setPercentage] = useState(50);

  const handleInvertSelectionChange = (event) => {
    setInvertSelection(event.target.checked);
  };

  const handlePercentageChange = (event) => {
    setPercentage(event.target.value);
  };

  const handleRemovePointsClick = () => {
    if (onRemovePoints) {
      onRemovePoints({
        percentage: parseInt(percentage, 10),
        invertSelection: invertSelection,
      });
    }
  };

  return (
    <div className='toolbar-window-content'>
      <span>Remove Points Tool</span>
      <div>
        <label htmlFor="invertSelection">Invert Selection:</label>
        <input
          id="invertSelection"
          type="checkbox"
          checked={invertSelection}
          onChange={handleInvertSelectionChange}
        />
      </div>
      <div>
        <label htmlFor="percentage">Percentage of Points to Remove:</label>
        <input
          id="percentage"
          type="range"
          min="1"
          max="100"
          value={percentage}
          onChange={handlePercentageChange}
        />
        {percentage}%
      </div>
      <button onClick={handleRemovePointsClick}>Remove Points</button>
    </div>
  );
};

export default RemovePointsTool;
