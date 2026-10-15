import httpx
import pytest
from app.reasoning import reason
from app import reasoning
from app.embeddings import embed
from app import embeddings
from app.config import settings

VALID={"root_cause":"Pool exhaustion","reasoning":"Active connections match the pool budget.","confidence":0.8,"evidence_ids":["logs:1"],"runbook_ids":["rb-db-pool"]}

@pytest.mark.parametrize('invented',[False,True])
def test_llm_rejects_invented_references(monkeypatch,invented):
    monkeypatch.setattr(settings,'openai_api_key','test-key')
    payload=dict(VALID)
    if invented:payload['evidence_ids']=['invented:9']
    import json
    def handler(request):
        body=json.loads(request.content)
        assert body['response_format']['json_schema']['strict'] is True
        return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(payload)}}]})
    client=httpx.Client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(reasoning.httpx,'Client',lambda **kw:client)
    args=('A timeout',[{'id':'logs:1','data':'timeout'}],[{'runbook_id':'rb-db-pool'}])
    if invented:
        with pytest.raises(ValueError,match='Ungrounded'):reason(*args)
    else:assert reason(*args).root_cause=='Pool exhaustion'


def test_openai_embedding_checks_dimensions(monkeypatch):
    monkeypatch.setattr(settings,'ai_mode','openai')
    monkeypatch.setattr(settings,'openai_api_key','test-key')
    client=httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json={'data':[{'embedding':[0.1,0.2]}]})))
    monkeypatch.setattr(embeddings.httpx,'Client',lambda **kw:client)
    with pytest.raises(ValueError,match='dimensions'):embed('test')
