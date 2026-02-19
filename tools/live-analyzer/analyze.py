#!/usr/bin/env python3
"""
Live Analyzer - Performance and Usage Tracking for HyperSync Components

This tool monitors component usage, tracks performance metrics, and collects
feedback for the live development cycle: Build → Assemble → Use → Analyze → Iterate
"""

import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class LiveAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.components_dir = project_root / "components"
        self.workspace_dir = project_root / "workspace"
        
    def analyze_build(self, build_id: str, component_name: str = None) -> Dict[str, Any]:
        """Analyze a specific build in workspace/assembly"""
        build_path = self.workspace_dir / "assembly" / build_id
        
        if not build_path.exists():
            return {"error": f"Build {build_id} not found"}
        
        analysis = {
            "build_id": build_id,
            "timestamp": datetime.now().isoformat(),
            "components_analyzed": [],
            "metrics": {},
            "issues": [],
            "suggestions": []
        }
        
        if component_name:
            comp_analysis = self._analyze_component(component_name, build_path)
            analysis["components_analyzed"].append(comp_analysis)
        
        return analysis
    
    def _analyze_component(self, component_name: str, build_path: Path) -> Dict[str, Any]:
        """Analyze a specific component's performance and usage"""
        return {
            "component": component_name,
            "performance": {
                "avg_execution_time": "N/A",
                "memory_usage": "N/A",
                "cpu_usage": "N/A"
            },
            "usage_patterns": {
                "most_called_functions": [],
                "error_rate": 0.0
            },
            "feedback": {
                "issues": [],
                "suggestions": []
            }
        }
    
    def track_usage(self, component_name: str, function_name: str, duration_ms: float):
        """Track function usage and performance"""
        component_path = self._find_component(component_name)
        if not component_path:
            print(f"Component {component_name} not found")
            return
        
        analysis_dir = component_path / "analysis" / "usage-patterns"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        usage_file = analysis_dir / "usage_log.jsonl"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "function": function_name,
            "duration_ms": duration_ms
        }
        
        with open(usage_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def collect_feedback(self, component_name: str, feedback_type: str, message: str):
        """Collect AI model feedback or issues"""
        component_path = self._find_component(component_name)
        if not component_path:
            print(f"Component {component_name} not found")
            return
        
        feedback_dir = component_path / "analysis" / "feedback"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        
        feedback_file = feedback_dir / f"{feedback_type}_feedback.jsonl"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": feedback_type,
            "message": message
        }
        
        with open(feedback_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def generate_report(self, component_name: str) -> Dict[str, Any]:
        """Generate analysis report for a component"""
        component_path = self._find_component(component_name)
        if not component_path:
            return {"error": f"Component {component_name} not found"}
        
        report = {
            "component": component_name,
            "generated": datetime.now().isoformat(),
            "performance": self._analyze_performance(component_path),
            "usage": self._analyze_usage_patterns(component_path),
            "feedback": self._analyze_feedback(component_path),
            "recommendations": []
        }
        
        report["recommendations"] = self._generate_recommendations(report)
        
        analysis_dir = component_path / "analysis"
        report_file = analysis_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"Report generated: {report_file}")
        return report
    
    def _find_component(self, component_name: str) -> Path:
        """Find component in production, stable, or experimental"""
        for stage in ["production", "stable", "experimental"]:
            comp_path = self.components_dir / stage / component_name
            if comp_path.exists():
                return comp_path
        return None
    
    def _analyze_performance(self, component_path: Path) -> Dict[str, Any]:
        """Analyze performance metrics"""
        benchmarks_dir = component_path / "analysis" / "benchmarks"
        if not benchmarks_dir.exists():
            return {"status": "no_data"}
        
        return {"status": "analyzed", "metrics": {}}
    
    def _analyze_usage_patterns(self, component_path: Path) -> Dict[str, Any]:
        """Analyze usage patterns from logs"""
        usage_dir = component_path / "analysis" / "usage-patterns"
        usage_file = usage_dir / "usage_log.jsonl"
        
        if not usage_file.exists():
            return {"status": "no_data"}
        
        usage_data = []
        with open(usage_file, "r") as f:
            for line in f:
                usage_data.append(json.loads(line))
        
        function_counts = {}
        for entry in usage_data:
            func = entry["function"]
            function_counts[func] = function_counts.get(func, 0) + 1
        
        return {
            "status": "analyzed",
            "total_calls": len(usage_data),
            "most_called": sorted(function_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _analyze_feedback(self, component_path: Path) -> Dict[str, Any]:
        """Analyze feedback from AI models"""
        feedback_dir = component_path / "analysis" / "feedback"
        if not feedback_dir.exists():
            return {"status": "no_data"}
        
        feedback_data = {"issues": [], "suggestions": []}
        
        for feedback_file in feedback_dir.glob("*.jsonl"):
            with open(feedback_file, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    if entry["type"] == "issue":
                        feedback_data["issues"].append(entry["message"])
                    elif entry["type"] == "suggestion":
                        feedback_data["suggestions"].append(entry["message"])
        
        return {
            "status": "analyzed",
            "issues_count": len(feedback_data["issues"]),
            "suggestions_count": len(feedback_data["suggestions"]),
            "recent_issues": feedback_data["issues"][-5:],
            "recent_suggestions": feedback_data["suggestions"][-5:]
        }
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if report["usage"]["status"] == "no_data":
            recommendations.append("No usage data collected. Start tracking component usage.")
        
        if report["feedback"]["status"] == "analyzed":
            if report["feedback"]["issues_count"] > 5:
                recommendations.append("Multiple issues reported. Review and address feedback.")
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description="Live Analyzer for HyperSync Components")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a build")
    analyze_parser.add_argument("--build", required=True, help="Build ID")
    analyze_parser.add_argument("--component", help="Component name")
    
    track_parser = subparsers.add_parser("track", help="Track usage")
    track_parser.add_argument("--component", required=True, help="Component name")
    track_parser.add_argument("--function", required=True, help="Function name")
    track_parser.add_argument("--duration", type=float, required=True, help="Duration in ms")
    
    feedback_parser = subparsers.add_parser("feedback", help="Collect feedback")
    feedback_parser.add_argument("--component", required=True, help="Component name")
    feedback_parser.add_argument("--type", required=True, choices=["issue", "suggestion"], help="Feedback type")
    feedback_parser.add_argument("--message", required=True, help="Feedback message")
    
    report_parser = subparsers.add_parser("report", help="Generate report")
    report_parser.add_argument("--component", required=True, help="Component name")
    
    args = parser.parse_args()
    
    analyzer = LiveAnalyzer(args.project_root)
    
    if args.command == "analyze":
        result = analyzer.analyze_build(args.build, args.component)
        print(json.dumps(result, indent=2))
    
    elif args.command == "track":
        analyzer.track_usage(args.component, args.function, args.duration)
        print(f"Usage tracked for {args.component}.{args.function}")
    
    elif args.command == "feedback":
        analyzer.collect_feedback(args.component, args.type, args.message)
        print(f"Feedback collected for {args.component}")
    
    elif args.command == "report":
        report = analyzer.generate_report(args.component)
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
