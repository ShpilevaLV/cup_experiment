# VLM-enhanced Urban Planning with LLM Agents

Experiment for Research Proposal (AIRI Summer School 2026).  
Tests whether adding visual observations (simulated VLM) improves LLM-generated urban zoning plans.

## Results
| Site | Faithfulness (Base) | Faithfulness (Enh) | Expert (Enh) | Overall Winner |
|------|---------------------|--------------------|--------------|----------------|
| ZIL Severny | 0.700 | 0.727 | 3/3 | Enhanced |
| Serp i Molot | 1.000 | 0.875 | 1/3 | Baseline |
| Nagatinsky Zaton | 0.889 | 0.889 | 2.5/3 | Enhanced |

See `report.md` for full analysis.

## How to reproduce
1. Clone the repository.
2. Install Python 3.x.
3. Run `python evaluate.py` to compute faithfulness scores.
4. Examine `data/` for site descriptions, VLM observations, and constraints.

## Author
Lina Shpileva, 2026
