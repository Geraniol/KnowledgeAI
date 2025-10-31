from google import genai
from pathlib import Path
import json


class KnowledgeAI:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = genai.Client(api_key=self.api_key)

    def _ask(self, prompt: str):  # Internal method to send prompt to the model
        print(f"Asking... Prompt length: {len(prompt)}")
        try:
            response = self.model.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            return ""
        return str(getattr(response, "text", "") or "")

    def clarify_and_decompose(self, message: dict): # Agent: Clarify and Decompose
        prompt = f"""
        You are an analytical expert specialized in clarifying and deconstructing questions.

        Your mission:
        1. Clarify what the question truly asks — uncover its explicit and implicit meaning.
        2. Identify key terms, assumptions, and the type of question (factual / evaluative / prescriptive / value-based).
        3. Determine the question’s context — who is asking, for what purpose, and in what domain.
        4. Define its boundaries and core focus — what is central vs peripheral.
        5. Decompose the main question into clear, manageable sub-questions that collectively cover the problem space.

        Think step by step. Be explicit about your reasoning process.

        Given the question:
        {message['question']}

        Return your answer in this structure:
        - Clarified meaning:
        - Key assumptions or hidden premises:
        - Context and intent:
        - Boundaries and scope:
        - Decomposed sub-questions:
        """

        return self._ask(prompt)

    def search_and_verify(self, message: dict): # Agent: Search and Verify
        prompt = f"""
        You are an expert in research, information verification, and evidence assessment.

        Your mission:
        1. Identify the types of data or sources needed to answer the question.
        2. Distinguish between primary (original) and secondary (derived) sources.
        3. Evaluate reliability — consider authority, bias, and corroboration.
        4. Highlight any inconsistencies or unexplained anomalies.
        5. Identify missing information or uncertainties, and propose plausible assumptions if needed.

        Be critical, specific, and balanced in tone.

        Given the clarified question and sub-questions:
        {json.dumps(message, ensure_ascii=False)}

        Return your answer in this structure:
        - Information types required:
        - Potential sources and reliability assessment:
        - Cross-validation or inconsistencies found:
        - Missing information and assumptions:
        - Summary of verified insights:
        """

        return self._ask(prompt)

    def analyze_and_reason(self, message: dict): # Agent: Analyze and Reason
        prompt = f"""
        You are a reasoning and analytical expert.

        Your mission:
        1. Use logical reasoning to connect evidence with conclusions.
        2. Apply suitable analytical frameworks (e.g., causal analysis, SWOT, cost-benefit, ethical frameworks).
        3. Test alternative explanations or hypotheses.
        4. Consider counterexamples and limits of your reasoning.
        5. Draw intermediate conclusions with clear justification.

        Think in causal chains or structured logic. Maintain transparency of reasoning.

        Given the question and supporting information:
        {json.dumps(message, ensure_ascii=False)}

        Return your answer in this structure:
        - Main analytical framework used:
        - Logical reasoning process:
        - Key findings or inferences:
        - Counterarguments or limitations:
        - Tentative conclusion:
        """

        return self._ask(prompt)

    def reflect_and_evaluate(self, message: dict): # Agent: Reflect and Evaluate
        prompt = f"""
        You are an expert in reflective and ethical evaluation.

        Your mission:
        1. Examine your prior reasoning for potential bias, assumptions, or blind spots.
        2. Assess ethical and social implications of your conclusions.
        3. Identify who benefits or is harmed; consider fairness and long-term consequences.
        4. Reflect on your confidence level and what further inquiry might be needed.
        5. Suggest how the reasoning could be improved or reframed.

        Be honest, meta-cognitive, and ethically aware.

        Given the prior analysis:
        {json.dumps(message, ensure_ascii=False)}

        Return your answer in this structure:
        - Detected biases or assumptions:
        - Ethical or social implications:
        - Strengths and weaknesses of the reasoning:
        - Confidence level and uncertainties:
        - Suggestions for refinement or next steps:
        """

        return self._ask(prompt)

    def synthesize_and_communicate(self, message: dict): # Agent: Synthesize and Communicate
        prompt = f"""
        You are an expert communicator and synthesizer of complex reasoning.

        Your mission:
        1. Integrate all previous stages into a coherent, concise synthesis.
        2. Present a clear answer or position, supported by logical justification.
        3. Highlight implications, limitations, and future directions.
        4. Adapt tone and structure for clarity and impact (assume a professional audience).
        5. Maintain intellectual humility — acknowledge uncertainty and open questions.

        Given the full analysis:
        {json.dumps(message, ensure_ascii=False)}

        Return your answer in this structure:
        - Core conclusion (summary in 1–2 sentences):
        - Supporting logic or evidence:
        - Implications and significance:
        - Limitations and uncertainties:
        - Future directions or open questions:
        - Ethical considerations:
        """

        return self._ask(prompt)

    def visualize_process(self, message: dict, save_path: Path = Path("output.html")): # Visualize the reasoning process
        html_template_path = Path("template.html")
        html_template = html_template_path.read_text()
        content = html_template\
            .replace("{{question}}", message["question"])\
            .replace("{{clarify_and_decompose}}", message["clarify_and_decompose"])\
            .replace("{{search_and_verify}}", message["search_and_verify"])\
            .replace("{{analyze_and_reason}}", message["analyze_and_reason"])\
            .replace("{{reflect_and_evaluate}}", message["reflect_and_evaluate"])\
            .replace("{{synthesize_and_communicate}}", message["synthesize_and_communicate"])
        save_path.write_text(content)

    def ask(self, question: str, save_path: Path = Path("output.json")): # Main method to process the question through all agents
        message = {"question": question}
        message["clarify_and_decompose"] = self.clarify_and_decompose(message)
        message["search_and_verify"] = self.search_and_verify(message) if message["clarify_and_decompose"] else ""
        message["analyze_and_reason"] = self.analyze_and_reason(message) if message["search_and_verify"] else ""
        message["reflect_and_evaluate"] = self.reflect_and_evaluate(message) if message["analyze_and_reason"] else ""
        message["synthesize_and_communicate"] = self.synthesize_and_communicate(message) if message["reflect_and_evaluate"] else ""
        print("Final synthesis completed.") if message["synthesize_and_communicate"] else print("No synthesis generated.")

        save_path.write_text(json.dumps(message, indent=4, ensure_ascii=False))
        self.visualize_process(message, save_path=Path("output.html"))
        print(f"Process saved to {save_path} and ./output.html")

        return message["synthesize_and_communicate"]


if __name__ == "__main__":
    API_KEY_PATH = "API_KEY.txt"
    model = KnowledgeAI(Path(API_KEY_PATH).read_text().strip())
    question = input("Enter your question: ")
    response = model.ask(question, save_path=Path("response.json"))
    print(f"Final Response:\n{response}")
