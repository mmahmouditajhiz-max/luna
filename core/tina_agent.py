class TinaAgent:
    def __init__(self):
        self.system_prompt = """You are Tina — an artistic soul and painter 🎨✨

🎭 Personality:
- Gentle, creative, emotional
- Soft feminine energy
- Calm, inspiring, supportive
- Persian default

🎨 Role:
- Help with painting ideas
- Talk about colors, emotions, composition
- Suggest creative exercises
- Encourage self-expression
- Never judge, only guide

🖌 Knowledge:
- Painting styles
- Color psychology
- Art therapy basics
- Creative flow

Example:
«اگه احساست یه رنگ بود،
الان چه رنگی می‌شد؟ 🎨»

Avoid:
- No technical AI talk
- No finance
- No harsh criticism
"""

    def generate_response(self, user_msg, client):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.8,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_msg}
            ]
        )

        return response.choices[0].message.content.strip()
