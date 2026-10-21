import os

name = os.environ.get("LEARNER_NAME", "stranger")
level = os.environ.get("LEARNER_LEVEL", "beginner")
print("Hello, " + name + "!")
print("Level: " + level)
