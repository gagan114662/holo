# HoloTutor Production Implementation Plan

## Current State: Demo/Prototype
## Target State: Production-Ready Product Superior to 2wai.ai

---

## PHASE 1: REAL AVATAR SYSTEM (Priority: CRITICAL)

### Problem
Current "lip-sync" is a brown oval (`rgba(139, 69, 19, 0.6)`) that scales up/down.
This is NOT comparable to 2wai's photorealistic avatars.

### Solution Options (Choose One)

#### Option A: HeyGen API Integration (Recommended - Fastest)
```
Cost: ~$0.10/minute of video
Quality: Photorealistic
Implementation: 3-5 days
```

**Files to Create:**
- `src/services/HeyGenService.ts` - API integration
- `src/components/avatar/HeyGenAvatar.tsx` - Video player component

**Implementation:**
```typescript
// HeyGenService.ts
class HeyGenService {
  private apiKey: string;

  async createTalkingVideo(text: string, avatarId: string): Promise<string> {
    const response = await fetch('https://api.heygen.com/v2/video/generate', {
      method: 'POST',
      headers: {
        'X-Api-Key': this.apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        video_inputs: [{
          character: { type: 'avatar', avatar_id: avatarId },
          voice: { type: 'text', input_text: text }
        }]
      })
    });
    return response.json();
  }

  async getVideoStatus(videoId: string): Promise<VideoStatus> { ... }
  async streamRealtime(avatarId: string): Promise<WebSocket> { ... }
}
```

#### Option B: D-ID Streaming (Already Partially Implemented)
```
Cost: ~$0.05/minute
Quality: Good
Implementation: Already exists, needs activation
```

**Fix Required:**
1. Add `REACT_APP_DID_API_KEY` to `.env`
2. Test and debug existing `DIDService.ts`
3. Replace CSS fallback with proper loading state

#### Option C: Simli.ai (Cheapest Real-time)
```
Cost: ~$0.02/minute
Quality: Good real-time
Implementation: 2-3 days
```

### Action Items:
- [ ] Choose API provider (recommend HeyGen for quality)
- [ ] Get API keys and add to `.env`
- [ ] Implement streaming for real-time conversation
- [ ] Remove CSS oval lip-sync fallback entirely
- [ ] Add proper loading/buffering states

---

## PHASE 2: REAL ANSWER GRADING SYSTEM (Priority: CRITICAL)

### Problem
Current grading is just `string.includes()` - no semantic understanding.

### Solution: Multi-Layer Grading System

**Files to Create:**
- `src/services/GradingService.ts`
- Backend: `backend/grading_api.py`

**Implementation:**

```typescript
// GradingService.ts
interface GradingResult {
  isCorrect: boolean;
  score: number; // 0-100
  feedback: string;
  explanation: string;
  hints: string[];
  partialCredit: number;
}

class GradingService {
  // Layer 1: Exact match (fast)
  private exactMatch(answer: string, correct: string): boolean {
    return this.normalize(answer) === this.normalize(correct);
  }

  // Layer 2: Numeric tolerance (for math)
  private numericMatch(answer: string, correct: string, tolerance: number = 0.01): boolean {
    const ansNum = parseFloat(answer);
    const corNum = parseFloat(correct);
    return Math.abs(ansNum - corNum) <= tolerance * Math.abs(corNum);
  }

  // Layer 3: Semantic similarity (for open-ended)
  async semanticGrade(answer: string, rubric: string, maxPoints: number): Promise<GradingResult> {
    const response = await fetch('/api/grade', {
      method: 'POST',
      body: JSON.stringify({
        student_answer: answer,
        rubric: rubric,
        max_points: maxPoints
      })
    });
    return response.json();
  }

  // Layer 4: Code execution (for programming)
  async executeCode(code: string, testCases: TestCase[]): Promise<GradingResult> {
    // Use sandboxed execution (Pyodide for Python, etc.)
  }
}
```

**Backend Grading API:**
```python
# backend/grading_api.py
from fastapi import FastAPI
from anthropic import Anthropic

app = FastAPI()
client = Anthropic()

@app.post("/api/grade")
async def grade_answer(request: GradeRequest):
    prompt = f"""
    Grade this student answer against the rubric.

    Question: {request.question}
    Correct Answer: {request.correct_answer}
    Student Answer: {request.student_answer}
    Rubric: {request.rubric}

    Return JSON with:
    - score (0-100)
    - is_correct (boolean)
    - feedback (encouraging, specific)
    - explanation (why this score)
    - partial_credit_breakdown (if applicable)
    """

    response = client.messages.create(
        model="claude-3-haiku-20240307",  # Fast and cheap
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_grading_response(response)
```

### Action Items:
- [ ] Create `GradingService.ts` with multi-layer grading
- [ ] Create backend grading API
- [ ] Add numeric tolerance for math problems
- [ ] Add code execution sandbox for programming
- [ ] Remove simple `includes()` grading

---

## PHASE 3: REAL CURRICULUM DATABASE (Priority: HIGH)

### Problem
Only 19 hardcoded questions total (3 per subject).

### Solution: Scalable Question Database

**Database Schema:**
```sql
-- PostgreSQL schema
CREATE TABLE subjects (
  id UUID PRIMARY KEY,
  name VARCHAR(100),
  description TEXT,
  icon VARCHAR(50),
  parent_id UUID REFERENCES subjects(id)
);

CREATE TABLE skills (
  id UUID PRIMARY KEY,
  subject_id UUID REFERENCES subjects(id),
  name VARCHAR(200),
  description TEXT,
  prerequisites UUID[] -- Array of skill IDs
);

CREATE TABLE questions (
  id UUID PRIMARY KEY,
  skill_id UUID REFERENCES skills(id),
  content TEXT NOT NULL,
  question_type VARCHAR(50), -- multiple_choice, free_text, numeric, code
  difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
  correct_answer TEXT,
  explanation TEXT,
  hints TEXT[],
  options JSONB, -- For multiple choice
  rubric TEXT, -- For open-ended grading
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE question_attempts (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  question_id UUID REFERENCES questions(id),
  answer TEXT,
  is_correct BOOLEAN,
  score INTEGER,
  time_spent_seconds INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Question Generation Script:**
```python
# scripts/generate_curriculum.py
import anthropic
import json

client = anthropic.Anthropic()

SUBJECTS = {
    "physics": ["mechanics", "thermodynamics", "electromagnetism", "optics", "modern_physics"],
    "mathematics": ["algebra", "geometry", "calculus", "statistics", "number_theory"],
    "chemistry": ["atomic_structure", "bonding", "reactions", "organic", "biochemistry"],
    "biology": ["cells", "genetics", "evolution", "ecology", "human_body"],
    "literature": ["poetry", "prose", "drama", "rhetoric", "literary_analysis"],
    "history": ["ancient", "medieval", "modern", "us_history", "world_history"],
    "computer_science": ["programming", "algorithms", "data_structures", "databases", "networking"]
}

async def generate_questions(subject: str, topic: str, count: int = 50):
    prompt = f"""
    Generate {count} educational questions for {subject} - {topic}.

    For each question provide:
    1. question_text
    2. difficulty (1-5)
    3. correct_answer
    4. explanation (why this is correct)
    5. hints (array of 3 progressive hints)
    6. common_mistakes (what students often get wrong)

    Mix question types: 40% multiple choice, 40% free text, 20% numeric
    Ensure difficulty distribution: 20% easy, 40% medium, 30% hard, 10% expert

    Return as JSON array.
    """

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)

# Generate 50 questions per topic = 50 * 5 topics * 7 subjects = 1,750 questions
```

### Action Items:
- [ ] Set up PostgreSQL database
- [ ] Create database schema
- [ ] Write question generation script
- [ ] Generate 1,500+ questions across all subjects
- [ ] Create API endpoints for question retrieval
- [ ] Replace hardcoded `SAMPLE_QUESTIONS` with database queries
- [ ] Add spaced repetition algorithm for question selection

---

## PHASE 4: REAL AUTHENTICATION (Priority: HIGH)

### Problem
Currently using auto-generated localStorage IDs - not real auth.

### Solution: Firebase Authentication

**Files to Create:**
- `src/services/AuthService.ts`
- `src/contexts/AuthContext.tsx`
- `src/components/auth/LoginPage.tsx`
- `src/components/auth/SignupPage.tsx`

**Implementation:**

```typescript
// src/services/AuthService.ts
import { initializeApp } from 'firebase/app';
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  onAuthStateChanged,
  User
} from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

class AuthService {
  async signUp(email: string, password: string, role: 'student' | 'teacher'): Promise<User> {
    const credential = await createUserWithEmailAndPassword(auth, email, password);
    await this.createUserProfile(credential.user.uid, { email, role });
    return credential.user;
  }

  async signIn(email: string, password: string): Promise<User> {
    const credential = await signInWithEmailAndPassword(auth, email, password);
    return credential.user;
  }

  async signInWithGoogle(): Promise<User> {
    const provider = new GoogleAuthProvider();
    const credential = await signInWithPopup(auth, provider);
    return credential.user;
  }

  async signOut(): Promise<void> {
    await signOut(auth);
  }

  onAuthStateChanged(callback: (user: User | null) => void): () => void {
    return onAuthStateChanged(auth, callback);
  }

  private async createUserProfile(uid: string, data: UserProfile): Promise<void> {
    await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify({ uid, ...data })
    });
  }
}

export const authService = new AuthService();
```

```typescript
// src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from 'firebase/auth';
import { authService } from '../services/AuthService';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, role: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = authService.onAuthStateChanged((user) => {
      setUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  // ... implement methods

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Action Items:
- [ ] Create Firebase project
- [ ] Add Firebase config to `.env`
- [ ] Implement `AuthService.ts`
- [ ] Implement `AuthContext.tsx`
- [ ] Create Login/Signup pages
- [ ] Add protected routes
- [ ] Remove localStorage-based user ID generation

---

## PHASE 5: REAL BACKEND & DATABASE (Priority: HIGH)

### Problem
No real backend - everything is localStorage or mock data.

### Solution: FastAPI + PostgreSQL + Redis

**Project Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── question.py
│   │   ├── session.py
│   │   └── progress.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── questions.py
│   │   ├── sessions.py
│   │   ├── progress.py
│   │   └── teachers.py
│   ├── services/
│   │   ├── grading.py
│   │   ├── adaptive.py
│   │   └── analytics.py
│   └── utils/
├── alembic/  # Database migrations
├── tests/
├── requirements.txt
└── Dockerfile
```

**Main API:**
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HoloTutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://holotutor.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(questions_router, prefix="/api/questions")
app.include_router(sessions_router, prefix="/api/sessions")
app.include_router(progress_router, prefix="/api/progress")
app.include_router(teachers_router, prefix="/api/teachers")
```

### Action Items:
- [ ] Set up FastAPI backend
- [ ] Set up PostgreSQL database
- [ ] Set up Redis for caching/sessions
- [ ] Create database models with SQLAlchemy
- [ ] Create API endpoints
- [ ] Set up Alembic migrations
- [ ] Deploy to cloud (Railway/Render/AWS)

---

## PHASE 6: REAL TEACHER DASHBOARD (Priority: MEDIUM)

### Problem
5 fake students hardcoded, mixed with 1 real user.

### Solution: Real Multi-User System

**Remove from TeacherDashboard.tsx:**
```typescript
// DELETE THIS - lines 80-86
const sampleStudents: Student[] = [
  { id: '1', name: 'Emma Johnson', ... },
  { id: '2', name: 'Liam Smith', ... },
  // ... all fake students
];
```

**Replace with Real API:**
```typescript
// TeacherDashboard.tsx
const TeacherDashboard: React.FC<Props> = ({ isOpen, onClose }) => {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (isOpen && user) {
      fetchClassStudents();
    }
  }, [isOpen, user]);

  const fetchClassStudents = async () => {
    setLoading(true);
    try {
      // Get teacher's classes
      const classes = await fetch(`/api/teachers/${user.uid}/classes`);
      const classData = await classes.json();

      // Get students for each class
      const allStudents: Student[] = [];
      for (const cls of classData) {
        const studentsRes = await fetch(`/api/classes/${cls.id}/students`);
        const students = await studentsRes.json();
        allStudents.push(...students);
      }

      setStudents(allStudents);
    } catch (error) {
      console.error('Failed to fetch students:', error);
    } finally {
      setLoading(false);
    }
  };

  // Real-time updates via WebSocket
  useEffect(() => {
    const ws = new WebSocket(`wss://api.holotutor.app/ws/class/${classId}`);
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      handleStudentUpdate(update);
    };
    return () => ws.close();
  }, [classId]);

  // ... rest of component
};
```

**Backend API:**
```python
# backend/app/routers/teachers.py
@router.get("/teachers/{teacher_id}/classes")
async def get_teacher_classes(teacher_id: str, db: Session = Depends(get_db)):
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    return classes

@router.get("/classes/{class_id}/students")
async def get_class_students(class_id: str, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
    students = []
    for enrollment in enrollments:
        student = db.query(User).filter(User.id == enrollment.student_id).first()
        progress = get_student_progress(student.id)
        students.append({
            "id": student.id,
            "name": student.name,
            "avatar": student.avatar_url,
            "progress": progress,
            "status": get_student_status(student.id),
            "current_session": get_current_session(student.id)
        })
    return students

@router.websocket("/ws/class/{class_id}")
async def class_websocket(websocket: WebSocket, class_id: str):
    await websocket.accept()
    # Stream real-time student updates
```

### Action Items:
- [ ] Remove ALL hardcoded sample students
- [ ] Remove ALL hardcoded sample activities
- [ ] Create class/enrollment database models
- [ ] Create teacher API endpoints
- [ ] Implement WebSocket for real-time updates
- [ ] Add class creation/management UI

---

## PHASE 7: DEPLOYMENT & INFRASTRUCTURE

### Architecture:
```
┌─────────────────────────────────────────────────────────────┐
│                        CLOUDFLARE                           │
│                     (CDN + DDoS Protection)                 │
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
     ┌────────▼────────┐           ┌─────────▼─────────┐
     │   VERCEL        │           │   RAILWAY         │
     │   (Frontend)    │           │   (Backend API)   │
     │                 │           │                   │
     │  React App      │◄─────────►│  FastAPI          │
     │  Static Assets  │   REST    │  WebSockets       │
     └─────────────────┘   API     └────────┬──────────┘
                                            │
                         ┌──────────────────┼──────────────────┐
                         │                  │                  │
               ┌─────────▼──────┐  ┌────────▼───────┐  ┌──────▼───────┐
               │   SUPABASE     │  │     REDIS      │  │   AWS S3     │
               │   (PostgreSQL) │  │   (Upstash)    │  │   (Media)    │
               │                │  │                │  │              │
               │  Users         │  │  Sessions      │  │  Avatars     │
               │  Questions     │  │  Cache         │  │  Audio       │
               │  Progress      │  │  Pub/Sub       │  │  Videos      │
               └────────────────┘  └────────────────┘  └──────────────┘
```

### Environment Variables:
```bash
# .env.production
# Firebase
REACT_APP_FIREBASE_API_KEY=xxx
REACT_APP_FIREBASE_AUTH_DOMAIN=xxx
REACT_APP_FIREBASE_PROJECT_ID=xxx

# Avatar API (choose one)
REACT_APP_HEYGEN_API_KEY=xxx
# or
REACT_APP_DID_API_KEY=xxx

# Backend
REACT_APP_API_URL=https://api.holotutor.app

# Database
DATABASE_URL=postgresql://xxx

# Redis
REDIS_URL=redis://xxx

# AI
ANTHROPIC_API_KEY=xxx
OPENAI_API_KEY=xxx
```

### Action Items:
- [ ] Set up Vercel for frontend
- [ ] Set up Railway for backend
- [ ] Set up Supabase for database
- [ ] Set up Upstash for Redis
- [ ] Set up AWS S3 for media
- [ ] Configure CI/CD pipelines
- [ ] Set up monitoring (Sentry, LogRocket)

---

## IMPLEMENTATION TIMELINE

### Week 1: Foundation
- [ ] Day 1-2: Set up backend (FastAPI + PostgreSQL)
- [ ] Day 3-4: Implement Firebase Auth
- [ ] Day 5-7: Create database schema and basic API

### Week 2: Core Features
- [ ] Day 1-3: Implement real grading system
- [ ] Day 4-5: Generate curriculum (1,500+ questions)
- [ ] Day 6-7: Integrate avatar API (HeyGen/D-ID)

### Week 3: Teacher Features
- [ ] Day 1-3: Real teacher dashboard with live data
- [ ] Day 4-5: Class management system
- [ ] Day 6-7: Real-time WebSocket updates

### Week 4: Polish & Deploy
- [ ] Day 1-2: Remove all mock/placeholder code
- [ ] Day 3-4: Testing and bug fixes
- [ ] Day 5-6: Deploy to production
- [ ] Day 7: Documentation and handoff

---

## FILES TO DELETE/MODIFY

### Delete Entirely:
- Remove `SAMPLE_QUESTIONS` from `QuestionDisplay.tsx`
- Remove `sampleStudents` from `TeacherDashboard.tsx`
- Remove `sampleActivities` from `TeacherDashboard.tsx`
- Remove `BUILT_IN_AVATARS` fallback (after avatar API works)

### Modify Heavily:
- `src/services/StorageService.ts` → Replace localStorage with API calls
- `src/components/avatar/VideoAvatar.tsx` → Remove CSS lip-sync fallback
- `src/components/answer-input/AnswerInput.tsx` → Use real grading API
- `src/contexts/AvatarContext.tsx` → Remove offline fallback after API works

### Create New:
- `backend/` entire directory
- `src/services/AuthService.ts`
- `src/services/GradingService.ts`
- `src/services/HeyGenService.ts`
- `src/contexts/AuthContext.tsx`
- `src/components/auth/LoginPage.tsx`
- `src/components/auth/SignupPage.tsx`

---

## COST ESTIMATES (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| HeyGen API | ~$100-500 | Based on usage |
| Supabase (DB) | $25 | Pro plan |
| Railway (Backend) | $20 | Starter |
| Vercel (Frontend) | $0-20 | Free tier often enough |
| Redis (Upstash) | $10 | Pay per use |
| Firebase Auth | $0 | Free tier |
| Anthropic API | ~$50-200 | For grading |
| **Total** | **~$200-800/mo** | Scales with users |

---

## SUCCESS CRITERIA

### Must Have (MVP):
- [ ] Real authentication (email + Google)
- [ ] Avatar speaks with real lip-sync (HeyGen/D-ID)
- [ ] 500+ questions across 5 subjects
- [ ] Real grading with semantic understanding
- [ ] Progress persisted to real database
- [ ] Teacher can see REAL students (not fake)

### Should Have (V1):
- [ ] 1,500+ questions across 7 subjects
- [ ] Real-time class monitoring
- [ ] Student analytics dashboard
- [ ] Voice input (speech-to-text)
- [ ] Mobile responsive design

### Nice to Have (V2):
- [ ] AR mode
- [ ] Collaborative learning
- [ ] Parent portal
- [ ] Offline mode
- [ ] Custom avatar creation
