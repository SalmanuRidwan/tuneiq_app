import json
import os
import sys

# Ensure project root is on sys.path so imports like `tuneiq_app.data_pipeline` resolve
sys.path.insert(0, os.getcwd())

import pandas as pd
import predictor as p


if __name__ == '__main__':
    sample_path = os.path.join(os.getcwd(), 'sample_data', 'streaming_sample.csv')
    df = pd.read_csv(sample_path)
    preds = p.predict_impact(df)
    print(json.dumps(preds, indent=2))
