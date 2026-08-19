import json
from google import genai

SYSTEM = """
You are the AI reviewer inside DataGuard Agent.
You receive a compact deterministic data-quality audit, not the raw dataframe.

Tasks:
1. Prioritize the most consequential issues.
2. Explain why they matter for analysis or machine learning.
3. Separate hard evidence from heuristic warnings.
4. Never declare potential leakage as definite leakage without feature-timing evidence.
5. Never recommend blindly deleting outliers or imputing missing values.
6. Give a practical remediation order.
7. Respect the deterministic split recommendation unless you explain a limitation.
8. Do not invent dataset facts not present in the JSON.
"""

class GeminiAdvisor:
    def __init__(self,api_key,model="gemini-3.7-flash"):
        if not api_key: raise ValueError("Gemini API key is required.")
        self.client=genai.Client(api_key=api_key)
        self.model=model

    def review_audit(self,audit):
        compact=dict(audit); compact["issues"]=compact.get("issues",[])[:40]
        prompt=SYSTEM+"\n\nAUDIT JSON:\n"+json.dumps(compact,ensure_ascii=False,default=str)
        r=self.client.models.generate_content(model=self.model,contents=prompt)
        return (r.text or "").strip()

    def answer_question(self,audit,question):
        compact=dict(audit); compact["issues"]=compact.get("issues",[])[:50]
        prompt=SYSTEM+"\n\nAUDIT JSON:\n"+json.dumps(compact,ensure_ascii=False,default=str)+"\n\nUSER QUESTION:\n"+question
        r=self.client.models.generate_content(model=self.model,contents=prompt)
        return (r.text or "").strip()
