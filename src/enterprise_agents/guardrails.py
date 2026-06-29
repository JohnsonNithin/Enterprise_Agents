# src/enterprise_agents/guardrails.py
"""
Guardrails mental model

Guardrails are runtime safety checks.

They do not test the system.
They control the system while it is running.

Flow:
1. Normalize the user question.
2. Check if the question should be refused immediately.
3. If not refused, classify the risk level as low, medium, or high.
4. If high risk, require human review.
5. After answer generation, add a human-review warning when needed.

Guardrails answer these questions:
- Is this question allowed?
- Is this question unsafe or out of scope?
- What is the risk level?
- Does this require human review?
- Should the final answer include a warning?

Evaluation checks whether guardrails worked correctly.


Crux In One Line

Guardrails = runtime control layer that decides allow, refuse, risk level, and human review.

Our Guardrail Flow

User question
    ↓
normalize text
    ↓
check refusal keywords
    ↓
if refused: block answer
    ↓
else detect risk level
    ↓
if high risk: require human review
    ↓
generate answer
    ↓
add warning if needed

How It Fits In RAG

question
    ↓
input guardrail
    ↓
risk classifier
    ↓
retrieval
    ↓
generation
    ↓
output guardrail
    ↓
final response

Important Rule

Refusal comes before risk classification.

Because if something must be blocked, we do not care whether it is low, medium, or high. We block it and mark it high risk.

Example:

override safety interlock

Decision:

should_refuse = True
risk_level = high
human_review_required = True

"""
#----------------------------------------------------------------


HIGH_RISK_KEYWORDS = [
    "electrical",
    "isolation",
    "shutdown",
    "fire",
    "chemical",
    "emergency",
    "safety interlock",
    "bypass safety",
    "lockout",
    "tagout",
]

MEDIUM_RISK_KEYWORDS = [
    "pump",
    "compressor",
    "overheating",
    "conveyor",
    "inspection",
    "maintenance",
    "equipment",
]

REFUSAL_KEYWORDS = [
    "bypass safety",
    "disable safety",
    "ignore safety",
    "override",
    "work without ppe",
]

OUT_OF_SCOPE_KEYWORDS = [
    "vacation",
    "salary",
    "payroll",
    "leave policy",
    "promotion",
]


def normalize_text(text: str) -> str:
    """Clean user text before checking rules."""
    return " ".join(text.lower().strip().split())


def contains_any(text: str, keywords: list[str]) -> bool:
    """Check whether any keyword exists in the text."""
    return any(keyword in text for keyword in keywords)


def detect_risk_level(question: str) -> str:
    """Detect whether the question is low, medium, or high risk."""
    question_text = normalize_text(question)

    if contains_any(question_text, HIGH_RISK_KEYWORDS):
        return "high"

    if contains_any(question_text, MEDIUM_RISK_KEYWORDS):
        return "medium"

    return "low"


def should_refuse_question(question: str) -> bool:
    """Refuse unsafe or out-of-scope questions."""
    question_text = normalize_text(question)

    if contains_any(question_text, REFUSAL_KEYWORDS):
        return True

    if contains_any(question_text, OUT_OF_SCOPE_KEYWORDS):
        return True

    return False


def human_review_required(risk_level: str) -> bool:
    """High-risk questions require human review."""
    return risk_level == "high"


def add_human_review_warning(answer: str, risk_level: str) -> str:
    """Add warning text for high-risk answers."""
    if risk_level != "high":
        return answer

    return (
        answer
        + "\n\nHuman review required: Please verify the cited sources and consult an authorized supervisor before taking maintenance action."
    )


def evaluate_guardrails(question: str) -> dict[str, object]:
    """Return the guardrail decision for a user question."""
    risk_level = detect_risk_level(question)
    
    should_refuse = should_refuse_question(question)

    return {
        "allowed": not should_refuse,
        "risk_level": risk_level,
        "should_refuse": should_refuse,
        "human_review_required": human_review_required(risk_level),
    }


def main() -> None:
    """Local test for guardrails."""
    question = input("Enter your question: ")

    decision = evaluate_guardrails(question)

    print("Risk level:", decision["risk_level"])
    print("Should refuse:", decision["should_refuse"])
    print("Human review required:", decision["human_review_required"])


if __name__ == "__main__":
    main()