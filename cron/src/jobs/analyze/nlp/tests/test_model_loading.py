import pytest
from pathlib import Path

class TestModelFiles:
    """Testy sprawdzające czy pliki modelu istnieją"""
    
    def test_model_file_exists(self, model_path):
        """Test czy plik modelu istnieje"""
        assert model_path.exists(), f"Model file not found at {model_path}"
    
    def test_model_file_extension(self, model_path):
        """Test czy model ma rozszerzenie .pt"""
        assert model_path.suffix == ".pt", f"Model should be .pt file, got {model_path.suffix}"
    
    def test_model_file_not_empty(self, model_path):
        """Test czy plik modelu nie jest pusty"""
        file_size = model_path.stat().st_size
        assert file_size > 0, "Model file is empty"
        
        min_size_mb = 100
        size_mb = file_size / (1024 * 1024)
        assert size_mb > min_size_mb, f"Model too small: {size_mb:.2f}MB (expected >{min_size_mb}MB)"
    
    def test_artifacts_directory_structure(self, artifacts_dir):
        """Test czy struktura katalogów artifacts jest poprawna"""
        assert artifacts_dir.exists(), "artifacts/ directory not found"
        assert (artifacts_dir / "models").exists(), "artifacts/models/ not found"
        assert (artifacts_dir / "reports").exists(), "artifacts/reports/ not found"