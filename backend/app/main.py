"""
Main FastAPI application for PolicyPilot backend.
"""
import uuid
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, ensure_directories
from app.models import (
    UploadResponse,
    AnalysisRequest,
    AnalysisResult,
    HealthResponse,
    ErrorResponse
)
from app.services import (
    file_handler,
    scoring_engine,
    report_generator
)


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="IBM watsonx Policy Compliance Checker - Analyze projects for security and documentation compliance",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    ensure_directories()
    print(f"🚀 {settings.app_name} v{settings.app_version} started")
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"📊 Reports directory: {settings.reports_dir}")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )


@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload project files for analysis.
    
    Args:
        files: List of files to upload
        
    Returns:
        Upload response with upload ID
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        # Save uploaded files
        upload_id, upload_path = await file_handler.save_upload(files)
        
        # Count processed files
        processed_files = file_handler.list_files(upload_path)
        
        return UploadResponse(
            success=True,
            message="Files uploaded successfully",
            upload_id=upload_id,
            files_received=len(files),
            files_processed=len(processed_files)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_project(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze uploaded project files.
    
    Args:
        request: Analysis request with upload ID
        background_tasks: Background tasks for cleanup
        
    Returns:
        Analysis results
    """
    try:
        # Get upload path
        upload_path = file_handler.get_upload_path(request.upload_id)
        
        # Run analysis
        result = scoring_engine.analyze_project(
            directory=upload_path,
            project_name=request.project_name or "Unnamed Project"
        )
        
        # Generate reports in background
        report_id = request.upload_id
        background_tasks.add_task(
            generate_reports_background,
            result,
            report_id
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/upload-and-analyze", response_model=AnalysisResult)
async def upload_and_analyze(
    files: List[UploadFile] = File(...),
    project_name: str = "Unnamed Project"
):
    """
    Upload files and analyze in one request.
    
    Args:
        files: List of files to upload
        project_name: Name of the project
        
    Returns:
        Analysis results
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        # Upload files
        upload_id, upload_path = await file_handler.save_upload(files)
        
        # Run analysis
        result = scoring_engine.analyze_project(
            directory=upload_path,
            project_name=project_name
        )
        
        # Generate reports
        report_id = upload_id
        await generate_reports_background(result, report_id)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")


@app.get("/api/report/{report_id}/{format}")
async def get_report(report_id: str, format: str):
    """
    Download generated report.
    
    Args:
        report_id: Report identifier
        format: Report format (json, html, md)
        
    Returns:
        Report file
    """
    if format not in ['json', 'html', 'md']:
        raise HTTPException(status_code=400, detail="Invalid format. Use: json, html, or md")
    
    report_path = report_generator.get_report_path(report_id, format)
    
    if not report_path:
        raise HTTPException(status_code=404, detail="Report not found")
    
    media_types = {
        'json': 'application/json',
        'html': 'text/html',
        'md': 'text/markdown'
    }
    
    return FileResponse(
        path=report_path,
        media_type=media_types[format],
        filename=f"policypilot_report_{report_id}.{format}"
    )


@app.delete("/api/upload/{upload_id}")
async def delete_upload(upload_id: str):
    """
    Delete uploaded files.
    
    Args:
        upload_id: Upload identifier
        
    Returns:
        Success message
    """
    try:
        file_handler.cleanup_upload(upload_id)
        return {"success": True, "message": "Upload deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@app.get("/api/config")
async def get_config():
    """
    Get current configuration (non-sensitive).
    
    Returns:
        Configuration details
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "max_upload_size_mb": settings.max_upload_size / (1024 * 1024),
        "allowed_extensions": settings.allowed_extensions,
        "pass_threshold": settings.pass_threshold,
        "warning_threshold": settings.warning_threshold,
        "scoring_weights": settings.scoring_weights
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=str(exc)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).model_dump()
    )


async def generate_reports_background(result: AnalysisResult, report_id: str):
    """
    Generate all report formats in background.
    
    Args:
        result: Analysis results
        report_id: Report identifier
    """
    try:
        report_generator.generate_json_report(result, report_id)
        report_generator.generate_html_report(result, report_id)
        report_generator.generate_markdown_report(result, report_id)
    except Exception as e:
        print(f"Error generating reports: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

# Made with Bob
