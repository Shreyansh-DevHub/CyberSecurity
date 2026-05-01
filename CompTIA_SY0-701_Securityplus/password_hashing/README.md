# Lab Instructions: Password Hashing & Authentication (Kali Linux)

## Objective
Use Kali Linux to demonstrate the difference between storing plaintext passwords and hashed passwords with Python.

## Requirements
- Kali Linux VM (already installed)
- Python 3 (preinstalled on Kali)
- `hashlib` library (included with Python by default)
- Terminal access

## Steps

1. **Open your Kali Linux terminal**
   - Log in as your user (`kali`) or root if you prefer.
   - Navigate to your project folder:
     ```bash
     cd ~/securityplus-sy0-701-labs/project01_password_hashing
     ```

2. **Create a new Python file**
   - Use nano or vim:
     ```bash
     nano hashing_demo.py
     ```

3. **Write code to store a plaintext password**
   - Example inside the file:
     ```python
     password = "mypassword123"
     ```

4. **Use hashlib to hash the password**
   - Add this code:
     ```python
     import hashlib

     password = "mypassword123"
     hashed = hashlib.sha256(password.encode()).hexdigest()

     print("Plaintext:", password)
     print("Hashed:", hashed)
     ```

5. **Save and run the script**
   - Save in nano with `CTRL+O`, then exit with `CTRL+X`.
   - Run:
     ```bash
     python3 hashing_demo.py
     ```
   - Observe the difference between plaintext and hashed output.

6. **Experiment with different inputs**
   - Edit the file and change the password string.
   - Notice how even small changes produce completely different hashes.

7. **Optional: Add salting**
   - Append a random string to the password before hashing:
     ```python
     salt = "abc123"
     hashed = hashlib.sha256((password + salt).encode()).hexdigest()
     print("Salted Hash:", hashed)
     ```

## Verification
- Confirm that the hashed output is always a long string of letters/numbers.
- Verify that the same password always produces the same hash.
- Verify that different passwords produce different hashes.
- Verify that adding a salt changes the hash even for the same password.

## Reflection
- Plaintext passwords are insecure because they can be read directly.
- Hashing adds security by storing only the hash, not the actual password.
- Salting prevents attackers from using precomputed hash tables (rainbow tables).
