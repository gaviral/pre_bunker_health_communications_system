import time
import json
from datetime import datetime

class Tracer:
    def __init__(self):
        self.traces = []
    
    def start_trace(self, agent_name, operation):
        trace_id = f"{agent_name}_{int(time.time())}"
        trace = {
            "id": trace_id,
            "agent": agent_name,
            "operation": operation,
            "start_time": datetime.now().isoformat(),
            "events": []
        }
        self.traces.append(trace)
        return trace_id
    
    def add_event(self, trace_id, event_type, data):
        for trace in self.traces:
            if trace["id"] == trace_id:
                trace["events"].append({
                    "type": event_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })
    
    def end_trace(self, trace_id, result):
        for trace in self.traces:
            if trace["id"] == trace_id:
                trace["end_time"] = datetime.now().isoformat()
                trace["result"] = result
    
    def get_traces(self):
        return self.traces
    
    def get_dashboard_data(self):
        """Return formatted data for dashboard display"""
        dashboard = {
            "total_traces": len(self.traces),
            "agents": list(set(trace["agent"] for trace in self.traces)),
            "recent_traces": self.traces[-5:] if self.traces else [],
            "trace_summary": []
        }
        
        for trace in self.traces:
            duration = None
            if "end_time" in trace:
                start = datetime.fromisoformat(trace["start_time"])
                end = datetime.fromisoformat(trace["end_time"])
                duration = (end - start).total_seconds()
            
            dashboard["trace_summary"].append({
                "id": trace["id"],
                "agent": trace["agent"],
                "operation": trace["operation"],
                "duration": duration,
                "event_count": len(trace["events"]),
                "status": "completed" if "end_time" in trace else "running"
            })
        
        return dashboard

# Global tracer instance
tracer = Tracer()
