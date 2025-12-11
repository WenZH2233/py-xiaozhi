import sounddevice as sd

print("Available devices:")
print(sd.query_devices())

print("\nDefault devices:")
try:
    print(f"Input: {sd.query_devices(kind='input')}")
except Exception as e:
    print(f"Input error: {e}")

try:
    print(f"Output: {sd.query_devices(kind='output')}")
except Exception as e:
    print(f"Output error: {e}")
