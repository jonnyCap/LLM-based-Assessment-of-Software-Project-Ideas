from enum import Enum

CLAIM = "Claim"
GROUNDS = "Grounds"
WARRANT = "Warrant"
BACKING = "Backing"
REBUTTAL = "Rebuttal"
QUALIFIER = "Qualifier"

COMPONENT_NAMES = [CLAIM, GROUNDS, WARRANT, BACKING, REBUTTAL, QUALIFIER]

class ToulminComponentClassifier(Enum):
    PRESENT = 1
    IMPLICT_WEAK = 2
    ABSENT = 3

class ArgumentationAnalysisResult:

    def __init__(self,
                 claim: ToulminComponentClassifier,
                 claim_notes: str,
                 grounds: ToulminComponentClassifier, 
                 grounds_notes: str,
                 warrant: ToulminComponentClassifier, 
                 warrant_notes: str,
                 backing: ToulminComponentClassifier, 
                 backing_notes: str,
                 rebuttal: ToulminComponentClassifier, 
                 rebuttal_notes: str,
                 qualifier: ToulminComponentClassifier,
                 qualifier_notes: str):
        self.claim = claim
        self.claim_notes = claim_notes
        self.grounds = grounds
        self.grounds_notes = grounds_notes
        self.warrant = warrant
        self.warrant_notes = warrant_notes
        self.backing = backing
        self.backing_notes = backing_notes
        self.rebuttal = rebuttal
        self.rebuttal_notes = rebuttal_notes
        self.qualifier = qualifier
        self.qualifier_notes = qualifier_notes
