"""
Model definition for Titanic survival prediction.
"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
import joblib
from pathlib import Path


def get_model_path():
    """Get path for saving/loading models."""
    import os
    sm_model_dir = os.environ.get('SM_MODEL_DIR')
    if sm_model_dir:
        return Path(sm_model_dir)
        
    fallback_dir = Path('/opt/ml/model')
    if fallback_dir.exists():
        return fallback_dir
        
    project_root = Path(__file__).parent.parent
    model_path = project_root / 'models'
    model_path.mkdir(parents=True, exist_ok=True)
    return model_path


def create_model(model_type='random_forest', **kwargs):
    """
    Create a machine learning model.
    
    Args:
        model_type: Type of model ('random_forest', 'logistic_regression', 'gradient_boosting')
        **kwargs: Additional parameters for the model
        
    Returns:
        Scikit-learn model instance
    """
    if model_type == 'random_forest':
        default_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_jobs': -1
        }
        default_params.update(kwargs)
        return RandomForestClassifier(**default_params)
    
    elif model_type == 'logistic_regression':
        default_params = {
            'max_iter': 1000,
            'random_state': 42
        }
        default_params.update(kwargs)
        return LogisticRegression(**default_params)
    
    elif model_type == 'gradient_boosting':
        default_params = {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 5,
            'random_state': 42
        }
        default_params.update(kwargs)
        return GradientBoostingClassifier(**default_params)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def save_model(model, filename='titanic_model.pkl'):
    """
    Save trained model to disk.
    
    Args:
        model: Trained model
        filename: Name of file to save model
    """
    model_path = get_model_path()
    filepath = model_path / filename
    joblib.dump(model, filepath)
    print(f"Model saved to: {filepath}")
    return filepath


def load_model(filename='titanic_model.pkl'):
    """
    Load trained model from disk.
    
    Args:
        filename: Name of model file
        
    Returns:
        Loaded model
    """
    model_path = get_model_path()
    filepath = model_path / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Model file not found: {filepath}")
    
    model = joblib.load(filepath)
    print(f"Model loaded from: {filepath}")
    return model
