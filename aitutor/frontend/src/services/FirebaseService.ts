/**
 * Firebase Authentication Service
 * Real authentication replacing localStorage mock
 */

import { initializeApp } from 'firebase/app';
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  onAuthStateChanged,
  User,
  updateProfile,
  sendPasswordResetEmail,
} from 'firebase/auth';

// Firebase configuration from environment
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
}

class FirebaseService {
  private currentUser: User | null = null;
  private authStateListeners: ((user: AuthUser | null) => void)[] = [];

  constructor() {
    // Listen to auth state changes
    onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
      const authUser = user ? this.mapUser(user) : null;
      this.authStateListeners.forEach(listener => listener(authUser));
    });
  }

  private mapUser(user: User): AuthUser {
    return {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      photoURL: user.photoURL,
      emailVerified: user.emailVerified,
    };
  }

  /**
   * Sign up with email and password
   */
  async signUp(email: string, password: string, displayName: string): Promise<AuthUser> {
    const credential = await createUserWithEmailAndPassword(auth, email, password);
    
    // Update display name
    if (credential.user) {
      await updateProfile(credential.user, { displayName });
    }
    
    return this.mapUser(credential.user);
  }

  /**
   * Sign in with email and password
   */
  async signIn(email: string, password: string): Promise<AuthUser> {
    const credential = await signInWithEmailAndPassword(auth, email, password);
    return this.mapUser(credential.user);
  }

  /**
   * Sign in with Google
   */
  async signInWithGoogle(): Promise<AuthUser> {
    const result = await signInWithPopup(auth, googleProvider);
    return this.mapUser(result.user);
  }

  /**
   * Sign out
   */
  async signOut(): Promise<void> {
    await signOut(auth);
  }

  /**
   * Send password reset email
   */
  async resetPassword(email: string): Promise<void> {
    await sendPasswordResetEmail(auth, email);
  }

  /**
   * Get current user
   */
  getCurrentUser(): AuthUser | null {
    return this.currentUser ? this.mapUser(this.currentUser) : null;
  }

  /**
   * Get Firebase ID token for API authentication
   */
  async getIdToken(): Promise<string | null> {
    if (!this.currentUser) return null;
    return this.currentUser.getIdToken();
  }

  /**
   * Subscribe to auth state changes
   */
  onAuthStateChange(callback: (user: AuthUser | null) => void): () => void {
    this.authStateListeners.push(callback);
    
    // Call immediately with current state
    if (this.currentUser) {
      callback(this.mapUser(this.currentUser));
    }
    
    // Return unsubscribe function
    return () => {
      const index = this.authStateListeners.indexOf(callback);
      if (index > -1) {
        this.authStateListeners.splice(index, 1);
      }
    };
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.currentUser !== null;
  }
}

// Export singleton instance
export const firebaseService = new FirebaseService();
export { auth };
