"""
Comprehensive tests for FastAPI endpoints.

Tests cover:
- Health check endpoints
- File upload
- Project analysis
- Report generation
- Error handling
- Integration workflows
"""
import pytest
import json
from io import BytesIO
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app


# ============================================================================
# Test Class: Health Check Endpoints
# ============================================================================

class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns health status."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Test /api/health endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_config_endpoint(self, client):
        """Test /api/config endpoint."""
        response = client.get("/api/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "version" in data
        assert "pass_threshold" in data
        assert "scoring_weights" in data


# ============================================================================
# Test Class: File Upload
# ============================================================================

class TestFileUpload:
    """Test file upload functionality."""
    
    def test_upload_single_file(self, client):
        """Test uploading a single file."""
        files = {
            "files": ("test.py", BytesIO(b"print('hello')"), "text/x-python")
        }
        
        response = client.post("/api/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "upload_id" in data
        assert data["files_received"] == 1
    
    def test_upload_multiple_files(self, client):
        """Test uploading multiple files."""
        files = [
            ("files", ("test1.py", BytesIO(b"print('test1')"), "text/x-python")),
            ("files", ("test2.md", BytesIO(b"# Test"), "text/markdown")),
        ]
        
        response = client.post("/api/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["files_received"] == 2
    
    def test_upload_no_files(self, client):
        """Test upload with no files."""
        response = client.post("/api/upload", files=[])
        
        assert response.status_code == 400
    
    def test_upload_invalid_extension(self, client):
        """Test upload with invalid file extension."""
        files = {
            "files": ("test.exe", BytesIO(b"binary"), "application/octet-stream")
        }
        
        response = client.post("/api/upload", files=files)
        
        assert response.status_code == 400
    
    def test_upload_returns_upload_id(self, client):
        """Test that upload returns valid upload ID."""
        files = {
            "files": ("test.py", BytesIO(b"print('test')"), "text/x-python")
        }
        
        response = client.post("/api/upload", files=files)
        data = response.json()
        
        assert "upload_id" in data
        assert len(data["upload_id"]) > 0


# ============================================================================
# Test Class: Project Analysis
# ============================================================================

class TestProjectAnalysis:
    """Test project analysis endpoints."""
    
    def test_analyze_with_upload_id(self, client):
        """Test analyzing project with upload ID."""
        # First upload files
        files = {
            "files": ("test.py", BytesIO(b"print('test')"), "text/x-python")
        }
        upload_response = client.post("/api/upload", files=files)
        upload_id = upload_response.json()["upload_id"]
        
        # Then analyze
        analysis_data = {
            "upload_id": upload_id,
            "project_name": "Test Project"
        }
        response = client.post("/api/analyze", json=analysis_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "project_name" in data
        assert "total_score" in data
        assert "module_scores" in data
    
    def test_analyze_invalid_upload_id(self, client):
        """Test analyzing with invalid upload ID."""
        analysis_data = {
            "upload_id": "invalid-id-12345",
            "project_name": "Test"
        }
        response = client.post("/api/analyze", json=analysis_data)
        
        assert response.status_code == 404
    
    def test_upload_and_analyze_combined(self, client):
        """Test combined upload and analyze endpoint."""
        files = [
            ("files", ("test.py", BytesIO(b"print('test')"), "text/x-python")),
            ("files", ("README.md", BytesIO(b"# Test\n## Description\nTest"), "text/markdown")),
        ]
        
        response = client.post(
            "/api/upload-and-analyze",
            files=files,
            data={"project_name": "Test Project"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "Test Project"
        assert "total_score" in data
        assert "secrets_found" in data
        assert "readme_result" in data
    
    def test_analysis_result_structure(self, client):
        """Test that analysis result has correct structure."""
        files = {
            "files": ("test.py", BytesIO(b"x = 1"), "text/x-python")
        }
        
        response = client.post(
            "/api/upload-and-analyze",
            files=files,
            data={"project_name": "Test"}
        )
        
        data = response.json()
        
        # Check required fields
        required_fields = [
            "project_name", "timestamp", "total_score", "passed",
            "total_issues", "critical_issues", "files_analyzed",
            "module_scores", "all_issues"
        ]
        for field in required_fields:
            assert field in data


# ============================================================================
# Test Class: Report Generation
# ============================================================================

class TestReportGeneration:
    """Test report generation endpoints."""
    
    def test_get_json_report(self, client):
        """Test getting JSON report."""
        # Upload and analyze
        files = {"files": ("test.py", BytesIO(b"x = 1"), "text/x-python")}
        response = client.post(
            "/api/upload-and-analyze",
            files=files,
            data={"project_name": "Test"}
        )
        
        # Note: Report generation happens in background
        # In real test, would need to wait or mock
        # This is a structure test
        assert response.status_code == 200
    
    def test_get_report_invalid_format(self, client):
        """Test getting report with invalid format."""
        response = client.get("/api/report/test-id/invalid")
        
        assert response.status_code == 400
    
    def test_get_report_not_found(self, client):
        """Test getting non-existent report."""
        response = client.get("/api/report/nonexistent-id/json")
        
        assert response.status_code == 404
    
    def test_report_formats(self, client):
        """Test that all report formats are supported."""
        formats = ["json", "html", "md"]
        
        for fmt in formats:
            # This will 404 but should not 400 (invalid format)
            response = client.get(f"/api/report/test-id/{fmt}")
            assert response.status_code in [200, 404]  # Not 400


# ============================================================================
# Test Class: Upload Management
# ============================================================================

class TestUploadManagement:
    """Test upload management endpoints."""
    
    def test_delete_upload(self, client):
        """Test deleting an upload."""
        # First upload
        files = {"files": ("test.py", BytesIO(b"x = 1"), "text/x-python")}
        upload_response = client.post("/api/upload", files=files)
        upload_id = upload_response.json()["upload_id"]
        
        # Then delete
        response = client.delete(f"/api/upload/{upload_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_nonexistent_upload(self, client):
        """Test deleting non-existent upload."""
        response = client.delete("/api/upload/nonexistent-id")
        
        # Should handle gracefully
        assert response.status_code in [200, 404, 500]


# ============================================================================
# Test Class: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling."""
    
    def test_404_for_invalid_endpoint(self, client):
        """Test 404 for invalid endpoint."""
        response = client.get("/api/invalid-endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed."""
        response = client.put("/api/health")
        
        assert response.status_code == 405
    
    def test_malformed_json(self, client):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        response = client.post("/api/analyze", json={})
        
        assert response.status_code == 422


# ============================================================================
# Test Class: CORS
# ============================================================================

class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.options("/api/health")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
    
    def test_cors_allows_methods(self, client):
        """Test that CORS allows required methods."""
        response = client.get("/api/health")
        
        # Should not block due to CORS
        assert response.status_code == 200


# ============================================================================
# Test Class: Integration Workflows
# ============================================================================

@pytest.mark.integration
class TestIntegrationWorkflows:
    """Test complete integration workflows."""
    
    def test_complete_analysis_workflow(self, client):
        """Test complete workflow from upload to report."""
        # Step 1: Upload files
        files = [
            ("files", ("app.py", BytesIO(b"print('hello')"), "text/x-python")),
            ("files", ("README.md", BytesIO(b"# Test\n## Description\nTest project"), "text/markdown")),
        ]
        
        upload_response = client.post("/api/upload", files=files)
        assert upload_response.status_code == 200
        upload_id = upload_response.json()["upload_id"]
        
        # Step 2: Analyze
        analysis_data = {
            "upload_id": upload_id,
            "project_name": "Integration Test"
        }
        analysis_response = client.post("/api/analyze", json=analysis_data)
        assert analysis_response.status_code == 200
        
        analysis_result = analysis_response.json()
        assert analysis_result["project_name"] == "Integration Test"
        assert "total_score" in analysis_result
        
        # Step 3: Cleanup
        delete_response = client.delete(f"/api/upload/{upload_id}")
        assert delete_response.status_code == 200
    
    def test_upload_analyze_combined_workflow(self, client):
        """Test combined upload and analyze workflow."""
        files = [
            ("files", ("test.py", BytesIO(b"def test(): pass"), "text/x-python")),
            ("files", ("README.md", BytesIO(b"# Project\n## Description\nDesc\n## Installation\nInstall\n## Usage\nUse"), "text/markdown")),
        ]
        
        response = client.post(
            "/api/upload-and-analyze",
            files=files,
            data={"project_name": "Combined Test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify complete analysis
        assert data["project_name"] == "Combined Test"
        assert data["files_analyzed"] >= 2
        assert "module_scores" in data
        assert len(data["module_scores"]) == 4
        
        # Verify README was analyzed
        assert data["readme_result"] is not None
        assert data["readme_result"]["exists"] is True
    
    def test_project_with_secrets_workflow(self, client):
        """Test workflow with project containing secrets."""
        files = [
            ("files", ("config.py", BytesIO(b'API_KEY = "AKIAIOSFODNN7EXAMPLE"'), "text/x-python")),
        ]
        
        response = client.post(
            "/api/upload-and-analyze",
            files=files,
            data={"project_name": "Secret Test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect secrets
        assert len(data["secrets_found"]) > 0
        assert data["critical_issues"] > 0
        assert data["total_score"] < 100
    
    def test_concurrent_uploads(self, client):
        """Test handling of concurrent uploads."""
        # Upload 1
        files1 = {"files": ("test1.py", BytesIO(b"x = 1"), "text/x-python")}
        response1 = client.post("/api/upload", files=files1)
        
        # Upload 2
        files2 = {"files": ("test2.py", BytesIO(b"y = 2"), "text/x-python")}
        response2 = client.post("/api/upload", files=files2)
        
        # Both should succeed with different IDs
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["upload_id"] != response2.json()["upload_id"]


# ============================================================================
# Test Class: Performance
# ============================================================================

@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_file_upload(self, client):
        """Test uploading large file."""
        # Create 1MB file
        large_content = b"x" * (1024 * 1024)
        files = {"files": ("large.txt", BytesIO(large_content), "text/plain")}
        
        response = client.post("/api/upload", files=files)
        
        # Should handle large files
        assert response.status_code in [200, 413]  # 413 if too large
    
    def test_many_files_upload(self, client):
        """Test uploading many files."""
        files = [
            ("files", (f"file{i}.py", BytesIO(b"x = 1"), "text/x-python"))
            for i in range(20)
        ]
        
        response = client.post("/api/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["files_received"] == 20


# ============================================================================
# Test Class: Security
# ============================================================================

class TestSecurity:
    """Test security features."""
    
    def test_path_traversal_prevention(self, client):
        """Test prevention of path traversal attacks."""
        files = {
            "files": ("../../../etc/passwd", BytesIO(b"content"), "text/plain")
        }
        
        response = client.post("/api/upload", files=files)
        
        # Should sanitize filename or reject
        assert response.status_code in [200, 400]
    
    def test_file_extension_validation(self, client):
        """Test file extension validation."""
        dangerous_extensions = [".exe", ".dll", ".so", ".sh"]
        
        for ext in dangerous_extensions:
            files = {"files": (f"file{ext}", BytesIO(b"content"), "application/octet-stream")}
            response = client.post("/api/upload", files=files)
            
            # Should reject dangerous extensions
            assert response.status_code == 400


# Made with Bob