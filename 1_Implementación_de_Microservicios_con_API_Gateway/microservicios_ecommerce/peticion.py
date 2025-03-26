import requests

# Probar directamente el endpoint de usuarios
response = requests.post(
    "http://usuarios-service:8000/api/usuarios/",
    json={
        "username": "testuser",
        "password": "securepassword",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    },
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")