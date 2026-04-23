import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tests.test_classification import (
    test_exact_model_code,
    test_not_exact_cpu_diff,
    test_fallback_exact,
    test_similar_segment_diff,
    test_intel_vs_amd_not_similar,
    test_intel_new_naming,
    # Edge case tests
    test_variant_ram_diff_not_variant,
    test_variant_same_series_and_specs,
    test_different_brand_not_similar,
    test_large_price_gap_not_similar,
    test_missing_processor_robustness,
    test_gpu_difference_not_exact,
    test_same_specs_different_model_code,
    test_noisy_processor_name_similar,
    test_case_insensitive_brand,
)

def run_tests():
    tests = [
        test_exact_model_code,
        test_not_exact_cpu_diff,
        test_fallback_exact,
        test_similar_segment_diff,
        test_intel_vs_amd_not_similar,
        test_intel_new_naming,
        # Edge cases
        test_variant_ram_diff_not_variant,
        test_variant_same_series_and_specs,
        test_different_brand_not_similar,
        test_large_price_gap_not_similar,
        test_missing_processor_robustness,
        test_gpu_difference_not_exact,
        test_same_specs_different_model_code,
        test_noisy_processor_name_similar,
        test_case_insensitive_brand,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"Running {test.__name__}...", end=" ")
            test()
            print("PASSED")
            passed += 1
        except AssertionError as e:
            print(f"FAILED  <- {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)} total")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
