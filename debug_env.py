#!/usr/bin/env python3
import os

from dotenv import load_dotenv

print("Before loading any .env files:")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

print("\nLoading .env.local:")
load_dotenv(".env.local")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

print("\nLoading .env:")
load_dotenv(".env")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

print("\nFinal DATABASE_URL:", os.getenv("DATABASE_URL"))
