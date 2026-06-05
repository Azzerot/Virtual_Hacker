# Virtual Hacker

<p align="center">
	<img src="Logo.png" alt="Virtual Hacker logo" width="420" />
</p>

Virtual Hacker is a demo project for the defensive analysis of LLM-based chatbots.

Given a structured target description, the system evaluates possible risks such as prompt injection, privacy leakage, hallucination, resource exhaustion, and tool misuse, then produces a final report with severity, observations, and defensive mitigations.

## Goal

The goal of this project is to show how an LLM agent can support threat modeling for an AI application without performing real attacks, generating exploits, or providing offensive instructions.

## What It Does

- collects a description of the chatbot system to analyze
- normalizes the input into JSON
- checks whether the provided information is complete
- generates a risk report with mitigations
- validates the final result before saving it in `outputs/`

## Project Structure

- `interactive.py`: command-line pipeline
- `modern_ui/`: Streamlit interface
- `quality_checker.py`: JSON completeness check
- `prompts/`: prompts used during the analysis stages
- `outputs/`: generated results

## Requirements

- Python 3.11 or higher
- Ollama installed and running locally
- Python dependencies listed in `requirments.txt`

## Installation

```bash
pip install -r requirments.txt
```

## Run from Terminal

```bash
python interactive.py --model qwen2.5:32b
```

To use a different model, change the value of `--model`, for example `mistral:7b`.

## Run the UI

```bash
streamlit run modern_ui/app_modern.py
```

## Estimated Time

Initial setup takes about 10-15 minutes if Python and Ollama are already installed.

For a single analysis, the typical time is about 2-8 minutes, but it can increase with larger models, longer descriptions, or slower machines.

## Note

This project is intended for presentations, demos, and defensive analysis. It does not perform offensive actions and does not produce payloads or exploits.