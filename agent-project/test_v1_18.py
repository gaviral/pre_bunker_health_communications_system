"""Test v1.18: Ops Dashboard"""

import os
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-dummy-for-local"

from src.ops.dashboard import MessageReviewQueue, WorkflowManager, DashboardGenerator
from datetime import datetime

def test_message_review_queue_initialization():
    """Test message review queue setup"""
    print("=== Testing MessageReviewQueue Initialization ===")
    
    queue = MessageReviewQueue()
    
    # Check initial state
    assert queue.queue == [], "Should start with empty queue"
    assert queue.reviewed == [], "Should start with empty reviewed list"
    assert queue.approved == [], "Should start with empty approved list"
    assert queue.rejected == [], "Should start with empty rejected list"
    
    print("✅ MessageReviewQueue initialized correctly")

def test_add_to_queue():
    """Test adding messages to review queue"""
    print("\n=== Testing Add to Queue ===")
    
    queue = MessageReviewQueue()
    
    # Sample analysis result
    analysis_result = {
        'claims': ['claim1', 'claim2'],
        'risk_report': {'overall_risk_score': 0.7},
        'countermeasures': {'VaccineHesitant': {'text': 'response'}}
    }
    
    # Add message to queue
    message_id = queue.add_to_queue(
        'test_msg_1', 
        'Sample health message', 
        analysis_result, 
        'high'
    )
    
    assert message_id == 'test_msg_1', "Should return correct message ID"
    assert len(queue.queue) == 1, "Should have one item in queue"
    
    item = queue.queue[0]
    assert item['id'] == 'test_msg_1', "Should have correct ID"
    assert item['original_text'] == 'Sample health message', "Should store original text"
    assert item['priority'] == 'high', "Should store priority"
    assert item['status'] == 'pending_review', "Should start with pending status"
    assert item['risk_score'] == 0.7, "Should extract risk score"
    assert item['concern_count'] == 2, "Should count claims"
    assert item['countermeasures_count'] == 1, "Should count countermeasures"
    
    print(f"✅ Added message {message_id} to queue with risk score {item['risk_score']}")

def test_queue_operations():
    """Test queue operations - approve, reject, revision"""
    print("\n=== Testing Queue Operations ===")
    
    queue = MessageReviewQueue()
    
    # Add test messages
    analysis_result = {
        'claims': ['claim1'],
        'risk_report': {'overall_risk_score': 0.5},
        'countermeasures': {}
    }
    
    queue.add_to_queue('msg_1', 'Message 1', analysis_result, 'medium')
    queue.add_to_queue('msg_2', 'Message 2', analysis_result, 'low')
    queue.add_to_queue('msg_3', 'Message 3', analysis_result, 'high')
    
    # Test approval
    success = queue.approve_message('msg_1', 'Dr. Smith', 'Looks good', 'Approved version')
    assert success, "Should successfully approve message"
    
    item = queue.get_item_by_id('msg_1')
    assert item['status'] == 'approved', "Should update status to approved"
    assert item['reviewer'] == 'Dr. Smith', "Should record reviewer"
    assert len(queue.approved) == 1, "Should add to approved list"
    
    # Test rejection
    success = queue.reject_message('msg_2', 'Dr. Jones', 'Contains misinformation')
    assert success, "Should successfully reject message"
    
    item = queue.get_item_by_id('msg_2')
    assert item['status'] == 'rejected', "Should update status to rejected"
    assert item['rejection_reason'] == 'Contains misinformation', "Should record reason"
    assert len(queue.rejected) == 1, "Should add to rejected list"
    
    # Test revision request
    success = queue.request_revision('msg_3', 'Dr. Brown', 'Needs more evidence citations')
    assert success, "Should successfully request revision"
    
    item = queue.get_item_by_id('msg_3')
    assert item['status'] == 'revision_requested', "Should update status"
    assert item['revision_notes'] == 'Needs more evidence citations', "Should record notes"
    
    print("✅ Queue operations (approve, reject, revision) working correctly")

def test_queue_filtering_and_sorting():
    """Test queue filtering and sorting"""
    print("\n=== Testing Queue Filtering and Sorting ===")
    
    queue = MessageReviewQueue()
    
    # Add messages with different priorities and risk scores
    analysis_high_risk = {'claims': ['claim1'], 'risk_report': {'overall_risk_score': 0.9}, 'countermeasures': {}}
    analysis_med_risk = {'claims': ['claim1'], 'risk_report': {'overall_risk_score': 0.5}, 'countermeasures': {}}
    analysis_low_risk = {'claims': ['claim1'], 'risk_report': {'overall_risk_score': 0.2}, 'countermeasures': {}}
    
    queue.add_to_queue('msg_high', 'High risk message', analysis_high_risk, 'high')
    queue.add_to_queue('msg_med', 'Medium risk message', analysis_med_risk, 'medium')
    queue.add_to_queue('msg_low', 'Low risk message', analysis_low_risk, 'low')
    
    # Test getting pending items sorted by priority
    pending_priority = queue.get_pending_items(sort_by='priority')
    assert len(pending_priority) == 3, "Should have 3 pending items"
    assert pending_priority[0]['priority'] == 'high', "First item should be high priority"
    assert pending_priority[1]['priority'] == 'medium', "Second item should be medium priority"
    assert pending_priority[2]['priority'] == 'low', "Third item should be low priority"
    
    # Test getting pending items sorted by risk
    pending_risk = queue.get_pending_items(sort_by='risk')
    assert pending_risk[0]['risk_score'] == 0.9, "First item should be highest risk"
    assert pending_risk[1]['risk_score'] == 0.5, "Second item should be medium risk"
    assert pending_risk[2]['risk_score'] == 0.2, "Third item should be lowest risk"
    
    # Test getting high priority items only
    high_priority = queue.get_high_priority_items()
    assert len(high_priority) == 1, "Should have 1 high priority item"
    assert high_priority[0]['id'] == 'msg_high', "Should be the high priority message"
    
    print("✅ Queue filtering and sorting working correctly")

def test_queue_statistics():
    """Test queue statistics calculation"""
    print("\n=== Testing Queue Statistics ===")
    
    queue = MessageReviewQueue()
    
    # Add various messages and process some
    analysis_result = {'claims': ['claim1'], 'risk_report': {'overall_risk_score': 0.6}, 'countermeasures': {}}
    
    queue.add_to_queue('msg_1', 'Message 1', analysis_result, 'high')
    queue.add_to_queue('msg_2', 'Message 2', analysis_result, 'medium')
    queue.add_to_queue('msg_3', 'Message 3', analysis_result, 'low')
    queue.add_to_queue('msg_4', 'Message 4', analysis_result, 'medium')
    
    # Process some messages
    queue.approve_message('msg_1', 'Dr. Smith', 'Good', 'Approved')
    queue.reject_message('msg_2', 'Dr. Jones', 'Bad')
    
    # Get statistics
    stats = queue.get_queue_stats()
    
    print(f"Queue statistics: {stats}")
    
    assert stats['total_items'] == 4, "Should count total items"
    assert stats['pending_review'] == 2, "Should count pending items"
    assert stats['approved'] == 1, "Should count approved items"
    assert stats['rejected'] == 1, "Should count rejected items"
    assert stats['priority_breakdown']['high'] == 0, "High priority pending should be 0"
    assert stats['priority_breakdown']['medium'] == 1, "Medium priority pending should be 1"
    assert stats['priority_breakdown']['low'] == 1, "Low priority pending should be 1"
    assert stats['average_risk_score'] == 0.6, "Should calculate average risk score"
    assert stats['queue_health'] in ['healthy', 'backlogged'], "Should assess queue health"
    
    print("✅ Queue statistics calculation working correctly")

def test_workflow_manager():
    """Test workflow management and routing"""
    print("\n=== Testing WorkflowManager ===")
    
    workflow_manager = WorkflowManager()
    
    # Test high risk workflow
    high_risk_analysis = {
        'claims': ['claim1', 'claim2'],
        'risk_report': {'overall_risk_score': 0.8},
        'persona_interpretations': [
            {'persona': 'VaccineHesitant', 'potential_misreading': ['concern1', 'concern2', 'concern3']},
            {'persona': 'HealthAnxious', 'potential_misreading': ['worry1', 'worry2']}
        ]
    }
    
    high_risk_workflow = workflow_manager.determine_workflow(high_risk_analysis)
    
    print(f"High risk workflow: {high_risk_workflow}")
    
    assert high_risk_workflow['risk_level'] == 'high_risk', "Should identify as high risk"
    assert high_risk_workflow['min_reviewers'] == 2, "Should require 2 reviewers"
    assert 'clinical' in high_risk_workflow['required_specialties'], "Should require clinical expertise"
    assert 'risk' in high_risk_workflow['required_specialties'], "Should require risk expertise"
    assert len(high_risk_workflow['recommended_reviewers']) >= 1, "Should recommend reviewers"
    assert 'estimated_review_time' in high_risk_workflow, "Should estimate review time"
    
    # Test medium risk workflow
    medium_risk_analysis = {
        'claims': ['claim1'],
        'risk_report': {'overall_risk_score': 0.5},
        'persona_interpretations': [
            {'persona': 'VaccineHesitant', 'potential_misreading': ['concern1']}
        ]
    }
    
    medium_risk_workflow = workflow_manager.determine_workflow(medium_risk_analysis)
    
    assert medium_risk_workflow['risk_level'] == 'medium_risk', "Should identify as medium risk"
    assert medium_risk_workflow['min_reviewers'] == 1, "Should require 1 reviewer"
    
    # Test low risk workflow
    low_risk_analysis = {
        'claims': ['claim1'],
        'risk_report': {'overall_risk_score': 0.2},
        'persona_interpretations': [
            {'persona': 'VaccineHesitant', 'potential_misreading': []}
        ]
    }
    
    low_risk_workflow = workflow_manager.determine_workflow(low_risk_analysis)
    
    assert low_risk_workflow['risk_level'] == 'low_risk', "Should identify as low risk"
    assert low_risk_workflow['min_reviewers'] == 1, "Should require 1 reviewer"
    
    print("✅ WorkflowManager routing working correctly")

def test_dashboard_generator():
    """Test HTML dashboard generation"""
    print("\n=== Testing DashboardGenerator ===")
    
    queue = MessageReviewQueue()
    workflow_manager = WorkflowManager()
    dashboard_gen = DashboardGenerator(queue, workflow_manager)
    
    # Add some test data
    analysis_result = {
        'claims': ['claim1', 'claim2'],
        'risk_report': {'overall_risk_score': 0.6},
        'countermeasures': {'VaccineHesitant': {'text': 'response'}},
        'persona_interpretations': [
            {'persona': 'VaccineHesitant', 'potential_misreading': ['concern1']}
        ]
    }
    
    queue.add_to_queue('test_msg', 'Sample message for testing dashboard', analysis_result, 'medium')
    
    # Test main dashboard generation
    dashboard_html = dashboard_gen.generate_main_dashboard()
    
    # Basic HTML structure checks
    assert '<!DOCTYPE html>' in dashboard_html, "Should be valid HTML"
    assert 'PRE-BUNKER Operations Dashboard' in dashboard_html, "Should have title"
    assert 'test_msg' in dashboard_html, "Should show message ID"
    assert 'Sample message for testing dashboard' in dashboard_html, "Should show message text"
    assert 'medium' in dashboard_html.lower(), "Should show priority"
    
    # Test detail view generation
    detail_html = dashboard_gen.generate_detail_view('test_msg')
    
    assert 'Message Review Detail' in detail_html, "Should have detail title"
    assert 'test_msg' in detail_html, "Should show message ID"
    assert 'Claims Detected' in detail_html, "Should show claims section"
    assert 'Persona Interpretations' in detail_html, "Should show personas section"
    assert 'Review Actions' in detail_html, "Should show action forms"
    
    # Test non-existent message
    not_found_html = dashboard_gen.generate_detail_view('non_existent')
    assert 'Message not found' in not_found_html, "Should handle non-existent message"
    
    print("✅ DashboardGenerator HTML generation working correctly")

def test_integration_workflow():
    """Test complete workflow from submission to review"""
    print("\n=== Testing Complete Integration Workflow ===")
    
    queue = MessageReviewQueue()
    workflow_manager = WorkflowManager()
    
    # Step 1: Submit message for review
    analysis_result = {
        'claims': ['Vaccines are 100% safe', 'No side effects ever occur'],
        'risk_report': {'overall_risk_score': 0.8},
        'countermeasures': {
            'VaccineHesitant': {'text': 'Actually, vaccines have rare side effects...', 'effectiveness_score': 0.7}
        },
        'persona_interpretations': [
            {'persona': 'VaccineHesitant', 'potential_misreading': ['safety concern', 'absolutist language']},
            {'persona': 'HealthAnxious', 'potential_misreading': ['worry about hidden risks']}
        ]
    }
    
    message_id = queue.add_to_queue(
        'integration_test',
        'Vaccines are 100% safe and have no side effects',
        analysis_result,
        'high'
    )
    
    # Step 2: Determine workflow
    workflow = workflow_manager.determine_workflow(analysis_result)
    
    assert workflow['risk_level'] == 'high_risk', "Should route as high risk"
    assert workflow['min_reviewers'] == 2, "Should require multiple reviewers"
    
    # Step 3: Review process
    pending = queue.get_pending_items()
    assert len(pending) == 1, "Should have one pending item"
    assert pending[0]['id'] == message_id, "Should be our test message"
    
    # Step 4: Approve message
    approved = queue.approve_message(
        message_id, 
        'Dr. Clinical Expert', 
        'Message needs revision to remove absolutist language',
        'Vaccines are generally safe and effective, with rare side effects that are closely monitored'
    )
    
    assert approved, "Should successfully approve message"
    
    # Step 5: Verify final state
    stats = queue.get_queue_stats()
    assert stats['approved'] == 1, "Should have one approved message"
    assert stats['pending_review'] == 0, "Should have no pending messages"
    
    approved_item = queue.get_item_by_id(message_id)
    assert approved_item['status'] == 'approved', "Should be approved"
    assert approved_item['reviewer'] == 'Dr. Clinical Expert', "Should record reviewer"
    
    print("✅ Complete integration workflow working correctly")

if __name__ == "__main__":
    test_message_review_queue_initialization()
    test_add_to_queue()
    test_queue_operations()
    test_queue_filtering_and_sorting()
    test_queue_statistics()
    test_workflow_manager()
    test_dashboard_generator()
    test_integration_workflow()
    
    print("\n✅ v1.18 Ops Dashboard - Human review queue and workflow management system")
