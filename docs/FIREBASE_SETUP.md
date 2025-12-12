# Firebase Setup Guide

## Bước 1: Tạo Firebase Project

1. Truy cập: https://console.firebase.google.com/
2. Click **"Add project"** (Thêm dự án)
3. Tên dự án: `fruit-classification-system`
4. Enable Google Analytics (tùy chọn)
5. Click **"Create project"**

---

## Bước 2: Enable Firebase Services

### 2.1 Firebase Storage (Lưu ảnh)

1. Sidebar → **Storage**
2. Click **"Get started"**
3. Choose **Production mode** (sẽ config rules sau)
4. Location: `asia-southeast1` (Singapore - gần VN)
5. Click **"Done"**

### 2.2 Cloud Firestore (Database)

1. Sidebar → **Firestore Database**
2. Click **"Create database"**
3. Choose **Production mode**
4. Location: `asia-southeast1`
5. Click **"Enable"**

### 2.3 Authentication

1. Sidebar → **Authentication**
2. Click **"Get started"**
3. Tab **"Sign-in method"**
4.Enable **Google** provider:
   - Click Google
   - Toggle Enable
   - Support email: your-email@gmail.com
   - Save
5. Enable **Email/Password**:
   - Click Email/Password
   - Enable
   - Save

### 2.4 Cloud Messaging (Push Notifications)

1. Sidebar → **Cloud Messaging**
2. Automatically enabled (no setup needed)

---

## Bước 3: Get Firebase Credentials

### 3.1 Web App Credentials

1. Project Overview → Click ⚙️ → **Project settings**
2. Tab **"General"**
3. Scroll to **"Your apps"**
4. Click **Web icon** (</>) → **"Add app"**
5. App nickname: `fruit-dashboard`
6. Enable **"Firebase Hosting"** (optional)
7. Click **"Register app"**
8. **Copy the config**:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "fruit-classification-system.firebaseapp.com",
  projectId: "fruit-classification-system",
  storageBucket: "fruit-classification-system.firebasestorage.app",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc..."
};
```

9. Save this → will use in `dashboard/firebase-config.js`

### 3.2 Backend (Admin SDK) Credentials

1. Project settings → Tab **"Service accounts"**
2. Click **"Generate new private key"**
3. Click **"Generate key"**
4. File JSON sẽ download → **VERY IMPORTANT!**
5. Rename to `firebase_config.json`
6. Save vào `backend/firebase_config.json`
7. **NEVER commit to git!** (add to .gitignore)

---

## Bước 4: Configure Security Rules

### 4.1 Storage Rules

1. Storage → Tab **"Rules"**
2. Paste:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Images folder
    match /images/{imageId} {
      // Anyone authenticated can read
      allow read: if request.auth != null;
      // Only backend (admin SDK) can write
      allow write: if false;
    }
  }
}
```

3. Click **"Publish"**

### 4.2 Firestore Rules

1. Firestore → Tab **"Rules"**
2. Paste:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection (for roles)
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if false; // Only admin SDK
    }
    
    // Classifications collection
    match /classifications/{classificationId} {
      allow read: if request.auth != null;
      allow write: if false; // Only backend (admin SDK)
    }
  }
}
```

3. Click **"Publish"**

---

## Bước 5: Setup Admin User

### Option 1: Manual (Console)

1. Authentication → **Users** tab
2. Click **"Add user"**
3. Email: your-admin@gmail.com
4. Password: your-secure-password
5. Click **"Add user"**
6. Copy the **User UID**

7. Go to Firestore → **Start collection**
   - Collection ID: `users`
   - Document ID: `<paste-user-uid>`
   - Fields:
     ```
     email: "your-admin@gmail.com"
     role: "admin"
     createdAt: <timestamp>
     ```
   - Save

### Option 2: Programmatic (Recommended)

Create `backend/setup_admin.py`:

```python
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Create admin user
email = "admin@example.com"
password = "your-secure-password"

try:
    user = auth.create_user(
        email=email,
        password=password,
        display_name="Admin"
    )
    
    # Set admin role in Firestore
    db.collection('users').document(user.uid).set({
        'email': email,
        'role': 'admin',
        'createdAt': firestore.SERVER_TIMESTAMP
    })
    
    print(f"✓ Admin created: {email}")
    print(f"  UID: {user.uid}")
    
except Exception as e:
    print(f"✗ Error: {e}")
```

Run:
```bash
cd backend
pip install firebase-admin
python setup_admin.py
```

---

## Bước 6: Test Connection

### Test từ Backend

Create `backend/test_firebase.py`:

```python
import firebase_admin
from firebase_admin import credentials, storage, firestore

# Initialize
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'fruit-classification-system.firebasestorage.app'
})

# Test Storage
bucket = storage.bucket()
print(f"✓ Storage bucket: {bucket.name}")

# Test Firestore
db = firestore.client()
test_doc = db.collection('test').document('test').set({
    'test': 'Hello Firebase!',
    'timestamp': firestore.SERVER_TIMESTAMP
})
print("✓ Firestore connected")

# Clean up test
db.collection('test').document('test').delete()
print("✓ All tests passed!")
```

Run:
```bash
python test_firebase.py
```

---

## Bước 7: Update .gitignore

Add to `.gitignore`:

```
# Firebase credentials
backend/firebase_config.json
**/firebase_config.json

# Frontend env
dashboard/firebase-config.js
```

---

## Tóm tắt Files cần tạo

```
DATT/
├── backend/
│   └── firebase_config.json       ← From Step 3.2 (DON'T commit!)
├── dashboard/
│   └── firebase-config.js         ← From Step 3.1
└── .gitignore                     ← Updated in Step 7
```

---

## Checklist

- [ ] Firebase project created
- [ ] Storage enabled (asia-southeast1)
- [ ] Firestore enabled (asia-southeast1)
- [ ] Authentication enabled (Google + Email)
- [ ] Cloud Messaging enabled
- [ ] Web app configured
- [ ] Service account key downloaded
- [ ] Storage rules set
- [ ] Firestore rules set
- [ ] Admin user created
- [ ] Backend test passed
- [ ] .gitignore updated

---

## Next Steps

After Firebase setup:
1. ✅ Implement `backend/firebase_storage.py`
2. ✅ Update `backend/database.py` schema
3. ✅ Add Firebase SDK to web dashboard
4. ✅ Implement authentication UI
5. ✅ Setup Flutter app with Firebase
