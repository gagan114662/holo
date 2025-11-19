import { useCallback } from 'react';

interface UseMediaMixerProps {
  socket: WebSocket | null;
}

export function useMediaMixer({ socket }: UseMediaMixerProps) {
  const sendCommand = useCallback(
    (command: string) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        console.log(`Sending command to MediaMixer: ${command}`);
        socket.send(command);
      } else {
        console.error('MediaMixer socket not connected or not available.');
      }
    },
    [socket]
  );

  return { sendCommand };
}
