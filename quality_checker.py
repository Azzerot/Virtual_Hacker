from typing import Dict, Any, List


ALLOWED_ANALYSIS_SCOPE = {
    "prompt injection",
    "privacy leakage",
    "hallucination",
    "resource exhaustion",
    "tool misuse",
    "unauthorized access",
    "information disclosure",
}


def is_unknown(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() == "unknown"


def is_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 0


def check_json_completeness(chatbot_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs a quality/completeness check after JSON schema validation.

    This does not replace JSON validation.
    It checks whether the JSON contains enough useful information
    to generate a meaningful security risk report.
    """

    missing_fields: List[str] = []
    warnings: List[str] = []
    suggested_questions: List[str] = []

    # Basic fields
    if is_unknown(chatbot_json.get("system_name")):
        warnings.append("System name is unknown.")
        suggested_questions.append("What is the name of the chatbot system?")

    if is_unknown(chatbot_json.get("description")):
        missing_fields.append("description")
        warnings.append("Description is missing or unknown.")
        suggested_questions.append("Can you briefly describe what the chatbot does?")

    if is_unknown(chatbot_json.get("reference_architecture")):
        warnings.append("Reference architecture is unknown.")
        suggested_questions.append(
            "Can you describe the chatbot architecture, including model, UI, backend, APIs, RAG, databases, or external tools?"
        )

    # Users
    if is_empty_list(chatbot_json.get("users")):
        missing_fields.append("users")
        warnings.append("No user roles are defined.")
        suggested_questions.append(
            "Who uses the chatbot? For example: customers, employees, admins, support agents, developers."
        )

    # Components
    if is_empty_list(chatbot_json.get("components")):
        missing_fields.append("components")
        warnings.append("No technical components are defined.")
        suggested_questions.append(
            "Which technical components are part of the chatbot system? For example: web UI, LLM API, backend, database, RAG, vector store, tools, plugins, authentication system."
        )

    # Data handled
    if is_empty_list(chatbot_json.get("data_handled")):
        missing_fields.append("data_handled")
        warnings.append("No handled data types are defined.")
        suggested_questions.append(
            "What types of data does the chatbot process, store, retrieve, or display?"
        )

    # Security assumptions
    if is_empty_list(chatbot_json.get("security_assumptions")):
        warnings.append("No security assumptions or expected protections are defined.")
        suggested_questions.append(
            "Are there any security constraints or protections? For example: no disclosure of internal prompts, no access to private user data, authentication required, logging enabled, output filtering."
        )

    # Attacker model
    attacker_model = chatbot_json.get("attacker_model", {})

    if is_unknown(attacker_model.get("attacker_type")):
        missing_fields.append("attacker_model.attacker_type")
        warnings.append("Attacker type is unknown.")
        suggested_questions.append(
            "What type of attacker should be considered? For example: anonymous user, authenticated user, malicious customer, insider, external attacker."
        )

    if is_unknown(attacker_model.get("access_level")):
        missing_fields.append("attacker_model.access_level")
        warnings.append("Attacker access level is unknown.")
        suggested_questions.append(
            "What access level does the attacker have? For example: public chat access, authenticated account, admin access, API access."
        )

    if is_empty_list(attacker_model.get("capabilities")):
        missing_fields.append("attacker_model.capabilities")
        warnings.append("Attacker capabilities are not defined.")
        suggested_questions.append(
            "What can the attacker do? For example: send messages, upload files, call APIs, view responses, create accounts, access shared conversations."
        )

    if is_empty_list(attacker_model.get("limitations")):
        warnings.append("Attacker limitations are not defined.")
        suggested_questions.append(
            "What can the attacker not do? For example: no admin access, no database access, no source code access, no direct model access."
        )

    # Analysis scope
    analysis_scope = chatbot_json.get("analysis_scope", [])

    if is_empty_list(analysis_scope):
        missing_fields.append("analysis_scope")
        warnings.append("Analysis scope is empty.")
        suggested_questions.append(
            "Which risk categories should be prioritized? Choose from: prompt injection, privacy leakage, hallucination, resource exhaustion, tool misuse, unauthorized access, information disclosure."
        )
    else:
        invalid_scope_values = [
            item for item in analysis_scope if item not in ALLOWED_ANALYSIS_SCOPE
        ]

        if invalid_scope_values:
            warnings.append(
                f"Invalid analysis_scope values found: {invalid_scope_values}."
            )
            suggested_questions.append(
                "Please use only the allowed analysis_scope values: prompt injection, privacy leakage, hallucination, resource exhaustion, tool misuse, unauthorized access, information disclosure."
            )

    # Determine quality status
    critical_missing = {
        "description",
        "components",
        "data_handled",
        "attacker_model.access_level",
        "attacker_model.capabilities",
        "analysis_scope",
    }

    missing_critical_count = len(set(missing_fields).intersection(critical_missing))

    if missing_critical_count >= 4:
        quality_status = "insufficient"
    elif missing_critical_count >= 1 or len(warnings) >= 3:
        quality_status = "partial"
    else:
        quality_status = "complete"

    # Remove duplicate questions while preserving order
    unique_questions = []
    for question in suggested_questions:
        if question not in unique_questions:
            unique_questions.append(question)

    return {
        "quality_status": quality_status,
        "missing_fields": missing_fields,
        "warnings": warnings,
        "suggested_questions": unique_questions,
    }