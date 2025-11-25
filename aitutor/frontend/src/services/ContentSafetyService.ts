/**
 * Content Safety & Moderation Service
 * Ensures age-appropriate content for educational platform
 */

export interface SafetyCheckResult {
  isSafe: boolean;
  flaggedCategories: string[];
  severity: 'none' | 'low' | 'medium' | 'high';
  sanitizedContent?: string;
  message?: string;
}

export interface SafetyConfig {
  enableProfanityFilter: boolean;
  enableTopicFilter: boolean;
  enablePersonalInfoFilter: boolean;
  ageGroup: 'elementary' | 'middle_school' | 'high_school' | 'adult';
  strictMode: boolean;
}

const DEFAULT_CONFIG: SafetyConfig = {
  enableProfanityFilter: true,
  enableTopicFilter: true,
  enablePersonalInfoFilter: true,
  ageGroup: 'middle_school',
  strictMode: false,
};

// Inappropriate content patterns (basic list - production would use ML models)
const PROFANITY_PATTERNS = [
  /\b(damn|hell|crap)\b/gi, // mild
  // More severe patterns would be handled server-side
];

// Topics that should be redirected to educational context
const SENSITIVE_TOPICS = [
  'violence',
  'weapons',
  'drugs',
  'alcohol',
  'dating',
  'politics',
  'religion',
];

// Personal information patterns
const PERSONAL_INFO_PATTERNS = [
  /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/, // Phone numbers
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/, // Email
  /\b\d{5}(-\d{4})?\b/, // ZIP codes
  /\b\d{3}[-]?\d{2}[-]?\d{4}\b/, // SSN pattern
  /\b(my address is|i live at|my home is)/i, // Address disclosure
];

// Educational redirects for sensitive topics
const TOPIC_REDIRECTS: Record<string, string> = {
  violence: "Let's focus on conflict resolution and peace-building instead. What aspects of historical diplomacy interest you?",
  weapons: "I'd be happy to discuss the history of defense technology or engineering innovations. What era interests you?",
  drugs: "Let's explore the science of pharmacology or the history of medicine. Would you like to learn about medical breakthroughs?",
  alcohol: "I can teach you about chemistry, fermentation science, or the history of prohibition. Which interests you?",
  dating: "Relationships are important! Let's explore communication skills or historical figures known for their partnerships.",
  politics: "Great interest in civics! Let's explore how governments work, historical elections, or constitutional principles.",
  religion: "Philosophy and belief systems are fascinating! Would you like to explore world religions from an academic perspective?",
};

class ContentSafetyService {
  private config: SafetyConfig;
  private warningCount: number = 0;
  private sessionBlocked: boolean = false;

  constructor(config: Partial<SafetyConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Check if user input is safe and appropriate
   */
  checkUserInput(input: string): SafetyCheckResult {
    if (this.sessionBlocked) {
      return {
        isSafe: false,
        flaggedCategories: ['session_blocked'],
        severity: 'high',
        message: 'Session has been temporarily restricted. Please contact your teacher or parent.',
      };
    }

    const flaggedCategories: string[] = [];
    let severity: SafetyCheckResult['severity'] = 'none';
    let sanitizedContent = input;

    // Check for profanity
    if (this.config.enableProfanityFilter) {
      for (const pattern of PROFANITY_PATTERNS) {
        if (pattern.test(input)) {
          flaggedCategories.push('mild_language');
          severity = 'low';
          sanitizedContent = sanitizedContent.replace(pattern, '***');
        }
      }
    }

    // Check for personal information
    if (this.config.enablePersonalInfoFilter) {
      for (const pattern of PERSONAL_INFO_PATTERNS) {
        if (pattern.test(input)) {
          flaggedCategories.push('personal_info');
          severity = this.escalateSeverity(severity, 'medium');
          sanitizedContent = sanitizedContent.replace(pattern, '[REDACTED]');
        }
      }
    }

    // Check for sensitive topics
    if (this.config.enableTopicFilter) {
      const lowerInput = input.toLowerCase();
      for (const topic of SENSITIVE_TOPICS) {
        if (lowerInput.includes(topic)) {
          flaggedCategories.push(`topic_${topic}`);
          severity = this.escalateSeverity(severity, 'low');
        }
      }
    }

    // Update warning count for repeated issues
    if (severity !== 'none') {
      this.warningCount++;
      if (this.warningCount >= 5 && this.config.strictMode) {
        this.sessionBlocked = true;
      }
    }

    return {
      isSafe: severity === 'none' || severity === 'low',
      flaggedCategories,
      severity,
      sanitizedContent,
      message: this.generateMessage(flaggedCategories, severity),
    };
  }

  /**
   * Get educational redirect for sensitive topic
   */
  getTopicRedirect(topic: string): string | null {
    return TOPIC_REDIRECTS[topic.toLowerCase()] || null;
  }

  /**
   * Check if AI response is appropriate
   */
  checkAIResponse(response: string): SafetyCheckResult {
    // AI responses should already be safe, but double-check
    const flaggedCategories: string[] = [];
    let severity: SafetyCheckResult['severity'] = 'none';

    // Check for any personal information in response
    for (const pattern of PERSONAL_INFO_PATTERNS) {
      if (pattern.test(response)) {
        flaggedCategories.push('personal_info_leak');
        severity = 'high';
      }
    }

    // Check response length (prevent overwhelming content)
    if (response.length > 5000) {
      flaggedCategories.push('content_too_long');
      severity = 'low';
    }

    return {
      isSafe: severity === 'none' || severity === 'low',
      flaggedCategories,
      severity,
    };
  }

  /**
   * Get age-appropriate language complexity guidance
   */
  getLanguageGuidance(): string {
    switch (this.config.ageGroup) {
      case 'elementary':
        return 'Use simple words, short sentences, and lots of encouragement. Avoid complex vocabulary.';
      case 'middle_school':
        return 'Use clear explanations with some academic vocabulary. Include engaging examples.';
      case 'high_school':
        return 'Use appropriate academic language. Challenge students while remaining accessible.';
      case 'adult':
        return 'Use full academic vocabulary and complex concepts as appropriate.';
      default:
        return 'Use clear, educational language appropriate for the student.';
    }
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<SafetyConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Reset warning count (e.g., for new session)
   */
  resetSession(): void {
    this.warningCount = 0;
    this.sessionBlocked = false;
  }

  /**
   * Get current session status
   */
  getSessionStatus(): { warningCount: number; isBlocked: boolean } {
    return {
      warningCount: this.warningCount,
      isBlocked: this.sessionBlocked,
    };
  }

  private escalateSeverity(
    current: SafetyCheckResult['severity'],
    proposed: SafetyCheckResult['severity']
  ): SafetyCheckResult['severity'] {
    const levels = { none: 0, low: 1, medium: 2, high: 3 };
    return levels[proposed] > levels[current] ? proposed : current;
  }

  private generateMessage(categories: string[], severity: SafetyCheckResult['severity']): string {
    if (severity === 'none') return '';

    if (categories.includes('personal_info')) {
      return "For your safety, please don't share personal information like phone numbers or addresses.";
    }

    if (categories.some(c => c.startsWith('topic_'))) {
      const topic = categories.find(c => c.startsWith('topic_'))?.replace('topic_', '');
      if (topic) {
        return this.getTopicRedirect(topic) || "Let's keep our discussion focused on learning!";
      }
    }

    if (categories.includes('mild_language')) {
      return "Let's use respectful language in our learning environment.";
    }

    return "Let's keep our conversation focused on learning!";
  }
}

// Singleton instance
export const contentSafetyService = new ContentSafetyService();

export default ContentSafetyService;
