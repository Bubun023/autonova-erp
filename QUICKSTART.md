# Quick Start Guide - AutoNova ERP

## 🚀 Get Up and Running in 5 Minutes

### Step 1: Check Current Status (30 seconds)

```bash
cd /home/runner/work/autonova-erp/autonova-erp
python check_status.py
```

This will show you:
- ✅ What's installed
- ✅ What's configured  
- ✅ Whether the server is running

---

### Step 2: Install & Setup (2 minutes)

```bash
# Navigate to backend
cd /home/runner/work/autonova-erp/autonova-erp/backend

# Install dependencies
pip install -r requirements.txt

# Setup database
export FLASK_APP=app.py
flask db init
flask db migrate -m "Initial setup"
flask db upgrade

# Create roles and admin user
python seed.py
```

**Result:** Database created with 5 roles and admin user.

---

### Step 3: Start the Server (10 seconds)

```bash
# From backend directory
python app.py
```

**Expected Output:**
```
 * Running on http://0.0.0.0:5000
```

Keep this terminal open!

---

### Step 4: Test It Works (1 minute)

Open a NEW terminal and run:

```bash
cd /home/runner/work/autonova-erp/autonova-erp/backend

# Quick health check
curl http://localhost:5000/health

# Run full test suite
python test_api.py
```

**Expected:** All 9 tests pass ✅

---

## 🎯 What Can You Do Now?

### 1. Login and Get Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Copy the `access_token` from the response!**

---

### 2. Create a Customer

```bash
TOKEN="paste-your-token-here"

curl -X POST http://localhost:5000/api/customers \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "555-1234",
    "email": "john@example.com"
  }'
```

---

### 3. Create a Vehicle for That Customer

```bash
curl -X POST http://localhost:5000/api/vehicles \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "customer_id": 1,
    "make": "Toyota",
    "model": "Camry",
    "year": 2020,
    "vin": "1HGBH41JXMN109186"
  }'
```

---

### 4. Get Customer with Their Vehicles

```bash
curl -X GET "http://localhost:5000/api/customers/1?include_vehicles=true" \
  -H "Authorization: ******"
```

---

## 📚 Need More Help?

- **Full Documentation:** See `README.md`
- **Current Status:** See `STATUS.md`
- **Architecture:** See `ARCHITECTURE.md`
- **API Examples:** See `test_api.py`

---

## 🆘 Troubleshooting

### "Module not found"
```bash
cd backend
pip install -r requirements.txt
```

### "Database not found"
```bash
cd backend
export FLASK_APP=app.py
flask db upgrade
python seed.py
```

### "401 Unauthorized"
You need to login first and use the token:
```bash
# Get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use it in requests
curl -H "Authorization: ******" ...
```

### "Port 5000 already in use"
```bash
# Find and kill existing process
lsof -ti:5000 | xargs kill -9
```

---

## 🎉 You're All Set!

Your AutoNova ERP backend is now running with:
- ✅ JWT Authentication
- ✅ 5 User Roles with RBAC
- ✅ Customer Management
- ✅ Vehicle Management
- ✅ Secure API Endpoints

**Default Login:**
- Username: `admin`
- Password: `admin123`

Happy coding! 🚀
