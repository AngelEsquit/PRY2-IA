from src.experiments.compare import run_k_comparison


def test_comparison_produces_expected_row_count(tmp_path):
    output = tmp_path / "comparison.csv"
    rows = run_k_comparison(
        rows=10,
        cols=10,
        k=3,
        generator_name="prim",
        seed=10,
        min_manhattan=4,
        output_csv=str(output),
    )

    assert len(rows) == 3 * 4
    assert output.exists()
