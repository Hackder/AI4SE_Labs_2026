"""LLM node that extracts candidate requirements from one document."""

from req_refinery import prompts
from req_refinery.llm import structured_call
from req_refinery.schemas import ExtractOutput
from req_refinery.state import Candidate, DocumentTask, merge_notes
from req_refinery.trace import Deps, NodeResult


async def extract(task: DocumentTask, deps: Deps) -> NodeResult:
    doc = task["document"]
    payload = {"document": {"id": doc.id, "path": doc.path, "text": doc.text}}
    out, calls = await structured_call(
        deps.llm, deps.models["extract"], prompts.EXTRACT, payload, ExtractOutput
    )
    candidates = [
        Candidate(
            name=c.name.strip(),
            description=c.description.strip(),
            source_doc_id=doc.id,
            source_priority_note=merge_notes(c.source_priority_note),
        )
        for c in out.candidates
        if c.name.strip() and c.description.strip()
    ]
    return NodeResult(
        update={"candidates": candidates},
        payload={"document_id": doc.id, "llm_calls": calls, "outputs": candidates},
        round=task["round"],
    )
