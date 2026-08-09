from typing import Optional


class MetricsCalculator:
    def calculate_coverage(self, coverage_data: dict) -> dict:
        return {
            "line_coverage_pct": coverage_data.get("line_rate", 0.0) * 100,
            "branch_coverage_pct": coverage_data.get("branch_rate", 0.0) * 100,
            "function_coverage_pct": coverage_data.get("function_rate", 0.0) * 100,
            "lines_covered": coverage_data.get("lines_covered", 0),
            "lines_total": coverage_data.get("lines_total", 0),
        }

    def calculate_flakiness(self, test_history: list[dict]) -> float:
        if not test_history:
            return 0.0

        statuses = [run.get("status", "") for run in test_history]
        if len(statuses) < 2:
            return 0.0

        transitions = 0
        for i in range(1, len(statuses)):
            if statuses[i] != statuses[i - 1]:
                transitions += 1

        return transitions / (len(statuses) - 1)

    def calculate_prd_coverage(self, requirements: list[dict], test_cases: list[dict]) -> dict:
        total_reqs = len(requirements)
        if total_reqs == 0:
            return {"covered": 0, "total": 0, "percentage": 0.0}

        req_tags = {r.get("tag", "") for r in requirements}
        covered_tags = set()

        for tc in test_cases:
            ref = tc.get("prd_reference", "")
            if ref in req_tags:
                covered_tags.add(ref)

        covered = len(covered_tags)
        return {
            "covered": covered,
            "total": total_reqs,
            "percentage": (covered / total_reqs) * 100,
        }

    def aggregate_run_metrics(self, results: list[dict]) -> dict:
        total = len(results)
        if total == 0:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "pass_rate": 0.0,
                "total_duration_ms": 0,
            }

        passed = sum(1 for r in results if r.get("status") == "PASSED")
        failed = sum(1 for r in results if r.get("status") == "FAILED")
        errors = sum(1 for r in results if r.get("status") not in ("PASSED", "FAILED"))
        total_duration = sum(r.get("duration_ms", 0) for r in results)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": (passed / total) * 100,
            "total_duration_ms": total_duration,
        }
