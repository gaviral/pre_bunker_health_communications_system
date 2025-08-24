"""Basic web interface for PRE-BUNKER health communications analysis"""

import os
import time
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

# Set OpenAI API key for local development
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-dummy-for-local"

from src.orchestration.pipeline import PrebunkerPipeline
from src.orchestration.risk_reporter import RiskReporter

app = FastAPI(title="PRE-BUNKER Health Communications", version="1.11.0")
templates = Jinja2Templates(directory="templates")

# Global instances
pipeline = PrebunkerPipeline()
risk_reporter = RiskReporter()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with message input form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_message(request: Request, message: str = Form(...)):
    """Analyze health message and return comprehensive risk report"""
    
    if not message.strip():
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Please enter a health message to analyze"
        })
    
    try:
        start_time = time.time()
        
        # Process message through pipeline
        pipeline_result = await pipeline.process_message(message, {'detailed_logging': False})
        
        # Generate enhanced risk report
        risk_report = await risk_reporter.compile_risk_report(pipeline_result)
        
        processing_time = time.time() - start_time
        
        return templates.TemplateResponse("results.html", {
            "request": request,
            "message": message,
            "pipeline_result": pipeline_result,
            "risk_report": risk_report,
            "processing_time": round(processing_time, 2)
        })
        
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Analysis failed: {str(e)}"
        })

@app.get("/api/analyze")
async def api_analyze(message: str):
    """API endpoint for programmatic access"""
    
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        start_time = time.time()
        
        # Process message through pipeline
        pipeline_result = await pipeline.process_message(message, {'detailed_logging': False})
        
        # Generate enhanced risk report
        risk_report = await risk_reporter.compile_risk_report(pipeline_result)
        
        processing_time = time.time() - start_time
        
        return {
            "message": message,
            "processing_time": round(processing_time, 2),
            "pipeline_result": pipeline_result,
            "risk_report": risk_report,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.11.0"}

if __name__ == "__main__":
    uvicorn.run(
        "src.web.app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
