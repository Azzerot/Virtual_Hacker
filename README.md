# Virtual Hacker

Virtual Hacker is a defensive LLM-based agent designed to support high-level security and privacy analysis of AI chatbot systems.

Given a structured description of a target chatbot, the agent identifies potential risks such as prompt injection, privacy leakage, hallucination, resource exhaustion, and tool misuse, then generates a safe risk report with severity levels and defensive mitigations.

## Project Goal

The goal of this project is to build a proof-of-concept AI agent for defensive threat modeling of LLM-based applications. The system does not perform real attacks and does not generate exploits, payloads, or offensive instructions.

## Case Study

The selected target is a customer support chatbot based on an LLM, inspired by open-source architectures such as Open WebUI and Ollama.