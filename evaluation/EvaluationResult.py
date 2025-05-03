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