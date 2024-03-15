import React, { useState } from 'react';

const AddPointsTool = ({ onAddPoints }) => {
  const [pointCount, setPointCount] = useState(10);
  const [distribution, setDistribution] = useState('uniform');

  const handlePointCountChange = (event) => {
    setPointCount(event.target.value);
  };

  const handleDistributionChange = (event) => {
    setDistribution(event.target.value);
  };

  const handleAddPointsClick = () => {
    if (onAddPoints) {
      onAddPoints({
        count: parseInt(pointCount, 10),
        distribution: distribution,
      });
    }
  };

  return (
    <div className='toolbar-window-content'>
      <span>Add Points Tool</span>
      <div>
        <label htmlFor="pointCount">Number of Points:</label>
        <input
          id="pointCount"
          type="number"
          value={pointCount}
          onChange={handlePointCountChange}
          min="1"
        />
      </div>
      <div>
        <label htmlFor="distribution">Distribution:</label>
        <select id="distribution" value={distribution} onChange={handleDistributionChange}>
          <option value="uniform">Uniform</option>
          <option value="normal">Normal</option>
          <option value="inverseNormal">Inverse Normal</option>
        </select>
      </div>
      <button onClick={handleAddPointsClick}>Add Points</button>
    </div>
  );
};

export default AddPointsTool;