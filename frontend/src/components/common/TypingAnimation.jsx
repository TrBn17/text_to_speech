import React, { useState, useEffect } from 'react';

import styles from './TypingAnimation.module.css';

const TypingAnimation = () => {
  const texts = [
    "Hello, I'm your AI Assistant",
    "How can I help you?"
  ];

  const [currentTextIndex, setCurrentTextIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    const typeText = async () => {
      const fullText = texts[currentTextIndex];

      if (isTyping) {
        // Typing effect
        if (currentText.length < fullText.length) {
          setTimeout(() => {
            setCurrentText(fullText.slice(0, currentText.length + 1));
          }, 100); // Typing speed
        } else {
          // Finished typing current text
          setIsTyping(false);
          setTimeout(() => {
            setIsTyping(true);
            setCurrentText('');
            setCurrentTextIndex((prev) => (prev + 1) % texts.length);
          }, 3000); // Wait 3 seconds before next text
        }
      }
    };

    typeText();
  }, [currentText, isTyping, currentTextIndex, texts]);

  // Cursor blinking effect
  useEffect(() => {
    const cursorInterval = setInterval(() => {
      setShowCursor(prev => !prev);
    }, 500);

    return () => clearInterval(cursorInterval);
  }, []);

  // Reset animation every 90 seconds
  useEffect(() => {
    const resetInterval = setInterval(() => {
      setCurrentTextIndex(0);
      setCurrentText('');
      setIsTyping(true);
    }, 90000); // 90 seconds

    return () => clearInterval(resetInterval);
  }, []);

  return (
    <div className={styles.typingContainer}>
      <span className={styles.typingText}>
        {currentText}
        <span className={`${styles.cursor} ${showCursor ? styles.visible : styles.hidden}`}>
          |
        </span>
      </span>
    </div>
  );
};

export default TypingAnimation;