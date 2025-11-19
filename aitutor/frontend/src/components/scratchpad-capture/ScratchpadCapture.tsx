import React, { useRef, useEffect, ReactNode } from 'react';
import html2canvas from 'html2canvas';

interface ScratchpadCaptureProps {
  children: ReactNode;
  socket: WebSocket | null;
}

const ScratchpadCapture: React.FC<ScratchpadCaptureProps> = ({ children, socket }) => {
  const captureRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const captureAndSend = () => {
      if (captureRef.current && socket && socket.readyState === WebSocket.OPEN) {
        html2canvas(captureRef.current, { useCORS: true, logging: false }).then(canvas => {
          const imageData = canvas.toDataURL('image/jpeg', 0.8);
          // Send as a JSON object to distinguish from other messages
          const payload = JSON.stringify({ type: 'scratchpad_frame', data: imageData });
          console.log('Sending scratchpad frame:', payload.substring(0, 100)); // Log first 100 chars
          socket.send(payload);
        });
      }
    };

    const intervalId = setInterval(() => {
      if (captureRef.current && socket && socket.readyState === WebSocket.OPEN) {
        html2canvas(captureRef.current, { useCORS: true, logging: false }).then(canvas => {
          const imageData = canvas.toDataURL('image/jpeg', 0.8);
          const payload = JSON.stringify({ type: 'scratchpad_frame', data: imageData });
          socket.send(payload);
        }).catch(err => {
          console.error("html2canvas error:", err);
        });
      }
    }, 1000 / 15); // ~15 FPS

    return () => {
      clearInterval(intervalId);
    };
  }, [socket]);

  return <div ref={captureRef} style={{ width: '100%', height: '100%' }}>{children}</div>;
};

export default ScratchpadCapture;
