"""Operations dashboard routes for FastAPI"""

from fastapi import Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from src.orchestration.pipeline import PrebunkerPipeline
from src.ops.dashboard import message_review_queue, workflow_manager, dashboard_generator
from datetime import datetime
import uuid

# Simple HTTP Basic Auth for ops dashboard
security = HTTPBasic()

def verify_ops_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Simple credential verification for ops dashboard"""
    # In production, use proper authentication
    if credentials.username != "admin" or credentials.password != "admin":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username

def setup_ops_routes(app):
    """Setup operations dashboard routes"""
    
    @app.get("/ops/dashboard", response_class=HTMLResponse)
    async def ops_dashboard(username: str = Depends(verify_ops_credentials)):
        """Main operations dashboard"""
        dashboard_html = dashboard_generator.generate_main_dashboard()
        return HTMLResponse(dashboard_html)
    
    @app.get("/ops/detail/{message_id}", response_class=HTMLResponse)
    async def message_detail(message_id: str, username: str = Depends(verify_ops_credentials)):
        """Detailed view of specific message"""
        detail_html = dashboard_generator.generate_detail_view(message_id)
        return HTMLResponse(detail_html)
    
    @app.post("/ops/submit")
    async def submit_for_review(
        message: str = Form(...), 
        priority: str = Form(...),
        username: str = Depends(verify_ops_credentials)
    ):
        """Submit message for review"""
        try:
            # Process message through pipeline
            pipeline = PrebunkerPipeline()
            analysis_result = await pipeline.process_message(message)
            
            # Generate unique message ID
            message_id = f"msg_{uuid.uuid4().hex[:8]}"
            
            # Add to review queue
            message_review_queue.add_to_queue(message_id, message, analysis_result, priority)
            
            return JSONResponse({
                "status": "success",
                "message": "Message submitted for review", 
                "id": message_id,
                "redirect": f"/ops/detail/{message_id}"
            })
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
    
    @app.post("/ops/approve/{message_id}")
    async def approve_message(
        message_id: str,
        reviewer: str = Form(...),
        notes: str = Form(...),
        approved_version: str = Form(...),
        username: str = Depends(verify_ops_credentials)
    ):
        """Approve a message"""
        success = message_review_queue.approve_message(message_id, reviewer, notes, approved_version)
        
        if success:
            return JSONResponse({
                "status": "success",
                "message": f"Message {message_id} approved",
                "redirect": "/ops/dashboard"
            })
        else:
            raise HTTPException(status_code=404, detail="Message not found")
    
    @app.post("/ops/reject/{message_id}")
    async def reject_message(
        message_id: str,
        reviewer: str = Form(...),
        rejection_reason: str = Form(...),
        username: str = Depends(verify_ops_credentials)
    ):
        """Reject a message"""
        success = message_review_queue.reject_message(message_id, reviewer, rejection_reason)
        
        if success:
            return JSONResponse({
                "status": "success",
                "message": f"Message {message_id} rejected",
                "redirect": "/ops/dashboard"
            })
        else:
            raise HTTPException(status_code=404, detail="Message not found")
    
    @app.post("/ops/revision/{message_id}")
    async def request_revision(
        message_id: str,
        reviewer: str = Form(...),
        revision_notes: str = Form(...),
        username: str = Depends(verify_ops_credentials)
    ):
        """Request revision of a message"""
        success = message_review_queue.request_revision(message_id, reviewer, revision_notes)
        
        if success:
            return JSONResponse({
                "status": "success",
                "message": f"Revision requested for message {message_id}",
                "redirect": "/ops/dashboard"
            })
        else:
            raise HTTPException(status_code=404, detail="Message not found")
    
    @app.get("/ops/api/stats")
    async def get_queue_stats(username: str = Depends(verify_ops_credentials)):
        """Get queue statistics API"""
        stats = message_review_queue.get_queue_stats()
        return JSONResponse(stats)
    
    @app.get("/ops/api/pending")
    async def get_pending_items(
        sort_by: str = "priority",
        username: str = Depends(verify_ops_credentials)
    ):
        """Get pending review items API"""
        pending = message_review_queue.get_pending_items(sort_by=sort_by)
        return JSONResponse({"pending_items": pending})
    
    @app.get("/ops/api/workflow/{message_id}")
    async def get_workflow_recommendation(
        message_id: str,
        username: str = Depends(verify_ops_credentials)
    ):
        """Get workflow recommendation for specific message"""
        item = message_review_queue.get_item_by_id(message_id)
        if not item:
            raise HTTPException(status_code=404, detail="Message not found")
        
        workflow = workflow_manager.determine_workflow(item['analysis'])
        return JSONResponse(workflow)
