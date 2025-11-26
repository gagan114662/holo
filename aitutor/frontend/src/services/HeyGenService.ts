/**
 * HeyGen API Service for Photorealistic Streaming Avatars
 * Provides real-time lip-sync video avatars via WebRTC
 *
 * HeyGen offers high-quality avatars with:
 * - Real-time streaming (low latency)
 * - Natural lip-sync
 * - Multiple pre-built avatars
 * - Custom avatar support
 */

const HEYGEN_API_URL = 'https://api.heygen.com';

export interface HeyGenSession {
  session_id: string;
  access_token: string;
  url: string;
  ice_servers: RTCIceServer[];
  sdp_offer?: RTCSessionDescriptionInit;
}

export interface HeyGenAvatar {
  avatar_id: string;
  avatar_name: string;
  preview_image_url: string;
  preview_video_url?: string;
}

export interface HeyGenVoice {
  voice_id: string;
  name: string;
  language: string;
  gender: string;
  preview_audio?: string;
}

export interface StreamingConfig {
  quality: 'low' | 'medium' | 'high';
  avatar_id: string;
  voice_id?: string;
  background?: {
    type: 'color' | 'image' | 'transparent';
    value?: string;
  };
}

type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

class HeyGenService {
  private apiKey: string;
  private sessionId: string | null = null;
  private accessToken: string | null = null;
  private peerConnection: RTCPeerConnection | null = null;
  private dataChannel: RTCDataChannel | null = null;
  private videoElement: HTMLVideoElement | null = null;
  private connectionState: ConnectionState = 'disconnected';
  private onStateChange: ((state: ConnectionState) => void) | null = null;
  private onSpeakingChange: ((speaking: boolean) => void) | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;

  constructor() {
    this.apiKey = process.env.REACT_APP_HEYGEN_API_KEY || '';
  }

  setApiKey(key: string) {
    this.apiKey = key;
  }

  hasApiKey(): boolean {
    return !!this.apiKey && this.apiKey.length > 10;
  }

  setStateChangeCallback(callback: ((state: ConnectionState) => void) | null) {
    this.onStateChange = callback;
  }

  setSpeakingChangeCallback(callback: ((speaking: boolean) => void) | null) {
    this.onSpeakingChange = callback;
  }

  private updateState(state: ConnectionState) {
    this.connectionState = state;
    this.onStateChange?.(state);
  }

  /**
   * Get list of available HeyGen avatars
   */
  async getAvailableAvatars(): Promise<HeyGenAvatar[]> {
    if (!this.hasApiKey()) {
      console.warn('HeyGen API key not configured');
      return [];
    }

    try {
      const response = await fetch(`${HEYGEN_API_URL}/v2/avatars`, {
        headers: {
          'X-Api-Key': this.apiKey,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch avatars: ${response.status}`);
      }

      const data = await response.json();
      return data.data?.avatars || [];
    } catch (error) {
      console.error('Failed to fetch HeyGen avatars:', error);
      return [];
    }
  }

  /**
   * Get list of available voices
   */
  async getAvailableVoices(): Promise<HeyGenVoice[]> {
    if (!this.hasApiKey()) {
      return [];
    }

    try {
      const response = await fetch(`${HEYGEN_API_URL}/v2/voices`, {
        headers: {
          'X-Api-Key': this.apiKey,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch voices: ${response.status}`);
      }

      const data = await response.json();
      return data.data?.voices || [];
    } catch (error) {
      console.error('Failed to fetch HeyGen voices:', error);
      return [];
    }
  }

  /**
   * Create a new streaming session
   */
  async createStreamingSession(config: StreamingConfig): Promise<HeyGenSession | null> {
    if (!this.hasApiKey()) {
      console.warn('HeyGen API key not configured, cannot create session');
      return null;
    }

    try {
      this.updateState('connecting');

      const response = await fetch(`${HEYGEN_API_URL}/v1/streaming.new`, {
        method: 'POST',
        headers: {
          'X-Api-Key': this.apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quality: config.quality,
          avatar_id: config.avatar_id,
          voice: config.voice_id ? { voice_id: config.voice_id } : undefined,
          background: config.background,
          version: 'v2',
          video_encoding: 'VP8',
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('HeyGen session creation failed:', errorText);
        this.updateState('error');
        return null;
      }

      const data = await response.json();

      if (data.error) {
        console.error('HeyGen API error:', data.error);
        this.updateState('error');
        return null;
      }

      this.sessionId = data.data.session_id;
      this.accessToken = data.data.access_token;

      return {
        session_id: data.data.session_id,
        access_token: data.data.access_token,
        url: data.data.url,
        ice_servers: data.data.ice_servers2 || [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' },
        ],
        sdp_offer: data.data.sdp,
      };
    } catch (error) {
      console.error('Failed to create HeyGen session:', error);
      this.updateState('error');
      return null;
    }
  }

  /**
   * Start the streaming session with WebRTC
   */
  async startSession(
    session: HeyGenSession,
    videoElement: HTMLVideoElement
  ): Promise<boolean> {
    try {
      this.videoElement = videoElement;

      // Create peer connection with ICE servers
      this.peerConnection = new RTCPeerConnection({
        iceServers: session.ice_servers,
        iceCandidatePoolSize: 10,
      });

      // Set up event handlers
      this.setupPeerConnectionHandlers();

      // If we have an SDP offer, set it as remote description
      if (session.sdp_offer) {
        await this.peerConnection.setRemoteDescription(
          new RTCSessionDescription(session.sdp_offer)
        );

        // Create and send answer
        const answer = await this.peerConnection.createAnswer();
        await this.peerConnection.setLocalDescription(answer);

        // Send answer to HeyGen
        await this.sendSDPAnswer(session.session_id, answer);
      } else {
        // Create offer ourselves
        const offer = await this.peerConnection.createOffer({
          offerToReceiveVideo: true,
          offerToReceiveAudio: true,
        });
        await this.peerConnection.setLocalDescription(offer);

        // Send offer and get answer
        const answerSdp = await this.exchangeSDP(session.session_id, offer);
        if (answerSdp) {
          await this.peerConnection.setRemoteDescription(
            new RTCSessionDescription(answerSdp)
          );
        }
      }

      // Wait for ICE gathering to complete
      await this.waitForIceGathering();

      // Start the session
      await this.sendStartCommand(session.session_id);

      this.reconnectAttempts = 0;
      return true;
    } catch (error) {
      console.error('Failed to start HeyGen session:', error);
      this.updateState('error');
      return false;
    }
  }

  private setupPeerConnectionHandlers() {
    if (!this.peerConnection) return;

    // Handle incoming video stream
    this.peerConnection.ontrack = (event) => {
      console.log('Received track:', event.track.kind);
      if (this.videoElement && event.streams[0]) {
        this.videoElement.srcObject = event.streams[0];
        this.videoElement.play().catch(console.error);
      }
    };

    // Handle connection state changes
    this.peerConnection.onconnectionstatechange = () => {
      const state = this.peerConnection?.connectionState;
      console.log('WebRTC connection state:', state);

      switch (state) {
        case 'connected':
          this.updateState('connected');
          break;
        case 'disconnected':
        case 'failed':
          this.handleDisconnection();
          break;
        case 'closed':
          this.updateState('disconnected');
          break;
      }
    };

    // Handle ICE connection state
    this.peerConnection.oniceconnectionstatechange = () => {
      console.log('ICE connection state:', this.peerConnection?.iceConnectionState);
    };

    // Handle ICE candidates
    this.peerConnection.onicecandidate = async (event) => {
      if (event.candidate && this.sessionId) {
        await this.sendIceCandidate(this.sessionId, event.candidate);
      }
    };

    // Set up data channel for commands
    this.dataChannel = this.peerConnection.createDataChannel('commands');
    this.dataChannel.onopen = () => {
      console.log('Data channel opened');
    };
    this.dataChannel.onmessage = (event) => {
      this.handleDataChannelMessage(event.data);
    };
  }

  private handleDataChannelMessage(data: string) {
    try {
      const message = JSON.parse(data);

      switch (message.type) {
        case 'speaking_started':
          this.onSpeakingChange?.(true);
          break;
        case 'speaking_ended':
          this.onSpeakingChange?.(false);
          break;
        case 'error':
          console.error('HeyGen data channel error:', message.error);
          break;
      }
    } catch (error) {
      console.log('Data channel message:', data);
    }
  }

  private async handleDisconnection() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      this.updateState('connecting');

      // Wait before reconnecting
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Try to reconnect - would need to recreate session
      // For now, just update state
      this.updateState('error');
    } else {
      this.updateState('error');
    }
  }

  private async sendSDPAnswer(
    sessionId: string,
    answer: RTCSessionDescriptionInit
  ): Promise<void> {
    const response = await fetch(`${HEYGEN_API_URL}/v1/streaming.sdp`, {
      method: 'POST',
      headers: {
        'X-Api-Key': this.apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        sdp: answer,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to send SDP answer: ${response.status}`);
    }
  }

  private async exchangeSDP(
    sessionId: string,
    offer: RTCSessionDescriptionInit
  ): Promise<RTCSessionDescriptionInit | null> {
    const response = await fetch(`${HEYGEN_API_URL}/v1/streaming.sdp`, {
      method: 'POST',
      headers: {
        'X-Api-Key': this.apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        sdp: offer,
      }),
    });

    if (!response.ok) {
      throw new Error(`SDP exchange failed: ${response.status}`);
    }

    const data = await response.json();
    return data.data?.sdp || null;
  }

  private async sendIceCandidate(
    sessionId: string,
    candidate: RTCIceCandidate
  ): Promise<void> {
    try {
      await fetch(`${HEYGEN_API_URL}/v1/streaming.ice`, {
        method: 'POST',
        headers: {
          'X-Api-Key': this.apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          candidate: candidate.toJSON(),
        }),
      });
    } catch (error) {
      console.warn('Failed to send ICE candidate:', error);
    }
  }

  private async sendStartCommand(sessionId: string): Promise<void> {
    const response = await fetch(`${HEYGEN_API_URL}/v1/streaming.start`, {
      method: 'POST',
      headers: {
        'X-Api-Key': this.apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to start stream: ${response.status}`);
    }
  }

  private waitForIceGathering(): Promise<void> {
    return new Promise((resolve) => {
      if (!this.peerConnection) {
        resolve();
        return;
      }

      if (this.peerConnection.iceGatheringState === 'complete') {
        resolve();
        return;
      }

      const checkState = () => {
        if (this.peerConnection?.iceGatheringState === 'complete') {
          this.peerConnection.removeEventListener('icegatheringstatechange', checkState);
          resolve();
        }
      };

      this.peerConnection.addEventListener('icegatheringstatechange', checkState);

      // Timeout after 10 seconds
      setTimeout(() => {
        this.peerConnection?.removeEventListener('icegatheringstatechange', checkState);
        resolve();
      }, 10000);
    });
  }

  /**
   * Make the avatar speak with real-time lip-sync
   */
  async speak(text: string, taskType: 'talk' | 'repeat' = 'talk'): Promise<boolean> {
    if (!this.sessionId) {
      console.warn('No active HeyGen session');
      return false;
    }

    try {
      const response = await fetch(`${HEYGEN_API_URL}/v1/streaming.task`, {
        method: 'POST',
        headers: {
          'X-Api-Key': this.apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          text: text,
          task_type: taskType,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('HeyGen speak failed:', errorText);
        return false;
      }

      this.onSpeakingChange?.(true);

      const data = await response.json();
      return data.code === 100 || data.data?.task_id;
    } catch (error) {
      console.error('Failed to make HeyGen avatar speak:', error);
      return false;
    }
  }

  /**
   * Interrupt current speech
   */
  async interrupt(): Promise<boolean> {
    if (!this.sessionId) {
      return false;
    }

    try {
      const response = await fetch(`${HEYGEN_API_URL}/v1/streaming.interrupt`, {
        method: 'POST',
        headers: {
          'X-Api-Key': this.apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
        }),
      });

      this.onSpeakingChange?.(false);
      return response.ok;
    } catch (error) {
      console.error('Failed to interrupt HeyGen speech:', error);
      return false;
    }
  }

  /**
   * Close the streaming session
   */
  async closeSession(): Promise<void> {
    if (this.sessionId) {
      try {
        await fetch(`${HEYGEN_API_URL}/v1/streaming.stop`, {
          method: 'POST',
          headers: {
            'X-Api-Key': this.apiKey,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: this.sessionId,
          }),
        });
      } catch (error) {
        console.error('Failed to close HeyGen session:', error);
      }
    }

    // Clean up
    if (this.dataChannel) {
      this.dataChannel.close();
      this.dataChannel = null;
    }

    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }

    this.sessionId = null;
    this.accessToken = null;
    this.videoElement = null;
    this.updateState('disconnected');
  }

  /**
   * Check if there's an active session
   */
  isConnected(): boolean {
    return this.connectionState === 'connected' && this.sessionId !== null;
  }

  /**
   * Get current connection state
   */
  getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  /**
   * Get session ID
   */
  getSessionId(): string | null {
    return this.sessionId;
  }
}

// Export singleton instance
export const heygenService = new HeyGenService();
export default HeyGenService;
