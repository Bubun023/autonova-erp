# AutoNova ERP Backend

Complete backend implementation for the AutoNova ERP system with JWT authentication, role-based access control, and RESTful APIs.

## Features

- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **Role-Based Access Control (RBAC)**: 5 user roles with granular permissions
  - Admin: Full system access
  - Manager: Elevated permissions for customer and vehicle management
  - Receptionist: Customer and vehicle management
  - Technician: View and update vehicles
  - Accountant: Limited access (future implementation)
- **Customer Management**: Complete CRUD operations with pagination
- **Vehicle Management**: Complete CRUD operations with customer relationships
- **Data Validation**: Email, password strength, and VIN format validation
- **Database Models**: SQLAlchemy models with relationships and cascade deletes
- **Production-Ready**: Security checks for production environment variables

## Tech Stack

- **Flask 2.3.0**: Web framework
- **Flask-SQLAlchemy 3.0.0**: ORM for database operations
- **Flask-JWT-Extended 4.4.4**: JWT token management
- **Flask-Bcrypt 1.0.1**: Password hashing
- **Flask-CORS 4.0.0**: Cross-origin resource sharing
- **Flask-Migrate 4.0.0**: Database migrations
- **SQLite**: Database (development)

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the `.env` file and update with your secrets:

```bash
cp .env .env.local
# Edit .env.local and set:
# - SECRET_KEY
# - JWT_SECRET_KEY
```

### 3. Initialize Database

Run the seed script to create tables and populate initial data:

```bash
python seed.py
```

This creates:
- 5 user roles (admin, manager, receptionist, technician, accountant)
- Default admin user (username: `admin`, password: `admin123`)

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### 5. Test the API

Run the comprehensive test suite:

```bash
python test_api.py
```

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info (requires JWT)

### Customers (`/api/customers`)

- `GET /api/customers` - List all customers (paginated)
- `GET /api/customers/<id>` - Get specific customer
- `POST /api/customers` - Create new customer
- `PUT /api/customers/<id>` - Update customer
- `DELETE /api/customers/<id>` - Delete customer (admin/manager only)

### Vehicles (`/api/vehicles`)

- `GET /api/vehicles` - List all vehicles (paginated, optional customer filter)
- `GET /api/vehicles/<id>` - Get specific vehicle
- `POST /api/vehicles` - Create new vehicle
- `PUT /api/vehicles/<id>` - Update vehicle
- `DELETE /api/vehicles/<id>` - Delete vehicle (admin/manager only)

### Health Check

- `GET /health` - Health check endpoint

## Default Credentials

**Username:** `admin`  
**Password:** `admin123`

⚠️ **Important:** Change the default admin password in production!

## Role-Based Access Control Matrix

| Endpoint | Admin | Manager | Receptionist | Technician | Accountant |
|----------|-------|---------|--------------|------------|------------|
| List customers | ✅ | ✅ | ✅ | ❌ | ❌ |
| View customer | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create customer | ✅ | ✅ | ✅ | ❌ | ❌ |
| Update customer | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete customer | ✅ | ✅ | ❌ | ❌ | ❌ |
| List vehicles | ✅ | ✅ | ✅ | ✅ | ❌ |
| View vehicle | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create vehicle | ✅ | ✅ | ✅ | ❌ | ❌ |
| Update vehicle | ✅ | ✅ | ✅ | ✅ | ❌ |
| Delete vehicle | ✅ | ✅ | ❌ | ❌ | ❌ |

## Example API Usage

### 1. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Create Customer

```bash
curl -X POST http://localhost:5000/api/customers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "555-0123",
    "address": "123 Main St"
  }'
```

### 3. Create Vehicle

```bash
curl -X POST http://localhost:5000/api/vehicles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "customer_id": 1,
    "make": "Toyota",
    "model": "Camry",
    "year": 2020,
    "vin": "1HGCM82633A123456",
    "license_plate": "ABC-1234",
    "color": "Silver",
    "mileage": 15000
  }'
```

## Data Validation

### Password Requirements
- Minimum 8 characters
- At least one letter
- At least one number

### Email Format
- Standard email format validation
- Example: `user@example.com`

### VIN Format
- Exactly 17 characters
- Alphanumeric only
- Excludes I, O, Q characters
- Example: `1HGCM82633A123456`

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Token expiration (1 hour for access, 30 days for refresh)
- Role-based access control
- Input validation for all endpoints
- Production environment variable validation
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration

## Database Schema

### Users
- id (PK)
- username (unique)
- email (unique)
- password_hash
- first_name
- last_name
- role_id (FK → Roles)
- is_active
- created_at
- updated_at

### Roles
- id (PK)
- name (unique)
- description
- created_at

### Customers
- id (PK)
- first_name
- last_name
- email
- phone
- address
- created_at
- updated_at

### Vehicles
- id (PK)
- customer_id (FK → Customers)
- make
- model
- year
- vin (unique)
- license_plate
- color
- mileage
- created_at
- updated_at

## Testing

The test suite validates:
1. ✅ Health check
2. ✅ Authentication (login)
3. ✅ User info retrieval
4. ✅ Customer creation
5. ✅ Vehicle creation
6. ✅ Customer retrieval with vehicles
7. ✅ List all customers
8. ✅ Vehicle retrieval with owner info
9. ✅ Role-based access control

Run tests with: `python test_api.py`

## Production Deployment

For production deployment:

1. Set strong secrets in environment variables
2. Use a production database (PostgreSQL recommended)
3. Use a production WSGI server (gunicorn or uWSGI)
4. Enable HTTPS
5. Set up proper CORS policies
6. Implement rate limiting
7. Set up monitoring and logging

Example with gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

## License

MIT License
