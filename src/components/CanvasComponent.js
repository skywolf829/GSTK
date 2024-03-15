

// MyComponent.js
import React, {useRef, useEffect} from 'react';
import { useWebSocket } from './WebSocketContext';
import 'react-resizable/css/styles.css';

const CanvasComponent = () => {
    const canvasRef = useRef(null);
    let particlesArray = [];
    const mouse = {
      x: null,
      y: null,
      radius: 350 // Adjust the radius of interaction
    };
    const maxSpeed = 500;
    let lastTime = Date.now(); // Initialize with the current time

    // Websocket setup (from global context)
    const { subscribe, send, connected } = useWebSocket();

    class Particle {
      constructor(canvasWidth, canvasHeight) {
          this.x = Math.random() * canvasWidth;
          this.y = Math.random() * canvasHeight;
          this.size = Math.random() * 20 + 5;
          this.speedX = Math.random() * 500 - 250;
          this.speedY = Math.random() * 500 - 250;
          this.r = Math.floor(Math.random() * 256);
          this.g = Math.floor(Math.random() * 256);
          this.b = Math.floor(Math.random() * 256);
          this.a = 100 + Math.floor(Math.random() * 156);
          this.color = `rgb(${this.r}, ${this.g}, ${this.b})`;
          this.color_edge = `rgba(${this.r}, ${this.g}, ${this.b}, 0)`;

        }

      update(canvasWidth, canvasHeight, deltaTime) {
        if (this.x < this.size || this.x > canvasWidth - this.size) {
            this.speedX = -this.speedX; // Reverse the horizontal direction
        }
        if (this.y < this.size || this.y > canvasHeight - this.size) {
            this.speedY = -this.speedY; // Reverse the vertical direction
        }

        this.x += this.speedX * deltaTime;
        this.y += this.speedY * deltaTime;          
          
          // Simple collision detection with the mouse
          const dx = mouse.x - this.x;
          const dy = mouse.y - this.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (distance < mouse.radius + this.size) {
            const mag = (mouse.radius - distance);

              this.speedX -= mag*dx / distance;
              this.speedY -= mag*dy / distance;
          }
        
          const newMag = Math.sqrt(this.speedX * this.speedX + this.speedY * this.speedY);
          if(newMag > maxSpeed){
            const ratio = maxSpeed / newMag;
            this.speedX *= ratio;
            this.speedY *= ratio; 
          }
      }

      draw(ctx) {
        const gradient = ctx.createRadialGradient(this.x, this.y, 
          this.size/4, this.x, this.y, this.size);
        gradient.addColorStop(0, this.color);
        gradient.addColorStop(1, this.color_edge); // Fade to transparent

        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fillStyle = gradient;
        ctx.fill();
      }
    }

    // Set up event listeners after the canvas is rendered
    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const handleMouseDown = (event) => {
          var button = "";
          var correctButton = false;
          if (event.button === 0) {
              button="left";
              correctButton=true;
          } else if (event.button === 2) {
              button="right";
              event.preventDefault(); // Prevent the context menu from appearing
              correctButton=true;
          }
          if(correctButton){
            const message ={ 
                type: 'mouseDown', 
                data: {
                  button: button
                } 
              };
            send(message);
          }
      };

      const handleMouseUp = (event) => {
        var button = "";
        var correctButton = false;
        if (event.button === 0) {
            button="left";
            correctButton=true;
        } else if (event.button === 2) {
            button="right";
            event.preventDefault(); // Prevent the context menu from appearing
            correctButton=true;
        }
        if(correctButton){
          const message ={ 
            type: 'mouseUp', 
            data: {
              button: button
            } 
          };
          send(message);
        }
      };

      const throttle = (func, limit) => {
        let inThrottle;
        return function() {
          const args = arguments;
          const context = this;
          if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
          }
        }
      }

      const handleMouseMove = throttle((event) => {
        // calculate mouse position
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;    // scale mouse coordinates after they have
        const scaleY = canvas.height / rect.height;  // been adjusted to be relative to element
        const x = (event.clientX - rect.left) * scaleX;
        const y = (event.clientY - rect.top) * scaleY;
        mouse.x = event.x;
        mouse.y = event.y;
        const mousePos = { x, y };
        // send mouse position to server
        const message ={ 
          type: 'mouseMove', 
          data: {
            position: mousePos
          } 
        };
        send(message);
      }, 16); // Update every 16ms

      const handleScroll = (event) => {
        // +1 is scroll down, -1 is scroll up
          const message ={ 
            type: 'mouseScroll', 
            data: {
              delta: event.deltaY/100
            } 
          };
          send(message);
          // Use event.deltaY for scroll direction and amount
      };
      
      canvas.addEventListener('mousedown', handleMouseDown);
      canvas.addEventListener('mouseup', handleMouseUp);
      canvas.addEventListener('mousemove', handleMouseMove);
      canvas.addEventListener('wheel', handleScroll);
      
      // Disable the context menu on right-click
      canvas.oncontextmenu = (e) => e.preventDefault();
      

      // Clean up the event listeners when the component unmounts
      return () => {
          canvas.removeEventListener('mousedown', handleMouseDown);
          canvas.removeEventListener('mouseup', handleMouseUp);
          canvas.removeEventListener('mousemove', handleMouseMove);
          canvas.removeEventListener('wheel', handleScroll);
      };
    }, [send]);

    useEffect(() => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      let frameId; // Used to cancel the animation frame

      const startParticlesAnimation = () => {
        if (!connected) {
          initParticles();
          animateParticles();
        }
      };

      const stopParticlesAnimation = () => {
        cancelAnimationFrame(frameId);
      };

      const initParticles = () => {
        particlesArray = [];
        let numberOfParticles = (canvas.height * canvas.width) / 9000;
        for (let i = 0; i < numberOfParticles; i++) {
          particlesArray.push(new Particle(canvas.width, canvas.height));
        }
      };

      const animateParticles = () => {
        const currentTime = Date.now();
        const dt = currentTime - lastTime; // Delta time in milliseconds
        lastTime = currentTime; // Update lastTime for the next frame
        ctx.fillStyle = "#000"; // This sets the fill color to black
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        particlesArray.forEach(particle => {
          particle.update(canvas.width, canvas.height, dt/1000);
          particle.draw(ctx);
        });
        frameId = requestAnimationFrame(animateParticles);
      };

      const renderImageFromServer = (imageBitmap) => {
        if (imageBitmap) {
          canvas.width = imageBitmap.width;
          canvas.height = imageBitmap.height;
          ctx.drawImage(imageBitmap, 0, 0);
        }
      };

      // Start or stop particle animation based on connection status
      if (connected) {
        stopParticlesAnimation(); // Stop particle animation when connected
      } else {
        startParticlesAnimation(); // Start particle animation when not connected
      }

      // Subscribe to server render messages when connected
      let unsubscribe;
      if (connected) {
        unsubscribe = subscribe((message) => message.type === 'render', async (data) => {
          const imageBitmap = await createImageBitmap(data.data);
          renderImageFromServer(imageBitmap);
        });
      }

      return () => {
        if (unsubscribe) unsubscribe(); // Unsubscribe from server messages when not needed
        stopParticlesAnimation(); // Stop animation when component unmounts or when connected
      };
    }, [connected]);

    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;
    
      let timeoutId = null;
      let pendingResize = false;
    
      const sendResizeMessage = (width, height) => {
        // Clear any pending timeout to avoid sending an outdated size
        if (timeoutId !== null) {
          clearTimeout(timeoutId);
          timeoutId = null;
        }
        send({ 
          type: 'updateResolution', 
          data: { 
            width: width, 
            height:height 
          } 
        });
        pendingResize = false;
      };
    
      const handleResize = (entries) => {
        for (let entry of entries) {
          const { width, height } = entry.contentRect;
          sendResizeMessage(width, height);
          if(!connected){
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.fillRect(0, 0, width, height);
          }
        }
      };
    
      const resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(canvas);
    
      // Clean up
      return () => {
        resizeObserver.unobserve(canvas);
        if (timeoutId !== null) {
          clearTimeout(timeoutId);
        }
      };
    }, [send, connected]); // Ensure `send` is included in dependency array if it's not defined inside the effect

    return (
        <div className="canvas-container">
          <canvas ref={canvasRef}  />
        </div>
    );
    
};



export default CanvasComponent;