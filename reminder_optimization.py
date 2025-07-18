import random
from collections import defaultdict

class PersonalizedBandit:
    def __init__(self, arms, epsilon=0.1):
        self.arms = arms  # List of tuples: (channel, time, message_type)
        self.epsilon = epsilon
        self.counts = defaultdict(lambda: [0] * len(arms))  # patient_id -> [count per arm]
        self.successes = defaultdict(lambda: [0] * len(arms))  # patient_id -> [success per arm]

    def select_arm(self, patient_id):
        if random.random() < self.epsilon:
            return random.randint(0, len(self.arms) - 1)  # Explore
        else:
            counts = self.counts[patient_id]
            successes = self.successes[patient_id]
            rates = [s / c if c > 0 else 0 for s, c in zip(successes, counts)]
            return rates.index(max(rates)) if any(counts) else random.randint(0, len(self.arms) - 1)

    def update(self, patient_id, arm_index, reward):
        self.counts[patient_id][arm_index] += 1
        self.successes[patient_id][arm_index] += reward  # reward: 1=adhered, 0=not

# Example usage:
if __name__ == "__main__":
    arms = [
        ("SMS", "8am", "friendly"),
        ("WhatsApp", "6pm", "urgent"),
        ("Voice", "12pm", "simple"),
    ]
    bandit = PersonalizedBandit(arms)
    patient_id = "patient_1"
    for _ in range(10):
        arm = bandit.select_arm(patient_id)
        print("Selected:", arms[arm])
        # Simulate a response (random for demo)
        reward = random.choice([0, 1])
        bandit.update(patient_id, arm, reward) 