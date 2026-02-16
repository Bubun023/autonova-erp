# AutoNova ERP - Architecture Overview

## Current System Architecture (Phase 2 - Week 4)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT/API CONSUMER                          │
│                    (Postman, curl, Frontend App)                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/HTTPS
                             │ JSON Requests
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FLASK APPLICATION                           │
│                         (app.py - Port 5000)                         │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    Middleware Layer                         │    │
│  │  • Flask-CORS (Cross-Origin Resource Sharing)              │    │
│  │  • Flask-JWT-Extended (Token Management)                   │    │
│  │  • Flask-Bcrypt (Password Hashing)                         │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    API Endpoints (Blueprints)               │    │
│  │                                                              │    │
│  │  ┌─────────────────────────────────────────────────────┐  │    │
│  │  │  /api/auth/*          (routes/auth.py)              │  │    │
│  │  │  • POST /register     - Register user               │  │    │
│  │  │  • POST /login        - Login & get tokens          │  │    │
│  │  │  • POST /refresh      - Refresh access token        │  │    │
│  │  │  • GET  /me           - Get current user            │  │    │
│  │  └─────────────────────────────────────────────────────┘  │    │
│  │                                                              │    │
│  │  ┌─────────────────────────────────────────────────────┐  │    │
│  │  │  /api/customers/*    (routes/customers.py)          │  │    │
│  │  │  • GET    /           - List customers              │  │    │
│  │  │  • GET    /{id}       - Get customer                │  │    │
│  │  │  • POST   /           - Create customer             │  │    │
│  │  │  • PUT    /{id}       - Update customer             │  │    │
│  │  │  • DELETE /{id}       - Delete customer             │  │    │
│  │  └─────────────────────────────────────────────────────┘  │    │
│  │                                                              │    │
│  │  ┌─────────────────────────────────────────────────────┐  │    │
│  │  │  /api/vehicles/*     (routes/vehicles.py)           │  │    │
│  │  │  • GET    /           - List vehicles               │  │    │
│  │  │  • GET    /{id}       - Get vehicle                 │  │    │
│  │  │  • POST   /           - Create vehicle              │  │    │
│  │  │  • PUT    /{id}       - Update vehicle              │  │    │
│  │  │  • DELETE /{id}       - Delete vehicle              │  │    │
│  │  └─────────────────────────────────────────────────────┘  │    │
│  │                                                              │    │
│  │  ┌─────────────────────────────────────────────────────┐  │    │
│  │  │  /health             (app.py)                        │  │    │
│  │  │  • GET /health        - Health check                │  │    │
│  │  └─────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              Authorization & Access Control                 │    │
│  │                     (utils.py)                              │    │
│  │  • @role_required decorator                                │    │
│  │  • get_current_user() helper                              │    │
│  └────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA ACCESS LAYER                             │
│                   Flask-SQLAlchemy (models.py)                       │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │    Role      │  │     User     │  │   Customer   │             │
│  │              │  │              │  │              │             │
│  │ • id         │  │ • id         │  │ • id         │             │
│  │ • name       │◄─┤ • username   │  │ • first_name │             │
│  │ • description│  │ • email      │  │ • last_name  │             │
│  │              │  │ • password   │  │ • email      │             │
│  │              │  │ • first_name │  │ • phone      │             │
│  │              │  │ • last_name  │  │ • address    │             │
│  │              │  │ • role_id    │  │              │             │
│  └──────────────┘  └──────────────┘  └──────┬───────┘             │
│                                               │                      │
│                                               │ 1:N                  │
│                                               ▼                      │
│                                      ┌──────────────┐               │
│                                      │   Vehicle    │               │
│                                      │              │               │
│                                      │ • id         │               │
│                                      │ • customer_id│               │
│                                      │ • make       │               │
│                                      │ • model      │               │
│                                      │ • year       │               │
│                                      │ • vin        │               │
│                                      │ • license_pl │               │
│                                      │ • color      │               │
│                                      │ • mileage    │               │
│                                      └──────────────┘               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                               │
│                    SQLite (autonova.db)                              │
│                 (Production: PostgreSQL/MySQL)                       │
│                                                                       │
│  Managed by: Flask-Migrate (Alembic)                                │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: Create Customer with Vehicle

```
1. CLIENT sends POST request to /api/customers
   ├─ Headers: Authorization: ******
   └─ Body: { "first_name": "John", "last_name": "Doe", "phone": "555-1234" }

2. FLASK receives request
   └─ JWT middleware validates token
      └─ Extracts user_id from token

3. AUTHORIZATION checks role
   └─ @role_required('admin', 'manager', 'receptionist')
      └─ Verifies user has required role
         └─ ✅ Pass: Continue
            ❌ Fail: Return 403 Forbidden

4. ROUTE HANDLER (routes/customers.py)
   ├─ Validates required fields
   ├─ Checks email uniqueness
   └─ Creates Customer object

5. DATABASE LAYER
   ├─ SQLAlchemy creates INSERT query
   ├─ Commits transaction
   └─ Returns customer with ID

6. RESPONSE sent to client
   └─ { "customer": { "id": 1, "first_name": "John", ... } }
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      Security Features                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Authentication                                    │
│  • JWT tokens (access: 1h, refresh: 30d)                   │
│  • Bcrypt password hashing                                 │
│  • Token expiration & refresh                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Authorization                                     │
│  • Role-based access control (RBAC)                        │
│  • 5 roles with different permissions                      │
│  • Decorator-based endpoint protection                     │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Input Validation                                  │
│  • Required field validation                               │
│  • Unique constraint checking                              │
│  • Data type validation                                    │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Error Handling                                    │
│  • 400 Bad Request (validation errors)                     │
│  • 401 Unauthorized (missing/invalid token)                │
│  • 403 Forbidden (insufficient permissions)                │
│  • 404 Not Found (resource doesn't exist)                  │
│  • 500 Internal Server Error (server issues)               │
└─────────────────────────────────────────────────────────────┘
```

## Current Feature Set

### ✅ Implemented
- User authentication (JWT)
- User registration & login
- Password hashing (bcrypt)
- Role-based access control
- Customer management (CRUD)
- Vehicle management (CRUD)
- Pagination for list endpoints
- Relationship loading (customers with vehicles, vehicles with owners)
- Database migrations
- Comprehensive test suite
- API documentation

### 🚧 Not Yet Implemented (Future Phases)
- Service/Repair orders
- Parts inventory
- Invoice generation
- Payment processing
- Appointment scheduling
- Email notifications
- File uploads (documents, photos)
- Reporting & analytics
- Frontend UI
- Multi-tenancy
- Audit logging

## Technology Stack

**Backend Framework:** Flask 2.0.1  
**Database ORM:** SQLAlchemy 1.4.46  
**Database:** SQLite (dev) → PostgreSQL (production)  
**Authentication:** JWT (Flask-JWT-Extended)  
**Password Security:** Bcrypt (Flask-Bcrypt)  
**Migrations:** Alembic (Flask-Migrate)  
**CORS:** Flask-CORS  
**Testing:** Custom test suite (test_api.py)  
**Security:** CodeQL scanning  

## Performance Characteristics

- **Pagination:** Default 20 items/page, max 100
- **Token Expiry:** Access 1h, Refresh 30d  
- **Password Hashing:** Bcrypt (default rounds)
- **Database:** SQLite (suitable for < 10K records, then migrate to PostgreSQL)

## Deployment Readiness

| Criteria | Status | Notes |
|----------|--------|-------|
| Code Complete | ✅ | All Phase 2 Week 4 requirements met |
| Tests Passing | ✅ | 9/9 tests pass |
| Security Scan | ✅ | 0 CodeQL alerts |
| Documentation | ✅ | README, STATUS, Architecture |
| Error Handling | ✅ | All HTTP codes covered |
| Input Validation | ✅ | All endpoints validate input |
| Production DB | ⚠️  | Need to migrate from SQLite to PostgreSQL |
| HTTPS/SSL | ⚠️  | Need to configure in production |
| Monitoring | ⚠️  | Need to add logging/monitoring |
| Backups | ⚠️  | Need to implement DB backup strategy |
