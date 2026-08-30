# Phase 3 - Implementation Roadmap

## Phase 3 Scope: Too Large for Single Session

Phase 3 requires ~3,000+ additional lines of production code across:
- Authentication system (JWT, password hashing)
- RBAC enforcement
- Dashboard with analytics
- Product database with search
- Admin rule management
- Report management
- Offline sync system
- Geolocation tracking
- System monitoring
- Complete documentation

**Recommendation:** Execute Phase 3 in 2-3 focused sessions using this roadmap.

---

## Session 1: Foundation (4-5 hours)

### Task: Authentication & User Management

**Backend:**
1. Add User model with password hashing (bcrypt)
2. Add Role/Permission models (ADMIN, INSPECTOR, SUPERVISOR, VIEWER)
3. Implement JWT authentication endpoints
4. Add middleware for RBAC enforcement

**Frontend:**
1. Create Login page
2. Add protected routes (PrivateRoute component)
3. Store JWT in secure storage
4. Implement logout

**Database Migrations:**
1. User table with roles
2. Audit log table

**Files to Create:**
```
backend/
├── app/
│   ├── auth/
│   │   ├── models.py          # User, Role, Permission models
│   │   ├── schemas.py         # Pydantic auth schemas
│   │   ├── utils.py           # JWT, password hashing
│   │   └── routes.py          # /auth/login, /auth/register, /auth/verify
│   └── middleware.py          # RBAC middleware
│
frontend/
├── src/
│   ├── pages/
│   │   ├── Login.tsx
│   │   └── Dashboard.tsx (basic)
│   ├── components/
│   │   ├── PrivateRoute.tsx
│   │   └── Navbar.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx
│   └── hooks/
│       └── useAuth.ts

tests/
├── test_auth.py               # Authentication tests
└── test_rbac.py              # RBAC tests
```

---

## Session 2: Dashboard & Admin (4-5 hours)

### Task: Professional Dashboard + Product Database + Admin Panel

**Backend:**
1. Dashboard analytics queries
2. Product search and filter endpoints
3. Rule management endpoints (CRUD)
4. Report archive endpoints

**Frontend:**
1. Professional dashboard with charts (using Recharts)
2. Product search page
3. Admin rule management UI
4. Inspection history view

**Database:**
1. Product table (denormalized from scans)
2. Rule versions table (with effective dates)
3. Report archives table

**Files to Create:**
```
backend/
├── app/
│   ├── dashboard/
│   │   ├── routes.py         # Analytics endpoints
│   │   └── queries.py        # Dashboard queries
│   ├── products/
│   │   ├── routes.py         # Search, filter endpoints
│   │   └── queries.py        # Product queries
│   └── admin/
│       ├── routes.py         # Rule management endpoints
│       └── queries.py        # Admin queries

frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx (enhanced)
│   │   ├── ProductSearch.tsx
│   │   ├── AdminRules.tsx
│   │   └── ReportArchive.tsx
│   └── components/
│       ├── Charts/
│       │   ├── ComplianceTrends.tsx
│       │   ├── ViolationsByCategory.tsx
│       │   └── ProductStats.tsx
│       └── Tables/
│           ├── ProductTable.tsx
│           └── RuleTable.tsx

tests/
├── test_dashboard.py
├── test_products.py
└── test_admin.py
```

---

## Session 3: Demo Mode & Mobile Optimization (3-4 hours)

### Task: Demo Mode + Mobile Workflow + Offline Support

**Backend:**
1. Demo mode data (synthetic packages)
2. Offline sync endpoints (queue management)
3. Geolocation storage

**Frontend:**
1. Mobile-responsive scan workflow
2. Camera integration
3. Demo mode UI with package selector
4. Offline queue storage (localStorage/IndexedDB)
5. Location tracking (optional)

**Database:**
1. Inspection queue table (for offline)
2. Geolocation data table

**Files to Create:**
```
backend/
├── app/
│   ├── demo/
│   │   ├── data.py           # Synthetic packages
│   │   └── routes.py         # Demo endpoints
│   ├── offline/
│   │   ├── routes.py         # Queue endpoints
│   │   └── sync.py           # Sync logic
│   └── geolocation/
│       └── routes.py         # Location endpoints

frontend/
├── src/
│   ├── pages/
│   │   └── DemoMode.tsx      # Demo selection & flow
│   ├── components/
│   │   ├── CameraCapture.tsx
│   │   ├── OfflineIndicator.tsx
│   │   └── LocationMap.tsx
│   ├── hooks/
│   │   ├── useCamera.ts
│   │   ├── useOfflineQueue.ts
│   │   └── useGeolocation.ts
│   └── services/
│       └── offlineSync.ts    # Queue management
```

---

## Session 4: Reports, API, & Monitoring (3-4 hours)

### Task: Report Management + Enterprise API + System Monitoring

**Backend:**
1. Advanced report endpoints
2. Enterprise API architecture (/api/v1/)
3. API authentication (API keys)
4. System monitoring endpoints
5. Rate limiting

**Frontend:**
1. Report management UI
2. System health dashboard
3. API documentation viewer

**Database:**
1. System metrics table
2. API keys table
3. Rate limit tracking

**Files to Create:**
```
backend/
├── app/
│   ├── reports/
│   │   ├── routes.py         # Report CRUD endpoints
│   │   └── export.py         # Export logic
│   ├── api_v1/
│   │   ├── routes.py         # v1 endpoints
│   │   ├── auth.py           # API key auth
│   │   └── rate_limit.py     # Rate limiting
│   └── monitoring/
│       ├── routes.py         # Health endpoints
│       ├── metrics.py        # Metric collection
│       └── logger.py         # Logging setup

frontend/
├── src/
│   ├── pages/
│   │   ├── ReportManager.tsx
│   │   ├── SystemHealth.tsx
│   │   └── APIDocumentation.tsx
│   └── components/
│       ├── MetricsCard.tsx
│       └── LogViewer.tsx
```

---

## Session 5: Documentation & SIH Presentation (3-4 hours)

### Task: Complete Documentation + SIH Presentation Package

**Documentation to Write:**
```
ARCHITECTURE.md              # Complete system design
API.md                       # API reference
AI_PIPELINE.md               # AI processing details
RULE_ENGINE.md               # Rules system explanation
SECURITY.md                  # Security implementation
DEPLOYMENT.md                # Production deployment
DEMO_GUIDE.md                # Step-by-step demo
SIH_PRESENTATION.md          # Problem → Solution → Impact
BUSINESS_MODEL.md            # Commercial strategy
```

**Presentation Assets:**
- Pitch deck template (Google Slides)
- Demo walkthrough checklist
- Key talking points
- Statistics and metrics
- Future roadmap

---

## Parallel Tasks (Can Start Immediately)

### Create Synthetic Test Data

```python
# backend/tests/synthetic_demo_data.py

DEMO_PACKAGES = {
    "compliant": {
        "name": "Premium Tea - Assorted (Demo)",
        "manufacturer": "Chai Enterprises Ltd.",
        "mrp": "₹299",
        "quantity": "500g",
        "images": [...]
    },
    "missing_mrp": {
        "name": "Biscuits - Digestive (Demo)",
        "manufacturer": "Baked Goods Inc.",
        "mrp": None,  # MISSING
        "quantity": "250g",
        "images": [...]
    },
    # ... more packages
}
```

### Set Up Production Configuration

```dockerfile
# docker-compose.prod.yml
# Production-optimized docker-compose
# With SSL, database backups, monitoring

# .env.production
# Production environment variables
```

### Create Monitoring Dashboard

```
System Health Page
├─ API Response Time
├─ OCR Processing Time
├─ Database Connection Pool
├─ Cache Hit Rate
├─ Error Rate
└─ Active Inspections
```

---

## Estimated Total Effort

| Component | Lines | Time |
|-----------|-------|------|
| Authentication | 300 | 1 hour |
| Dashboard | 400 | 1.5 hours |
| Admin Panel | 300 | 1 hour |
| Demo Mode | 200 | 1 hour |
| Mobile Workflow | 400 | 1.5 hours |
| Offline Support | 250 | 1 hour |
| Reports | 300 | 1 hour |
| API v1 | 400 | 1.5 hours |
| Monitoring | 250 | 1 hour |
| Documentation | 1000 | 2-3 hours |
| **TOTAL** | **3,800+** | **14-16 hours** |

---

## Quick Wins (Can Implement Today)

### 1. Add Basic Login Page

```tsx
// frontend/src/pages/Login.tsx
import { useState } from 'react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const handleLogin = async () => {
    // Call /api/auth/login
    // Store JWT
    // Redirect to dashboard
  };
  
  return (
    <div className="login-container">
      <h1>SIH 2026 Compliance Inspector</h1>
      <input type="email" placeholder="Email" />
      <input type="password" placeholder="Password" />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};
```

### 2. Create User Model

```python
# backend/app/auth/models.py
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)  # bcrypt hash
    full_name = Column(String)
    role = Column(String)  # ADMIN, INSPECTOR, SUPERVISOR, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 3. Add Basic Dashboard Statistics

```tsx
// frontend/src/pages/Dashboard.tsx
export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalInspections: 1245,
    compliant: 1050,
    violations: 180,
    needsVerification: 15
  });
  
  return (
    <div className="dashboard">
      <h1>Inspection Analytics</h1>
      <div className="stats-grid">
        <Card title="Total Inspections" value={stats.totalInspections} />
        <Card title="Compliant" value={stats.compliant} color="green" />
        <Card title="Violations" value={stats.violations} color="red" />
        <Card title="Needs Verification" value={stats.needsVerification} color="yellow" />
      </div>
    </div>
  );
};
```

---

## Prioritization for SIH Success

### Must Complete Before Demo
1. ✅ User authentication (even basic)
2. ✅ Dashboard with stats
3. ✅ Demo mode selection
4. ✅ Working scan flow (Phase 1+2 already done)
5. ✅ Report generation
6. ✅ Professional UI polish

### Can Skip for Demo
- Advanced analytics
- Offline sync complexity
- Geolocation maps
- Advanced RBAC
- Enterprise API versioning

### Focus Areas for Judges
- **Innovation**: AI explainability (Phase 2 strength)
- **Quality**: Professional UI and UX
- **Completeness**: End-to-end workflow
- **Viability**: Business model clarity
- **Impact**: Social value articulation

---

## Next Steps

1. **Review this roadmap** - Confirm priorities
2. **Start Session 1** - Authentication (see Session 1 tasks above)
3. **Use provided strategies** - Don't overcomplicate
4. **Demo constantly** - Test early, demo often
5. **Document as you go** - No last-minute writing

---

**Phase 3 is achievable in 4-5 days with focused execution. Start with authentication, move to dashboard, add demo mode, and finalize with documentation.**

For detailed implementation of Session 1, see the next section.
