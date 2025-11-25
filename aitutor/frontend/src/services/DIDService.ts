/**
 * D-ID API Service for Real Talking Avatar Videos
 * Creates photorealistic talking head videos from still images
 */

const DID_API_URL = 'https://api.d-id.com';

export interface TalkRequest {
  text: string;
  voiceId?: string;
  avatarImageUrl: string;
}

export interface TalkResponse {
  id: string;
  status: 'created' | 'started' | 'done' | 'error';
  result_url?: string;
}

export interface StreamingSession {
  id: string;
  offer: RTCSessionDescriptionInit;
  ice_servers: RTCIceServer[];
  session_id: string;
}

class DIDService {
  private apiKey: string;
  private peerConnection: RTCPeerConnection | null = null;
  private dataChannel: RTCDataChannel | null = null;
  private streamId: string | null = null;
  private sessionId: string | null = null;
  private videoElement: HTMLVideoElement | null = null;
  private onStreamReady: ((stream: MediaStream) => void) | null = null;

  constructor() {
    // API key should be set via environment variable
    this.apiKey = process.env.REACT_APP_DID_API_KEY || '';
  }

  setApiKey(key: string) {
    this.apiKey = key;
  }

  hasApiKey(): boolean {
    return !!this.apiKey && this.apiKey.length > 10;
  }

  /**
   * Create a streaming session for real-time avatar interaction
   */
  async createStreamingSession(sourceUrl: string): Promise<StreamingSession | null> {
    if (!this.hasApiKey()) {
      console.warn('D-ID API key not configured, using fallback mode');
      return null;
    }

    try {
      const response = await fetch(`${DID_API_URL}/talks/streams`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_url: sourceUrl,
          driver_url: 'bank://lively',
          config: {
            stitch: true,
            result_format: 'mp4'
          }
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        console.error('D-ID streaming session error:', error);
        return null;
      }

      const data = await response.json();
      this.streamId = data.id;
      this.sessionId = data.session_id;

      return {
        id: data.id,
        session_id: data.session_id,
        offer: data.offer,
        ice_servers: data.ice_servers,
      };
    } catch (error) {
      console.error('Failed to create D-ID streaming session:', error);
      return null;
    }
  }

  /**
   * Connect WebRTC for streaming
   */
  async connectStream(
    session: StreamingSession,
    videoElement: HTMLVideoElement,
    onReady?: () => void
  ): Promise<boolean> {
    try {
      this.videoElement = videoElement;

      // Create peer connection
      this.peerConnection = new RTCPeerConnection({
        iceServers: session.ice_servers,
      });

      // Handle incoming stream
      this.peerConnection.ontrack = (event) => {
        if (event.streams && event.streams[0]) {
          videoElement.srcObject = event.streams[0];
          if (this.onStreamReady) {
            this.onStreamReady(event.streams[0]);
          }
          onReady?.();
        }
      };

      // Set remote description (offer from D-ID)
      await this.peerConnection.setRemoteDescription(session.offer);

      // Create and set local description (answer)
      const answer = await this.peerConnection.createAnswer();
      await this.peerConnection.setLocalDescription(answer);

      // Send answer to D-ID
      await this.sendSDPAnswer(session.id, session.session_id, answer);

      // Wait for ICE gathering
      await this.waitForIceGathering();

      return true;
    } catch (error) {
      console.error('Failed to connect WebRTC stream:', error);
      return false;
    }
  }

  private async sendSDPAnswer(
    streamId: string,
    sessionId: string,
    answer: RTCSessionDescriptionInit
  ): Promise<void> {
    await fetch(`${DID_API_URL}/talks/streams/${streamId}/sdp`, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        answer,
        session_id: sessionId,
      }),
    });
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

      this.peerConnection.onicegatheringstatechange = () => {
        if (this.peerConnection?.iceGatheringState === 'complete') {
          resolve();
        }
      };

      // Timeout after 10 seconds
      setTimeout(resolve, 10000);
    });
  }

  /**
   * Make the avatar speak with real lip-sync
   */
  async speak(text: string, voiceId?: string): Promise<boolean> {
    if (!this.streamId || !this.sessionId) {
      console.warn('No active streaming session');
      return false;
    }

    try {
      const response = await fetch(
        `${DID_API_URL}/talks/streams/${this.streamId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Basic ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            script: {
              type: 'text',
              input: text,
              provider: {
                type: 'microsoft',
                voice_id: voiceId || 'en-US-JennyNeural',
              },
            },
            session_id: this.sessionId,
            driver_url: 'bank://lively',
            config: {
              stitch: true,
            },
          }),
        }
      );

      return response.ok;
    } catch (error) {
      console.error('Failed to make avatar speak:', error);
      return false;
    }
  }

  /**
   * Create a non-streaming talk video (for fallback)
   */
  async createTalkVideo(request: TalkRequest): Promise<TalkResponse | null> {
    if (!this.hasApiKey()) {
      return null;
    }

    try {
      const response = await fetch(`${DID_API_URL}/talks`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_url: request.avatarImageUrl,
          script: {
            type: 'text',
            input: request.text,
            provider: {
              type: 'microsoft',
              voice_id: request.voiceId || 'en-US-JennyNeural',
            },
          },
          config: {
            stitch: true,
            result_format: 'mp4',
          },
        }),
      });

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to create talk video:', error);
      return null;
    }
  }

  /**
   * Get talk video status
   */
  async getTalkStatus(talkId: string): Promise<TalkResponse | null> {
    if (!this.hasApiKey()) {
      return null;
    }

    try {
      const response = await fetch(`${DID_API_URL}/talks/${talkId}`, {
        headers: {
          'Authorization': `Basic ${this.apiKey}`,
        },
      });

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get talk status:', error);
      return null;
    }
  }

  /**
   * Close the streaming session
   */
  async closeSession(): Promise<void> {
    if (this.streamId && this.sessionId) {
      try {
        await fetch(`${DID_API_URL}/talks/streams/${this.streamId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Basic ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: this.sessionId,
          }),
        });
      } catch (error) {
        console.error('Failed to close D-ID session:', error);
      }
    }

    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }

    this.streamId = null;
    this.sessionId = null;
    this.videoElement = null;
  }

  isConnected(): boolean {
    return !!(this.streamId && this.sessionId && this.peerConnection);
  }
}

export const didService = new DIDService();
export default DIDService;
