import json
import os
from typing import List, Tuple

def load_plan(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_requirements(site_name: str) -> dict:
    """Load the appropriate requirements file for a given site."""
    req_file = f'data/requirements_{site_name}.json'
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Fallback to default if site-specific file not found
    with open('data/requirements.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def detect_site(filename: str) -> str:
    """Detect site name from filename (e.g., 'site_zil_baseline.json' -> 'zil')."""
    name_lower = filename.lower()
    if 'zil' in name_lower:
        return 'zil'
    elif 'serp' in name_lower:
        return 'serp'
    elif 'nagatino' in name_lower:
        return 'nagatino'
    else:
        return 'default'

def check_area(plan: dict, total_area_ha: float) -> List[str]:
    errors = []
    total_zones_area = sum(zone.get('area_ha', 0) for zone in plan.get('zones', []))
    if abs(total_zones_area - total_area_ha) > 0.1 * total_area_ha:
        errors.append(
            f"Total zones area ({total_zones_area:.2f} ha) deviates from site area ({total_area_ha} ha) by more than 10%"
        )
    return errors

def check_green_space(plan: dict, min_green_percent: float = 15.0) -> List[str]:
    errors = []
    total_area = sum(zone.get('area_ha', 0) for zone in plan.get('zones', []))
    if total_area == 0:
        return errors
    green_keywords = ['green', 'park', 'recreation', 'landscape', 'promenade', 'ecological']
    green_area = 0.0
    for zone in plan.get('zones', []):
        purpose = zone.get('purpose', '').lower()
        if any(kw in purpose for kw in green_keywords):
            green_area += zone.get('area_ha', 0)
    if (green_area / total_area * 100) < min_green_percent:
        errors.append(
            f"Green space ({green_area/total_area*100:.1f}%) below minimum required ({min_green_percent}%)"
        )
    return errors

def check_building_height(plan: dict, max_floors: int = 9) -> List[str]:
    errors = []
    for zone in plan.get('zones', []):
        floors = zone.get('floors')
        if floors is not None and floors > max_floors:
            errors.append(
                f"Zone '{zone.get('zone', 'unknown')}' has {floors} floors, exceeding limit of {max_floors}"
            )
    return errors

def check_flood_risk(plan: dict, flood_risk_zone: bool = False) -> List[str]:
    errors = []
    if flood_risk_zone:
        for zone in plan.get('zones', []):
            if 'residential' in zone.get('purpose', '').lower():
                errors.append(
                    f"Residential zone '{zone.get('zone', 'unknown')}' is located in flood risk zone"
                )
    return errors

def evaluate_plan(plan: dict, requirements: dict) -> Tuple[int, List[str]]:
    all_errors = []
    if 'total_area_ha' in requirements:
        all_errors.extend(check_area(plan, requirements['total_area_ha']))
    if 'min_green_percent' in requirements:
        all_errors.extend(check_green_space(plan, requirements['min_green_percent']))
    if 'max_floors' in requirements:
        all_errors.extend(check_building_height(plan, requirements['max_floors']))
    if requirements.get('flood_risk', False):
        all_errors.extend(check_flood_risk(plan, requirements['flood_risk']))
    return len(all_errors), all_errors

def faithfulness_score(plan: dict, requirements: dict) -> float:
    n_claims = len(plan.get('zones', [])) + 1
    n_errors, _ = evaluate_plan(plan, requirements)
    return 1.0 - (n_errors / n_claims) if n_claims > 0 else 1.0

if __name__ == '__main__':
    baseline_dir = 'generated_plans/baseline/'
    enhanced_dir = 'generated_plans/enhanced/'
    results = []

    for dir_path, label in [(baseline_dir, 'baseline'), (enhanced_dir, 'enhanced')]:
        if not os.path.exists(dir_path):
            continue
        for filename in os.listdir(dir_path):
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(dir_path, filename)
            plan = load_plan(filepath)
            site = detect_site(filename)
            reqs = load_requirements(site)
            score = faithfulness_score(plan, reqs)
            n_errors, error_list = evaluate_plan(plan, reqs)
            results.append({
                'file': filename,
                'type': label,
                'site': site,
                'faithfulness': round(score, 3),
                'errors': n_errors,
                'error_details': error_list
            })

    # Print summary table
    print("\n" + "="*80)
    print("FAITHFULNESS EVALUATION RESULTS")
    print("="*80)
    print(f"{'Site':<12} {'Type':<10} {'Faithfulness':<15} {'Errors':<8} {'File'}")
    print("-"*80)
    for r in sorted(results, key=lambda x: (x['site'], x['type'])):
        print(f"{r['site']:<12} {r['type']:<10} {r['faithfulness']:<15.3f} {r['errors']:<8} {r['file']}")
    print("="*80)

    # Print detailed errors if any
    print("\nDETAILED ERRORS:")
    for r in results:
        if r['errors'] > 0:
            print(f"\n{r['file']} ({r['type']}, {r['site']}):")
            for err in r['error_details']:
                print(f"  - {err}")

    # Compare baseline vs enhanced for each site
    print("\n" + "="*80)
    print("COMPARISON: BASELINE vs ENHANCED")
    print("="*80)
    sites = sorted(set(r['site'] for r in results))
    for site in sites:
        baseline = next((r for r in results if r['site'] == site and r['type'] == 'baseline'), None)
        enhanced = next((r for r in results if r['site'] == site and r['type'] == 'enhanced'), None)
        if baseline and enhanced:
            delta = enhanced['faithfulness'] - baseline['faithfulness']
            winner = "Enhanced" if delta > 0 else ("Baseline" if delta < 0 else "Tie")
            print(f"{site:<12} Baseline: {baseline['faithfulness']:.3f}  Enhanced: {enhanced['faithfulness']:.3f}  Delta: {delta:+.3f}  Winner: {winner}")