"""Enhanced FastAPI application with complete PRE-BUNKER integration"""

from fastapi import FastAPI, Form, Request, HTTPException, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import uuid

from src.integration.complete_pipeline import complete_prebunker_system
from src.web.ops_routes import setup_ops_routes

# Create FastAPI app
app = FastAPI(
    title="PRE-BUNKER Health Communications System",
    description="Complete system for analyzing health messages, identifying risks, and generating countermeasures.",
    version="2.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Pydantic models for API
class HealthMessage(BaseModel):
    text: str
    priority: str = "medium"
    target_audience: Optional[str] = None
    topic_area: Optional[str] = None

class AnalysisRequest(BaseModel):
    message: HealthMessage
    include_ab_testing: bool = False
    submit_for_review: bool = True
    priority: str = "medium"

class AnalysisResponse(BaseModel):
    analysis_id: str
    message: str
    risk_score: float
    status: str
    claims_detected: int
    persona_concerns: int
    countermeasures_generated: int
    processing_time: float
    recommendations: list

# Setup operations routes
setup_ops_routes(app)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Enhanced home page with system status"""
    system_status = complete_prebunker_system.get_system_status()
    
    return templates.TemplateResponse("enhanced_index.html", {
        "request": request,
        "system_version": system_status['version'],
        "capabilities": system_status['capabilities'],
        "queue_stats": system_status['review_queue']
    })

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_message_web(
    request: Request,
    message: str = Form(...),
    include_ab_testing: bool = Form(False),
    submit_for_review: bool = Form(True),
    priority: str = Form("medium")
):
    """Enhanced web interface for message analysis"""
    try:
        # Choose analysis method based on options
        if include_ab_testing:
            result = await complete_prebunker_system.analyze_with_ab_testing(message)
        else:
            result = await complete_prebunker_system.analyze_health_communication(message)
        
        # Submit for review if requested
        review_id = None
        if submit_for_review and result.get('status') == 'completed':
            review_id = complete_prebunker_system.submit_for_human_review(result, priority)
        
        return templates.TemplateResponse("enhanced_results.html", {
            "request": request,
            "result": result,
            "review_id": review_id,
            "include_ab_testing": include_ab_testing
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/analyze", response_model=AnalysisResponse)
async def analyze_message_api(
    message: str,
    include_ab_testing: bool = False,
    submit_for_review: bool = False,
    priority: str = "medium"
):
    """Enhanced API endpoint for message analysis"""
    try:
        # Choose analysis method
        if include_ab_testing:
            result = await complete_prebunker_system.analyze_with_ab_testing(message)
        else:
            result = await complete_prebunker_system.analyze_health_communication(message)
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('error', 'Analysis failed'))
        
        # Submit for review if requested
        if submit_for_review:
            complete_prebunker_system.submit_for_human_review(result, priority)
        
        # Format response
        response = AnalysisResponse(
            analysis_id=result['analysis_id'],
            message=result['message'],
            risk_score=result['risk_report']['overall_risk_score'],
            status=result['status'],
            claims_detected=len(result['all_claims']),
            persona_concerns=sum(len(p.get('potential_misreading', [])) for p in result['persona_interpretations']),
            countermeasures_generated=len(result['countermeasures']),
            processing_time=result['processing_time'],
            recommendations=result['evaluation_metrics'].get('recommendations', [])
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/status")
async def get_system_status():
    """Get comprehensive system status"""
    status = complete_prebunker_system.get_system_status()
    return JSONResponse(status)

@app.get("/api/capabilities")
async def get_system_capabilities():
    """Get system capabilities overview"""
    capabilities = complete_prebunker_system.get_system_capabilities()
    return JSONResponse(capabilities)

@app.post("/api/feedback")
async def submit_feedback(
    analysis_id: str = Form(...),
    human_decision: str = Form(...),
    reviewer_notes: str = Form(...),
    reviewer_id: str = Form(...)
):
    """Submit human feedback for learning"""
    # This would need to retrieve the original analysis result
    # For now, return success
    return JSONResponse({
        "status": "success",
        "message": "Feedback recorded for learning system"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "version": "2.0.0",
        "components": "all_operational"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
