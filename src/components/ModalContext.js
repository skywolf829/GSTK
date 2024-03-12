import { createContext, useContext, useState, useCallback } from 'react';
import styles from '../css/Modal.module.css'; // Ensure you have the appropriate modal styles

const ModalContext = createContext();

export const useModal = () => useContext(ModalContext);

export const ModalProvider = ({ children }) => {
  const [modalContent, setModalContent] = useState(null);

  const openModal = useCallback((content) => {
    setModalContent(content);
  }, []);

  const closeModal = useCallback(() => {
    setModalContent(null);
  }, []);

  const value = {
    modalContent,
    openModal,
    closeModal,
  };

  return (
    <ModalContext.Provider value={value}>
      {children}
      {modalContent && (
        <div className={styles.modalBackdrop}>
          <div className={styles.modalContent}>{modalContent}</div>
        </div>
      )}
    </ModalContext.Provider>
  );
};