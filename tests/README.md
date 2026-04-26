## Running the Dashboard

Generate sample telemetry first:

    python scripts/generate_sample_data.py --config configs/base.yaml

Then run the Streamlit dashboard:

    streamlit run scripts/run_dashboard.py -- --config configs/base.yaml

The dashboard loads the generated CSV file, calculates gameplay metrics, and displays player, session, level, combat, and item insights.