from textblob import TextBlob

# Example intent keywords
INTENT_KEYWORDS = {
    "side_effects": ["nausea", "vomit", "dizzy", "rash", "pain", "side effect"],
    "forgot": ["forgot", "missed", "didn't remember", "overslept"],
    "confused": ["confused", "unclear", "don't understand", "instructions"],
    "cost": ["expensive", "cost", "money", "afford"],
    "other": []
}

def analyze_feedback(feedback_text):
    # Sentiment analysis
    blob = TextBlob(feedback_text)
    polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
    sentiment = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"
    
    # Intent detection
    detected_intents = []
    text_lower = feedback_text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            detected_intents.append(intent)
    if not detected_intents:
        detected_intents.append("other")
    
    # Flag if negative or concerning intent
    flag = sentiment == "negative" or any(i in detected_intents for i in ["side_effects", "cost", "confused"])
    
    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "intents": detected_intents,
        "flag": flag
    }

# Example usage
if __name__ == "__main__":
    feedback = "I felt dizzy and nauseous after taking the medicine."
    result = analyze_feedback(feedback)
    print(result) 