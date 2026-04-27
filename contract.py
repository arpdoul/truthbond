# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

class TruthBond(gl.Contract):
    # Storage
    claims: TreeMap[str, str]      # claim_id -> JSON claim data
    claim_count: u256
    owner: str

    def __init__(self):
        self.claim_count = 0
        self.owner = str(gl.message.sender_address)

    @gl.public.view
    def get_claim(self, claim_id: str) -> str:
        stored = self.claims.get(claim_id, None)
        if stored is None:
            return json.dumps({"error": "Claim not found"})
        return stored

    @gl.public.view
    def get_count(self) -> str:
        return str(self.claim_count)

    @gl.public.write
    def post_claim(
        self,
        headline: str,
        source_url: str,
        category: str
    ) -> str:
        claim_id = str(self.claim_count)
        claim = {
            "id": claim_id,
            "headline": headline,
            "source_url": source_url,
            "category": category,
            "poster": str(gl.message.sender_address),
            "status": "pending",
            "verdict": "",
            "verdict_reason": "",
            "challenger": ""
        }
        self.claims[claim_id] = json.dumps(claim)
        self.claim_count += 1
        return claim_id

    @gl.public.write
    def challenge_claim(self, claim_id: str) -> str:
        stored = self.claims.get(claim_id, None)
        if stored is None:
            return "ERROR: claim not found"
        claim = json.loads(stored)
        if claim["status"] != "pending":
            return "ERROR: claim already processed"
        claim["challenger"] = str(gl.message.sender_address)
        claim["status"] = "challenged"
        self.claims[claim_id] = json.dumps(claim)
        return "challenged"

    @gl.public.write
    def verify_claim(self, claim_id: str) -> str:
        stored = self.claims.get(claim_id, None)
        if stored is None:
            return "ERROR: not found"
        claim = json.loads(stored)

        headline = claim["headline"]
        source_url = claim["source_url"]
        category = claim["category"]

        def fetch_and_verify() -> str:
            # Fetch the actual webpage content
            try:
                web_content = gl.get_webpage(source_url, mode="text")
                page_text = web_content[:3000]  # first 3000 chars
            except Exception:
                page_text = "Could not fetch page"

            prompt = f"""You are a professional fact-checker and journalist.

CLAIM TO VERIFY: "{headline}"
CATEGORY: {category}
SOURCE URL: {source_url}
PAGE CONTENT FETCHED: {page_text}

Your task:
1. Analyze if the headline/claim is supported by the page content
2. Check if the claim is factually accurate based on what you know
3. Give a clear verdict

Respond ONLY in this exact JSON format:
{{
  "verdict": "TRUE" or "FALSE" or "UNVERIFIABLE",
  "confidence": "HIGH" or "MEDIUM" or "LOW",
  "reason": "One clear sentence explaining your verdict"
}}"""

            result = gl.exec_prompt(prompt)
            return result

        raw = gl.eq_principle_prompt_comparative(
            fetch_and_verify,
            principle="The verdict must be TRUE, FALSE, or UNVERIFIABLE based on evidence"
        )

        try:
            data = json.loads(raw)
            claim["verdict"] = data.get("verdict", "UNVERIFIABLE")
            claim["verdict_reason"] = (
                data.get("reason", "") +
                " [Confidence: " + data.get("confidence", "?") + "]"
            )
        except Exception:
            claim["verdict"] = "UNVERIFIABLE"
            claim["verdict_reason"] = raw[:200]

        claim["status"] = "verified"
        self.claims[claim_id] = json.dumps(claim)
        return claim["verdict"]
