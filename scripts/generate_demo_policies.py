from pathlib import Path


OUTPUT_DIRECTORY = Path("data/demo_policies")

TOPICS = [
    "Pump Overheating",
    "Conveyor Belt Inspection",
    "Electrical Isolation",
    "Hydraulic Leak Response",
    "Compressed Air System Check",
    "Cooling System Inspection",
    "Lubrication Control",
    "Machine Guarding Inspection",
    "Emergency Shutdown",
    "Shift Handover",
    "Maintenance Incident Logging",
    "Contractor Access",
]


def create_policy_lines(number: int, topic: str) -> list[str]:
    """Create one fictional industrial policy document."""
    return [
        f"Title: {topic} Procedure {number}",
        f"Document ID: OPS-{number:03d}",
        "Classification: Internal",
        f"Purpose: Define the approved process for {topic.lower()}.",
        "Scope: Applies to authorized maintenance personnel.",
        "Trigger: Follow this procedure when the relevant condition is observed.",
        "Step 1: Review the equipment status and relevant safety warnings.",
        "Step 2: Follow the approved lockout-tagout procedure when required.",
        "Step 3: Inspect the equipment using the approved checklist.",
        "Safety: Do not bypass alarms, interlocks, or thermal protection.",
        "Escalation: Report unresolved faults to the maintenance supervisor.",
        "Evidence: Record completed checks in the maintenance log.",
        "Prohibited action: Do not perform work outside your authorization level.",
        "Access: This document is for internal authorized users only.",
        "Review: The procedure must be reviewed after repeated incidents.",
        "Version: 1.0",
        "Status: Fictional training document for the Enterprise Agent project.",
    ]


def main() -> None:
    """Create 60 fictional policy documents for ingestion testing."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    for number in range(1, 61):
        topic = TOPICS[(number - 1) % len(TOPICS)]
        content = "\n".join(create_policy_lines(number, topic)) + "\n"
        policy_path = OUTPUT_DIRECTORY / f"policy-{number:03d}.txt"
        policy_path.write_text(content, encoding="utf-8")

    print("Created 60 demo policy documents with 1,020 total lines.")


if __name__ == "__main__":
    main()