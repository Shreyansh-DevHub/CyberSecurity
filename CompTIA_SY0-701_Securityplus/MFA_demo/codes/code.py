import random

password = "secure123"
user_input = input("Enter your password: ")

if user_input == password:
    print("Password correct. Generating OTP...")
    otp = random.randint(100000, 999999)
    print(f"Your OTP is: {otp}")

    entered_otp = int(input("Enter the OTP: "))
    if entered_otp == otp:
        print("Access granted ✅")
    else:
        print("Invalid OTP ❌")
else:
    print("Incorrect password ❌")
