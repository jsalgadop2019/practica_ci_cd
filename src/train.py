"""
Training script for Titanic survival prediction model.
"""
import sys
import json
import argparse
import os
import pandas as pd
from pathlib import Path
from sklearn.model_selection import cross_val_score
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_titanic_data
from src.preprocessing import preprocess_data
from src.model import create_model, save_model


def train_model(model_type='random_forest', val_split=0.2, cv_folds=5):
    """
    Train Titanic survival prediction model.
    
    Args:
        model_type: Type of model to train
        val_split: Validation split ratio
        cv_folds: Number of cross-validation folds
        
    Returns:
        Dictionary with training results
    """
    print("=" * 50)
    print("TITANIC SURVIVAL PREDICTION - TRAINING")
    print("=" * 50)
    
    # Load data
    print("\n1. Loading data...")
    sm_channel_train = os.environ.get('SM_CHANNEL_TRAIN')
    input_dir = Path(sm_channel_train) if sm_channel_train else Path('/opt/ml/input/data/train')
    
    if input_dir.exists() and list(input_dir.glob('*.csv')):
        print(f"   ✓ Running in SageMaker, loading preprocessed data from {input_dir}")
        train_df = pd.read_csv(input_dir / 'train.csv')
        y_train = train_df['Survived']
        X_train = train_df.drop('Survived', axis=1)
        print(f"   ✓ Loaded {len(train_df)} training samples")
        
        X_val = None
        y_val = None
        if (input_dir / 'validation.csv').exists():
            val_df = pd.read_csv(input_dir / 'validation.csv')
            y_val = val_df['Survived']
            X_val = val_df.drop('Survived', axis=1)
            print(f"   ✓ Validation set: {X_val.shape}")
            
        test_df = None
        if (input_dir / 'test.csv').exists():
            test_df = pd.read_csv(input_dir / 'test.csv')
            print(f"   ✓ Loaded {len(test_df)} test samples")
            
    else:
        # Local execution fallback
        train_df, test_df = load_titanic_data()
        print(f"   ✓ Loaded {len(train_df)} training samples")
        if test_df is not None:
            print(f"   ✓ Loaded {len(test_df)} test samples")
        
        # Preprocess data
        print("\n2. Preprocessing data...")
        processed = preprocess_data(train_df, test_df, val_split=val_split)
        X_train = processed['X_train']
        y_train = processed['y_train']
        X_val = processed['X_val']
        y_val = processed['y_val']
        
        print(f"   ✓ Training set: {X_train.shape}")
        if X_val is not None:
            print(f"   ✓ Validation set: {X_val.shape}")
        print(f"   ✓ Features: {X_train.shape[1]}")
    
    # Create model
    print(f"\n3. Creating model ({model_type})...")
    model = create_model(model_type)
    print(f"   ✓ Model created")
    
    # Cross-validation
    print(f"\n4. Cross-validation ({cv_folds} folds)...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring='accuracy')
    print(f"   ✓ CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Train model
    print("\n5. Training model...")
    model.fit(X_train, y_train)
    print("   ✓ Model trained")
    
    # Evaluate on training set
    train_score = model.score(X_train, y_train)
    print(f"\n6. Training accuracy: {train_score:.4f}")
    
    # Evaluate on validation set
    val_score = None
    if X_val is not None and y_val is not None:
        val_score = model.score(X_val, y_val)
        print(f"   Validation accuracy: {val_score:.4f}")
    
    # Feature importance (for tree-based models)
    feature_importance = None
    if hasattr(model, 'feature_importances_'):
        feature_importance = dict(zip(
            X_train.columns,
            model.feature_importances_
        ))
        print("\n7. Top 10 feature importances:")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for i, (feature, importance) in enumerate(sorted_features[:10], 1):
            print(f"   {i}. {feature}: {importance:.4f}")
    
    # Save model
    print("\n8. Saving model...")
    model_filename = f'titanic_model_{model_type}.pkl'
    save_model(model, model_filename)
    
    # Save metrics
    metrics = {
        'model_type': model_type,
        'train_accuracy': float(train_score),
        'val_accuracy': float(val_score) if val_score else None,
        'cv_accuracy_mean': float(cv_scores.mean()),
        'cv_accuracy_std': float(cv_scores.std()),
        'cv_scores': cv_scores.tolist(),
        'n_features': int(X_train.shape[1]),
        'n_train_samples': int(X_train.shape[0]),
        'n_val_samples': int(X_val.shape[0]) if X_val is not None else None,
        'feature_importance': {k: float(v) for k, v in feature_importance.items()} if feature_importance else None
    }
    
    # Save metrics to file
    sm_model_dir = os.environ.get('SM_MODEL_DIR')
    if sm_model_dir:
        reports_path = Path(sm_model_dir)
    elif Path('/opt/ml/model').exists():
        reports_path = Path('/opt/ml/model')
    else:
        project_root = Path(__file__).parent.parent
        reports_path = project_root / 'reports'
        reports_path.mkdir(parents=True, exist_ok=True)
    
    metrics_file = reports_path / 'training_metrics.json'
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"   ✓ Metrics saved to: {metrics_file}")
    
    print("\n" + "=" * 50)
    print("TRAINING COMPLETE!")
    print("=" * 50)
    
    return metrics


def main():
    import traceback
    
    parser = argparse.ArgumentParser(description='Train Titanic survival prediction model')
    parser.add_argument('--model', type=str, default='random_forest',
                        choices=['random_forest', 'logistic_regression', 'gradient_boosting'],
                        help='Type of model to train')
    parser.add_argument('--val-split', type=float, default=0.2,
                        help='Validation split ratio')
    parser.add_argument('--cv-folds', type=int, default=5,
                        help='Number of cross-validation folds')
    
    # SageMaker passes hyperparams as additional args
    args, _ = parser.parse_known_args()
    
    # Diagnostic logging
    print("\n" + "="*50)
    print("DIAGNOSTIC LOGGING")
    print(f"Current Environment: {dict(os.environ)}")
    
    input_paths = ['/opt/ml/input/data/train', '/opt/ml/input/data/', '/app/data/raw']
    for p in input_paths:
        path = Path(p)
        if path.exists():
            print(f"Path {p} exists. Content: {list(path.glob('*'))}")
        else:
            print(f"Path {p} does NOT exist.")
    print("="*50 + "\n")

    try:
        train_model(
            model_type=args.model,
            val_split=args.val_split,
            cv_folds=args.cv_folds
        )
    except Exception as e:
        # Write failure message for SageMaker
        failure_path = Path('/opt/ml/output/failure')
        error_msg = f"TRAINING FAILURE: {str(e)}\n{traceback.format_exc()}"
        print(f"\nCRITICAL ERROR:\n{error_msg}")
        
        try:
            with open(failure_path, 'w') as f:
                f.write(error_msg)
        except Exception as write_err:
            print(f"Could not write to failure file: {write_err}")
            
        sys.exit(2)  # Maintain exit code 2 but with logged context


if __name__ == '__main__':
    main()
