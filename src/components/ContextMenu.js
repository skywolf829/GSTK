import React from 'react';
import styles from '../css/ContextMenu.module.css'; // You need to create this CSS module

const ContextMenu = ({ x, y, items, callbacks }) => {
  const style = {
    top: y,
    left: x
  };
  return (
    <div className={styles.contextMenu} style={style}>
      {items.map((item, i) => (
        <button className={styles.contextMenuItem} onClick={callbacks[i]}>
          {items[i]}
        </button>
      ))}
    </div>
  );
};

export default ContextMenu;