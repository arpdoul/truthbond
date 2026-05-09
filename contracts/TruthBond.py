# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

class TruthBond(gl.Contract):
    claims: TreeMap[str, str]
    claim_count: u256

    def __init__(self):
        self.claim_count = 0

    @gl.public.view
    def get_count(self) -> str:
        return str(self.claim_count)

    @gl.public.view
    def get_claim(self, claim_id: str) -> str:
        return self.claims.get(claim_id, '{}')

    @gl.public.write
    def post_claim(self, url: str) -> None:
        cid = str(self.claim_count)
        self.claims[cid] = json.dumps({"url": url, "status": "pending", "verdict": ""})
        self.claim_count += 1

    @gl.public.write
    def verify_claim(self, claim_id: str) -> None:
        stored = self.claims.get(claim_id, None)
        if stored is None:
            return
        claim = json.loads(stored)
        url = claim["url"]

        prompt = f"""
        You are a fact-checker. Analyze this URL and determine if the article is real news or satire/fake.
        URL: {url}
        Respond as JSON: {{"verdict": "TRUE", "reason": "brief reason"}}
        verdict must be TRUE (real news), FALSE (fake/satire), or UNVERIFIABLE.
        """

        def leader_fn():
            return gl.nondet.exec_prompt(prompt, response_format="json")

        def validator_fn(leaders_res) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            my_result = leader_fn()
            return my_result["verdict"] == leaders_res.calldata["verdict"]

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        claim["verdict"] = result.get("verdict", "UNVERIFIABLE")
        claim["status"] = "verified"
        self.claims[claim_id] = json.dumps(claim)
