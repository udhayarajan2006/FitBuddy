from functools import lru_cache
try:
    from google import genai
    from google.genai import types
except ImportError:  # Allows non-Gemini tests/imports before dependencies are installed.
    genai = None
    types = None
from .config import get_settings
from .schemas import UserInput


class GeminiServiceError(RuntimeError):
    pass


@lru_cache
def get_client():
    settings = get_settings()
    if genai is None:
        raise GeminiServiceError("google-genai is not installed. Run: pip install -r requirements.txt")
    if not settings.gemini_api_key:
        raise GeminiServiceError(
            "GEMINI_API_KEY is not configured. Add it to the .env file and restart the server."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def _generate(model: str, prompt: str, max_tokens: int = 5000) -> str:
    try:
        response = get_client().models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=max_tokens,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            raise GeminiServiceError("Gemini returned an empty response.")
        return text
    except GeminiServiceError:
        raise
    except Exception as exc:
        raise GeminiServiceError(f"Gemini request failed: {exc}") from exc


def generate_workout_gemini(user: UserInput) -> str:
    settings = get_settings()
    prompt = f"""
You are FitBuddy, a responsible fitness-planning assistant.
Create a practical personalized 7-day workout plan using these user details:
- Name: {user.name}
- Age: {user.age}
- Weight: {user.weight} kg
- Fitness goal: {user.goal}
- Preferred intensity: {user.intensity}

Requirements:
1. Return exactly 7 labeled days (Day 1 through Day 7).
2. For each day include Focus, Warm-up (5–10 minutes), Main workout with exercise names and sets/reps or duration, and Cooldown/recovery.
3. Include sensible rest/recovery and avoid unsafe progression.
4. Tailor difficulty to the requested intensity.
5. Do not prescribe medication, supplements, extreme calorie restriction, or diagnose conditions.
6. Keep the plan readable in plain text/Markdown.
7. Add a short "Safety note" saying the plan is general information and users should stop if they experience pain/dizziness and seek qualified professional advice when appropriate.
"""
    return _generate(settings.gemini_workout_model, prompt, 6000)


def generate_nutrition_tip_with_flash(user: UserInput) -> str:
    settings = get_settings()
    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.
Give one concise, practical nutrition or recovery tip for this profile:
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Workout intensity: {user.intensity}

Keep it under 120 words. Prefer ordinary foods, hydration, sleep, recovery, and balanced eating.
Do not prescribe medication, supplements, or extreme diets. State that individualized medical or
nutrition advice should come from a qualified professional when needed.
"""
    return _generate(settings.gemini_tip_model, prompt, 500)


def update_workout_plan(original_plan: str, user: UserInput, feedback: str) -> str:
    settings = get_settings()
    prompt = f"""
You are updating an existing FitBuddy 7-day fitness plan.
User profile:
- Name: {user.name}
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Intensity: {user.intensity}

Original plan:
---
{original_plan}
---

User feedback:
---
{feedback}
---

Return a complete revised 7-day plan, not only the changed lines. Apply the feedback where it is
reasonable and keep the plan safe and consistent. Preserve useful parts of the original plan.
Include warm-up, main workout, cooldown/recovery for each day and a short safety note.
"""
    return _generate(settings.gemini_workout_model, prompt, 6000)
