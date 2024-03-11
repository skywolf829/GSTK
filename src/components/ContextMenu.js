import React from 'react';
import styles from '../css/ContextMenu.module.css'; // You need to create this CSS module

const ContextMenu = ({ x, y, onResetPosition, onMinimize, onClose }) => {
  const style = {
    top: y,
    left: x
  };

  return (
    <div className={styles.contextMenu} style={style}>
      <button className={styles.contextMenuItem} onClick={onResetPosition}>
        Reset position
      </button>
      <button className={styles.contextMenuItem} onClick={onMinimize}>
        Minimize
      </button>
      <button className={styles.contextMenuItem} onClick={onClose}>
        Close
      </button>
    </div>
  );
};

export default ContextMenu;