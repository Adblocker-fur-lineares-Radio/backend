import sys

k = 0
try:
    # for line in iter(sys.stdin.readline, b''):
    for line in sys.stdin:
        print(f"Zeile {k}: {line}")
        k += 1

except KeyboardInterrupt:
    sys.stdout.flush()
    pass
