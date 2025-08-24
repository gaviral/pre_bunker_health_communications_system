"""Operations dashboard for human review and workflow management"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
import uuid

class MessageReviewQueue:
    """Message review queue for human oversight"""
    
    def __init__(self):
        self.queue = []
        self.reviewed = []
        self.approved = []
        self.rejected = []
    
    def add_to_queue(self, message_id: str, original_text: str, analysis_result: Dict, priority: str = 'medium') -> str:
        """Add message to review queue"""
        queue_item = {
            'id': message_id,
            'original_text': original_text,
            'analysis': analysis_result,
            'priority': priority,
            'submitted_at': datetime.now().isoformat(),
            'status': 'pending_review',
            'reviewer': None,
            'review_notes': None,
            'risk_score': analysis_result.get('risk_report', {}).get('overall_risk_score', 0.0),
            'concern_count': len(analysis_result.get('claims', [])),
            'countermeasures_count': len(analysis_result.get('countermeasures', {}))
        }
        self.queue.append(queue_item)
        return message_id
    
    def get_pending_items(self, sort_by: str = 'priority') -> List[Dict]:
        """Get pending review items, optionally sorted"""
        pending = [item for item in self.queue if item['status'] == 'pending_review']
        
        if sort_by == 'priority':
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            pending.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        elif sort_by == 'risk':
            pending.sort(key=lambda x: x['risk_score'], reverse=True)
        elif sort_by == 'date':
            pending.sort(key=lambda x: x['submitted_at'], reverse=True)
        
        return pending
    
    def get_high_priority_items(self) -> List[Dict]:
        """Get only high priority pending items"""
        return [item for item in self.queue 
                if item['status'] == 'pending_review' and item['priority'] == 'high']
    
    def approve_message(self, message_id: str, reviewer: str, notes: str, approved_version: str) -> bool:
        """Approve a message with reviewer notes"""
        for item in self.queue:
            if item['id'] == message_id:
                item['status'] = 'approved'
                item['reviewer'] = reviewer
                item['review_notes'] = notes
                item['approved_version'] = approved_version
                item['reviewed_at'] = datetime.now().isoformat()
                self.approved.append(item)
                return True
        return False
    
    def reject_message(self, message_id: str, reviewer: str, rejection_reason: str) -> bool:
        """Reject a message with reason"""
        for item in self.queue:
            if item['id'] == message_id:
                item['status'] = 'rejected'
                item['reviewer'] = reviewer
                item['rejection_reason'] = rejection_reason
                item['reviewed_at'] = datetime.now().isoformat()
                self.rejected.append(item)
                return True
        return False
    
    def request_revision(self, message_id: str, reviewer: str, revision_notes: str) -> bool:
        """Request revision of a message"""
        for item in self.queue:
            if item['id'] == message_id:
                item['status'] = 'revision_requested'
                item['reviewer'] = reviewer
                item['revision_notes'] = revision_notes
                item['reviewed_at'] = datetime.now().isoformat()
                return True
        return False
    
    def get_item_by_id(self, message_id: str) -> Optional[Dict]:
        """Get specific queue item by ID"""
        for item in self.queue:
            if item['id'] == message_id:
                return item
        return None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        total_items = len(self.queue)
        pending_count = len([item for item in self.queue if item['status'] == 'pending_review'])
        approved_count = len(self.approved)
        rejected_count = len(self.rejected)
        revision_count = len([item for item in self.queue if item['status'] == 'revision_requested'])
        
        priority_counts = {
            'high': len([item for item in self.queue if item['priority'] == 'high' and item['status'] == 'pending_review']),
            'medium': len([item for item in self.queue if item['priority'] == 'medium' and item['status'] == 'pending_review']),
            'low': len([item for item in self.queue if item['priority'] == 'low' and item['status'] == 'pending_review'])
        }
        
        avg_risk_score = 0.0
        if pending_count > 0:
            pending_items = [item for item in self.queue if item['status'] == 'pending_review']
            avg_risk_score = sum(item['risk_score'] for item in pending_items) / len(pending_items)
        
        return {
            'total_items': total_items,
            'pending_review': pending_count,
            'approved': approved_count,
            'rejected': rejected_count,
            'revision_requested': revision_count,
            'priority_breakdown': priority_counts,
            'average_risk_score': round(avg_risk_score, 2),
            'queue_health': 'healthy' if pending_count < 10 else 'backlogged'
        }

class WorkflowManager:
    """Manage review workflow and routing"""
    
    def __init__(self):
        self.reviewers = {
            'health_expert': {'name': 'Dr. Health Expert', 'specialties': ['clinical', 'medical']},
            'comm_specialist': {'name': 'Communications Specialist', 'specialties': ['clarity', 'messaging']},
            'risk_assessor': {'name': 'Risk Assessment Lead', 'specialties': ['risk', 'safety']}
        }
        self.workflow_rules = {
            'high_risk': {'min_reviewers': 2, 'required_specialties': ['clinical', 'risk']},
            'medium_risk': {'min_reviewers': 1, 'required_specialties': ['clinical']},
            'low_risk': {'min_reviewers': 1, 'required_specialties': ['comm_specialist']}
        }
    
    def determine_workflow(self, analysis_result: Dict) -> Dict[str, Any]:
        """Determine appropriate workflow based on analysis"""
        risk_score = analysis_result.get('risk_report', {}).get('overall_risk_score', 0.0)
        claim_count = len(analysis_result.get('claims', []))
        concern_count = sum(len(interp.get('potential_misreading', [])) 
                          for interp in analysis_result.get('persona_interpretations', []))
        
        # Determine risk level
        if risk_score >= 0.7 or concern_count >= 10:
            risk_level = 'high_risk'
        elif risk_score >= 0.4 or concern_count >= 5:
            risk_level = 'medium_risk'
        else:
            risk_level = 'low_risk'
        
        workflow = self.workflow_rules[risk_level].copy()
        workflow['risk_level'] = risk_level
        workflow['recommended_reviewers'] = self._recommend_reviewers(workflow['required_specialties'])
        workflow['estimated_review_time'] = self._estimate_review_time(risk_level, claim_count)
        
        return workflow
    
    def _recommend_reviewers(self, required_specialties: List[str]) -> List[str]:
        """Recommend reviewers based on required specialties"""
        recommended = []
        for reviewer_id, reviewer_info in self.reviewers.items():
            if any(specialty in reviewer_info['specialties'] for specialty in required_specialties):
                recommended.append(reviewer_id)
        return recommended
    
    def _estimate_review_time(self, risk_level: str, claim_count: int) -> str:
        """Estimate time needed for review"""
        base_times = {
            'high_risk': 45,  # minutes
            'medium_risk': 25,
            'low_risk': 15
        }
        
        base_time = base_times[risk_level]
        additional_time = claim_count * 5  # 5 minutes per claim
        total_time = base_time + additional_time
        
        if total_time < 60:
            return f"{total_time} minutes"
        else:
            hours = total_time // 60
            minutes = total_time % 60
            return f"{hours}h {minutes}m"

class DashboardGenerator:
    """Generate HTML dashboard views"""
    
    def __init__(self, review_queue: MessageReviewQueue, workflow_manager: WorkflowManager):
        self.review_queue = review_queue
        self.workflow_manager = workflow_manager
    
    def generate_main_dashboard(self) -> str:
        """Generate main dashboard HTML"""
        stats = self.review_queue.get_queue_stats()
        pending_items = self.review_queue.get_pending_items(sort_by='priority')
        
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PRE-BUNKER Ops Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; min-width: 150px; }}
                .priority-high {{ border-left: 4px solid #ff4444; }}
                .priority-medium {{ border-left: 4px solid #ffaa00; }}
                .priority-low {{ border-left: 4px solid #44ff44; }}
                .review-item {{ border: 1px solid #eee; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .actions {{ margin-top: 10px; }}
                .button {{ padding: 8px 16px; margin-right: 10px; border: none; border-radius: 3px; cursor: pointer; }}
                .btn-approve {{ background-color: #4CAF50; color: white; }}
                .btn-reject {{ background-color: #f44336; color: white; }}
                .btn-revise {{ background-color: #ff9800; color: white; }}
            </style>
        </head>
        <body>
            <h1>PRE-BUNKER Operations Dashboard</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Queue Status</h3>
                    <p><strong>{stats['pending_review']}</strong> pending</p>
                    <p><strong>{stats['approved']}</strong> approved</p>
                    <p><strong>{stats['rejected']}</strong> rejected</p>
                    <p>Status: <strong>{stats['queue_health']}</strong></p>
                </div>
                <div class="stat-card">
                    <h3>Priority Breakdown</h3>
                    <p>High: <strong>{stats['priority_breakdown']['high']}</strong></p>
                    <p>Medium: <strong>{stats['priority_breakdown']['medium']}</strong></p>
                    <p>Low: <strong>{stats['priority_breakdown']['low']}</strong></p>
                </div>
                <div class="stat-card">
                    <h3>Risk Assessment</h3>
                    <p>Avg Risk Score: <strong>{stats['average_risk_score']}</strong></p>
                    <p>Total Items: <strong>{stats['total_items']}</strong></p>
                </div>
            </div>
            
            <h2>Pending Reviews ({len(pending_items)})</h2>
            {self._generate_review_items_html(pending_items)}
            
            <h2>Submit New Message</h2>
            <form action="/ops/submit" method="post">
                <textarea name="message" rows="5" cols="80" placeholder="Health message to review..." required></textarea><br><br>
                <label>Priority: </label>
                <select name="priority">
                    <option value="low">Low Priority</option>
                    <option value="medium" selected>Medium Priority</option>
                    <option value="high">High Priority</option>
                </select><br><br>
                <button type="submit" class="button btn-approve">Submit for Review</button>
            </form>
        </body>
        </html>
        """
        
        return dashboard_html
    
    def _generate_review_items_html(self, items: List[Dict]) -> str:
        """Generate HTML for review items"""
        if not items:
            return "<p>No pending reviews.</p>"
        
        items_html = ""
        for item in items:
            priority_class = f"priority-{item['priority']}"
            workflow = self.workflow_manager.determine_workflow(item['analysis'])
            
            items_html += f"""
            <div class="review-item {priority_class}">
                <h3>Message ID: {item['id']}</h3>
                <p><strong>Priority:</strong> {item['priority'].upper()}</p>
                <p><strong>Risk Score:</strong> {item['risk_score']:.2f}</p>
                <p><strong>Submitted:</strong> {item['submitted_at']}</p>
                <p><strong>Estimated Review Time:</strong> {workflow['estimated_review_time']}</p>
                
                <h4>Original Message:</h4>
                <p style="background: #f5f5f5; padding: 10px; border-radius: 3px;">{item['original_text']}</p>
                
                <h4>Analysis Summary:</h4>
                <p>Claims detected: {item['concern_count']}</p>
                <p>Countermeasures generated: {item['countermeasures_count']}</p>
                <p>Recommended reviewers: {', '.join(workflow['recommended_reviewers'])}</p>
                
                <div class="actions">
                    <button class="button btn-approve" onclick="approveMessage('{item['id']}')">Approve</button>
                    <button class="button btn-revise" onclick="requestRevision('{item['id']}')">Request Revision</button>
                    <button class="button btn-reject" onclick="rejectMessage('{item['id']}')">Reject</button>
                    <a href="/ops/detail/{item['id']}" style="margin-left: 20px;">View Details</a>
                </div>
            </div>
            """
        
        return items_html
    
    def generate_detail_view(self, message_id: str) -> str:
        """Generate detailed view for specific message"""
        item = self.review_queue.get_item_by_id(message_id)
        if not item:
            return "<html><body><h1>Message not found</h1></body></html>"
        
        analysis = item['analysis']
        workflow = self.workflow_manager.determine_workflow(analysis)
        
        # Format claims
        claims_html = ""
        for i, claim in enumerate(analysis.get('claims', []), 1):
            claims_html += f"<li>Claim {i}: {claim}</li>"
        
        # Format persona interpretations
        personas_html = ""
        for interp in analysis.get('persona_interpretations', []):
            concerns = interp.get('potential_misreading', [])
            concerns_text = ', '.join(concerns) if concerns else 'No concerns'
            personas_html += f"<li><strong>{interp['persona']}:</strong> {concerns_text}</li>"
        
        # Format countermeasures
        countermeasures_html = ""
        for persona, cm_data in analysis.get('countermeasures', {}).items():
            effectiveness = cm_data.get('effectiveness_score', 'N/A')
            countermeasures_html += f"<li><strong>{persona}</strong> (effectiveness: {effectiveness}): {cm_data.get('text', 'N/A')[:100]}...</li>"
        
        detail_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Message Detail - {message_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .priority-{item['priority']} {{ border-left: 4px solid {'#ff4444' if item['priority'] == 'high' else '#ffaa00' if item['priority'] == 'medium' else '#44ff44'}; }}
            </style>
        </head>
        <body>
            <h1>Message Review Detail</h1>
            <a href="/ops/dashboard">&larr; Back to Dashboard</a>
            
            <div class="section priority-{item['priority']}">
                <h2>Message Information</h2>
                <p><strong>ID:</strong> {item['id']}</p>
                <p><strong>Priority:</strong> {item['priority'].upper()}</p>
                <p><strong>Risk Score:</strong> {item['risk_score']:.2f}</p>
                <p><strong>Status:</strong> {item['status']}</p>
                <p><strong>Submitted:</strong> {item['submitted_at']}</p>
                <p><strong>Estimated Review Time:</strong> {workflow['estimated_review_time']}</p>
                <p><strong>Recommended Reviewers:</strong> {', '.join(workflow['recommended_reviewers'])}</p>
            </div>
            
            <div class="section">
                <h2>Original Message</h2>
                <p style="background: #f5f5f5; padding: 15px; border-radius: 3px; white-space: pre-wrap;">{item['original_text']}</p>
            </div>
            
            <div class="section">
                <h2>Claims Detected ({len(analysis.get('claims', []))})</h2>
                <ul>{claims_html}</ul>
            </div>
            
            <div class="section">
                <h2>Persona Interpretations</h2>
                <ul>{personas_html}</ul>
            </div>
            
            <div class="section">
                <h2>Countermeasures Generated ({len(analysis.get('countermeasures', {}))})</h2>
                <ul>{countermeasures_html}</ul>
            </div>
            
            <div class="section">
                <h2>Review Actions</h2>
                <form action="/ops/approve/{message_id}" method="post" style="margin: 10px 0;">
                    <h3>Approve Message</h3>
                    <input type="text" name="reviewer" placeholder="Your name" required style="width: 200px; margin-right: 10px;">
                    <textarea name="notes" placeholder="Approval notes..." rows="3" cols="50"></textarea><br>
                    <textarea name="approved_version" placeholder="Final approved version..." rows="5" cols="80" required></textarea><br>
                    <button type="submit" style="background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 3px;">Approve</button>
                </form>
                
                <form action="/ops/revision/{message_id}" method="post" style="margin: 10px 0;">
                    <h3>Request Revision</h3>
                    <input type="text" name="reviewer" placeholder="Your name" required style="width: 200px; margin-right: 10px;">
                    <textarea name="revision_notes" placeholder="Revision requirements..." rows="3" cols="50" required></textarea><br>
                    <button type="submit" style="background: #ff9800; color: white; padding: 10px 20px; border: none; border-radius: 3px;">Request Revision</button>
                </form>
                
                <form action="/ops/reject/{message_id}" method="post" style="margin: 10px 0;">
                    <h3>Reject Message</h3>
                    <input type="text" name="reviewer" placeholder="Your name" required style="width: 200px; margin-right: 10px;">
                    <textarea name="rejection_reason" placeholder="Rejection reason..." rows="3" cols="50" required></textarea><br>
                    <button type="submit" style="background: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 3px;">Reject</button>
                </form>
            </div>
        </body>
        </html>
        """
        
        return detail_html

# Global instances
message_review_queue = MessageReviewQueue()
workflow_manager = WorkflowManager()
dashboard_generator = DashboardGenerator(message_review_queue, workflow_manager)
