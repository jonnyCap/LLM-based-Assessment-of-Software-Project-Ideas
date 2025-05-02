import pandas as pd


class EvaluationResult:
    def __init__(self, novelty: int, usefulness: int, market_potential: int, applicability: int, complexity: int, completeness: int, feedback: str):
        self.novelty = novelty
        self.usefulness = usefulness
        self.market_potential = market_potential
        self.applicability = applicability
        self.complexity = complexity
        self.completeness = completeness
        self.feedback = feedback

    def to_list(self):
        return [self.novelty, self.usefulness, self.market_potential, self.applicability, self.complexity, self.completeness]

    def to_dict(self):
        return {
            "novelty": self.novelty,
            "usefulness": self.usefulness,
            "market_potential": self.market_potential,
            "applicability": self.applicability,
            "complexity": self.complexity,
            "completeness": self.completeness,
            "feedback": self.feedback
        }

    @staticmethod
    def to_dataframe(results: list):
        return pd.DataFrame([res.to_list() for res in results],
                            columns=["novelty", "usefulness", "market_potential", "applicability", "complexity", "completeness"])



# MISTRAL
MISTRAL_ID = "mistral"
MISTRAL_EVALUATIONS = [
    EvaluationResult(8, 9, 7, 6, 5, 8, "This is a sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

MISTRAL_ADVANCED_EVALUATIONS = [
    EvaluationResult(9, 8, 7, 6, 5, 9, "This is a sample feedback."),
    EvaluationResult(8, 7, 6, 5, 4, 8, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

# DEEPSEEK
DEEPSEEK_ID = "deepseek-r1"
DEEPSEEK_EVALUATIONS = [
    EvaluationResult(8, 9, 7, 6, 5, 8, "This is a sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

DEEPSEEK_ADVANCED_EVALUATIONS = [
    EvaluationResult(9, 8, 7, 6, 5, 9, "This is a sample feedback."),
    EvaluationResult(8, 7, 6, 5, 4, 8, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

# MIXTRAL
MIXTRAL_ID = "mixtral"
MIXTRAL_EVALUATIONS = [
    EvaluationResult(8, 9, 7, 6, 5, 8, "This is a sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

MIXTRAL_ADVANCED_EVALUATIONS = [
    EvaluationResult(9, 8, 7, 6, 5, 9, "This is a sample feedback."),
    EvaluationResult(8, 7, 6, 5, 4, 8, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

# GEMMA3
GEMMA3_ID = "gemma3"
GEMMA3_EVALUATIONS = [
    EvaluationResult(8, 9, 7, 6, 5, 8, "This is a sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

GEMMA3_ADVANCED_EVALUATIONS = [
    EvaluationResult(9, 8, 7, 6, 5, 9, "This is a sample feedback."),
    EvaluationResult(8, 7, 6, 5, 4, 8, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

# LLAMA3.1
LLAMA3_1_ID = "llama3-1"
LLAMA3_1_EVALUATIONS = [
    EvaluationResult(8, 9, 7, 6, 5, 8, "This is a sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

LLAMA3_1_ADVANCED_EVALUATIONS = [
    EvaluationResult(9, 8, 7, 6, 5, 9, "This is a sample feedback."),
    EvaluationResult(8, 7, 6, 5, 4, 8, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

# PHI
PHI_ID = "phi"
PHI_EVALUATIONS = [
    EvaluationResult(8, 9, 7, 6, 5, 8, "This is a sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

PHI_ADVANCED_EVALUATIONS = [
    EvaluationResult(9, 8, 7, 6, 5, 9, "This is a sample feedback."),
    EvaluationResult(8, 7, 6, 5, 4, 8, "This is another sample feedback."),
    EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
]

# Summaries
MISTRAL_SUMMARY = EvaluationResult(8, 9, 7, 6, 5, 8, "This is a sample feedback.")
DEEPSEEK_SUMMARY = EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")
MIXTRAL_SUMMARY = EvaluationResult(9, 8, 7, 6, 5, 9, "This is a sample feedback.")
GEMMA3_SUMMARY = EvaluationResult(8, 7, 6, 5, 4, 8, "This is another sample feedback.")
LLAMA3_1_SUMMARY = EvaluationResult(8, 9, 7, 6, 5, 8, "This is a sample feedback.")
PHI_SUMMARY = EvaluationResult(7, 8, 6, 5, 4, 7, "This is another sample feedback.")

    