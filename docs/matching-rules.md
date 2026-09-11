# Matching Rules

Weighted rules (admin configurable):
- location: 0.4
- budget: 0.3
- property_type: 0.2
- timeframe: 0.1

Score = weighted sum of criterion scores in `[0,1]`.
Breakdown payload includes weighted score and raw sub-score.
