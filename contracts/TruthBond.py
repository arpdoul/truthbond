# { "Depends": "py-genlayer:test" }
# v0.1.2

from genlayer import *
import json

@gl.contract
class TruthBond:
    claims: TreeMap[u256, dict]
    claim_count: u256
    verdicts: TreeMap[u256, str]
    submitters: TreeMap[u256, Address]

    def __init__(self) -> None:
        self.claim_count = u256(0)

    @gl.public.write
    def submit_claim(self, article_url: str) -> None:
        claim_id = self.claim_count
        self.claims[claim_id] = {
            "url": article_url,
            "status": "pending"
        }
        self.submitters[claim_id] = gl.message.sender_account
        self.claim_count = u256(int(self.claim_count) + 1)

    @gl.public.write
    def verify_claim(self, claim_id: u256) -> None:
        claim = self.claims[claim_id]
        article_url = claim["url"]

        def fetch_article() -> str:
            return gl.get_webpage(article_url, mode="text")

        article_content = gl.eq_principle_strict_eq(fetch_article)

        task = f"""
        You are a fact-checking AI. Analyze this article and determine
        if it contains misinformation or fake news.
        Article: {article_content}
        Respond ONLY with JSON:
        {{"verdict": "FAKE" or "REAL", "reason": "brief explanation"}}
        """

        result = gl.eq_principle_prompt_comparative(
            task,
            principle="Verdict must be FAKE or REAL based on factual accuracy"
        )

        verdict_data = json.loads(result)
        self.verdicts[claim_id] = verdict_data["verdict"]
        self.claims[claim_id] = {
            "url": article_url,
            "status": "verified",
            "verdict": verdict_data["verdict"],
            "reason": verdict_data["reason"]
        }

    @gl.public.view
    def get_claim(self, claim_id: u256) -> dict:
        return self.claims[claim_id]

    @gl.public.view
    def get_verdict(self, claim_id: u256) -> str:
        return self.verdicts[claim_id]

    @gl.public.view
    def get_total_claims(self) -> u256:
        return self.claim_count
