import React, { useState } from 'react';
import { useWebSocket } from '../WebSocketContext';

const RemovePointsTool = () => {
  const [invertSelection, setInvertSelection] = useState(false);
  const [percentage, setPercentage] = useState(100);
  const { send } = useWebSocket();

  const handleInvertSelectionChange = (event) => {
    setInvertSelection(event.target.checked);
    const message = {
      type: "editorSelectionInverted",
      data: {
        inverted: event.target.checked
      }
    };
    send(message);
  };

  const handlePercentageChange = (event) => {
    setPercentage(event.target.value);
  };

  const handleRemovePointsClick = () => {
    const message = {
      type: "processEdit",
      data: {
        editType: "removePoints",
        payload: {
          removePercent: parseFloat(percentage),
          invertSelection: invertSelection,
        }
      }
    };
    send(message);
  };

  return (
    <div className='toolbar-window-content'>
      <span>Remove Points Tool</span>
      <div>
        <label htmlFor="invertSelection">Invert View Selection:</label>
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
