import os
import json
import time
import datetime
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class RAGEvaluator:
    """Evaluates the performance of RAG system components."""
    
    def __init__(self, metrics_dir="metrics"):
        """Initialize the evaluator with a directory to store metrics."""
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Track current session
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_metrics = {
            "extraction": [],
            "retrieval": [],
            "generation": [],
            "end_to_end": []
        }
        
        # Load baseline metrics if available
        self.baseline_metrics = self._load_baseline_metrics()
    
    def _load_baseline_metrics(self):
        """Load baseline metrics for comparison."""
        baseline_path = self.metrics_dir / "baseline_metrics.json"
        if baseline_path.exists():
            try:
                with open(baseline_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading baseline metrics: {e}")
        
        # Return empty baseline if none exists
        return {
            "extraction": {},
            "retrieval": {},
            "generation": {},
            "end_to_end": {}
        }
    
    def save_session_metrics(self):
        """Save the current session metrics."""
        session_path = self.metrics_dir / f"session_{self.session_id}.json"
        try:
            with open(session_path, 'w') as f:
                json.dump(self.session_metrics, f, indent=2)
            logger.info(f"Saved session metrics to {session_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving session metrics: {e}")
            return False
    
    def set_as_baseline(self):
        """Set the current session as the baseline for future comparisons."""
        # Calculate averages from session metrics
        baseline = {
            "extraction": self._calculate_avg_metrics(self.session_metrics["extraction"]),
            "retrieval": self._calculate_avg_metrics(self.session_metrics["retrieval"]),
            "generation": self._calculate_avg_metrics(self.session_metrics["generation"]),
            "end_to_end": self._calculate_avg_metrics(self.session_metrics["end_to_end"]),
            "timestamp": datetime.datetime.now().isoformat(),
            "session_id": self.session_id
        }
        
        baseline_path = self.metrics_dir / "baseline_metrics.json"
        try:
            with open(baseline_path, 'w') as f:
                json.dump(baseline, f, indent=2)
            logger.info(f"Set current session as baseline")
            
            # Update in-memory baseline
            self.baseline_metrics = baseline
            return True
        except Exception as e:
            logger.error(f"Error setting baseline: {e}")
            return False
    
    def _calculate_avg_metrics(self, metrics_list):
        """Calculate average metrics from a list of metric records."""
        if not metrics_list:
            return {}
        
        # Collect all metric keys
        all_keys = set()
        for metrics in metrics_list:
            all_keys.update(metrics.keys())
        
        # Calculate averages
        avg_metrics = {}
        for key in all_keys:
            if key in ['timestamp', 'id', 'query', 'text']:
                continue  # Skip non-numeric fields
                
            values = [m.get(key) for m in metrics_list if key in m and m[key] is not None]
            if values:
                avg_metrics[key] = sum(values) / len(values)
        
        return avg_metrics
    
    def evaluate_extraction(self, email_text, extracted_info, ground_truth=None):
        """
        Evaluate email information extraction.
        
        Args:
            email_text: Original email text
            extracted_info: Dictionary with extracted information
            ground_truth: Optional ground truth for comparison
        """
        start_time = time.time()
        
        metrics = {
            "timestamp": datetime.datetime.now().isoformat(),
            "process_time_ms": 0,
            "extraction_completeness": 0,
            "query_length": len(email_text),
            "fields_extracted": 0,
            "text": email_text[:100] + "..."  # Store truncated text for reference
        }
        
        # Count non-empty fields
        non_empty_fields = 0
        total_fields = 0
        
        for key, value in extracted_info.items():
            if key in ['destination', 'dates', 'travelers', 'budget', 'interests', 'duration', 'travel_type']:
                total_fields += 1
                if value and value not in [None, 'None']:
                    non_empty_fields += 1
        
        # Calculate metrics
        metrics["fields_extracted"] = non_empty_fields
        metrics["extraction_completeness"] = non_empty_fields / max(1, total_fields)
        metrics["process_time_ms"] = (time.time() - start_time) * 1000
        
        # Compare with ground truth if available
        if ground_truth:
            correct_fields = 0
            for key in ['destination', 'dates', 'travelers', 'budget', 'interests', 'duration', 'travel_type']:
                if key in ground_truth and key in extracted_info:
                    # Normalize for comparison
                    gt_value = str(ground_truth[key]).lower() if ground_truth[key] else None
                    extracted_value = str(extracted_info[key]).lower() if extracted_info[key] else None
                    
                    if gt_value == extracted_value:
                        correct_fields += 1
            
            metrics["accuracy"] = correct_fields / max(1, total_fields)
        
        # Save to session
        self.session_metrics["extraction"].append(metrics)
        
        # Compare with baseline
        comparison = {}
        if self.baseline_metrics["extraction"]:
            for key in metrics:
                if key in ['timestamp', 'text']:
                    continue
                if key in self.baseline_metrics["extraction"]:
                    baseline_value = self.baseline_metrics["extraction"][key]
                    current_value = metrics[key]
                    if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                        change = current_value - baseline_value
                        percent_change = (change / baseline_value) * 100 if baseline_value != 0 else float('inf')
                        comparison[key] = {
                            "baseline": baseline_value,
                            "current": current_value,
                            "change": change,
                            "percent_change": percent_change
                        }
        
        return {
            "metrics": metrics,
            "comparison": comparison
        }
    
    def evaluate_retrieval(self, query, retrieved_packages, 
                          relevant_ids=None, top_k=None):
        """
        Evaluate package retrieval performance.
        
        Args:
            query: The search query
            retrieved_packages: List of retrieved packages
            relevant_ids: Optional list of relevant package IDs for relevance calculation
            top_k: Max number of packages to evaluate (defaults to all)
        """
        start_time = time.time()
        
        top_k = top_k or len(retrieved_packages)
        
        metrics = {
            "timestamp": datetime.datetime.now().isoformat(),
            "process_time_ms": 0,
            "packages_count": len(retrieved_packages),
            "query_length": len(query),
            "query": query[:100] + "..." if len(query) > 100 else query  # Truncated query for reference
        }
        
        # Basic diversity metrics
        location_set = set()
        theme_set = set()
        price_range = [float('inf'), 0]  # min, max
        
        for package in retrieved_packages[:top_k]:
            # Track unique locations
            location = package.get('location', package.get('destination', ''))
            if location:
                location_set.add(location)
            
            # Track price range
            if isinstance(package.get('price'), (int, float)):
                price = float(package.get('price'))
                price_range[0] = min(price_range[0], price)
                price_range[1] = max(price_range[1], price)
            elif isinstance(package.get('price'), dict) and 'amount' in package.get('price'):
                price = float(package.get('price')['amount'])
                price_range[0] = min(price_range[0], price)
                price_range[1] = max(price_range[1], price)
            
            # Track thematic diversity
            description = package.get('description', '').lower()
            activities = []
            
            if isinstance(package.get('activities'), list):
                for activity in package.get('activities'):
                    if isinstance(activity, dict) and 'name' in activity:
                        activities.append(activity['name'].lower())
                    elif isinstance(activity, str):
                        activities.append(activity.lower())
            
            # Check for common themes
            all_text = description + ' ' + ' '.join(activities)
            if 'beach' in all_text or 'ocean' in all_text or 'sea' in all_text:
                theme_set.add('beach')
            if 'mountain' in all_text or 'hiking' in all_text or 'trek' in all_text:
                theme_set.add('mountain')
            if 'city' in all_text or 'urban' in all_text or 'museum' in all_text:
                theme_set.add('city')
            if 'culture' in all_text or 'history' in all_text or 'heritage' in all_text:
                theme_set.add('culture')
            if 'food' in all_text or 'culinary' in all_text or 'gastronomy' in all_text:
                theme_set.add('food')
        
        # Calculate metrics
        metrics["location_diversity"] = len(location_set) / max(1, len(retrieved_packages[:top_k]))
        metrics["theme_diversity"] = len(theme_set) / max(1, len(retrieved_packages[:top_k]))
        metrics["price_range_width"] = price_range[1] - price_range[0] if price_range[1] > price_range[0] else 0
        
        # Calculate relevance if ground truth provided
        if relevant_ids:
            retrieved_ids = [p.get('id') for p in retrieved_packages[:top_k] if p.get('id')]
            
            # Count relevant packages retrieved
            relevant_retrieved = set(retrieved_ids).intersection(set(relevant_ids))
            
            # Precision = relevant_retrieved / retrieved
            metrics["precision"] = len(relevant_retrieved) / max(1, len(retrieved_packages[:top_k]))
            
            # Recall = relevant_retrieved / relevant
            metrics["recall"] = len(relevant_retrieved) / max(1, len(relevant_ids))
            
            # F1 score = 2 * precision * recall / (precision + recall)
            if metrics["precision"] + metrics["recall"] > 0:
                metrics["f1_score"] = 2 * metrics["precision"] * metrics["recall"] / (metrics["precision"] + metrics["recall"])
            else:
                metrics["f1_score"] = 0
        
        metrics["process_time_ms"] = (time.time() - start_time) * 1000
        
        # Save to session
        self.session_metrics["retrieval"].append(metrics)
        
        # Compare with baseline
        comparison = {}
        if self.baseline_metrics["retrieval"]:
            for key in metrics:
                if key in ['timestamp', 'query']:
                    continue
                if key in self.baseline_metrics["retrieval"]:
                    baseline_value = self.baseline_metrics["retrieval"][key]
                    current_value = metrics[key]
                    if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                        change = current_value - baseline_value
                        percent_change = (change / baseline_value) * 100 if baseline_value != 0 else float('inf')
                        comparison[key] = {
                            "baseline": baseline_value,
                            "current": current_value,
                            "change": change,
                            "percent_change": percent_change
                        }
        
        return {
            "metrics": metrics,
            "comparison": comparison
        }
    
    def evaluate_generation(self, customer_info, packages, proposal):
        """
        Evaluate proposal generation quality.
        
        Args:
            customer_info: Dictionary with extracted customer information
            packages: List of retrieved packages used for generation
            proposal: Generated proposal text
        """
        start_time = time.time()
        
        metrics = {
            "timestamp": datetime.datetime.now().isoformat(),
            "process_time_ms": 0,
            "proposal_length": len(proposal),
            "structure_score": 0,
            "information_density": 0,
            "coherence_score": 0
        }
        
        # Check for structure (headings, sections)
        heading_pattern = r'^#+\s+.+$'
        headings = re.findall(heading_pattern, proposal, re.MULTILINE)
        metrics["headings_count"] = len(headings)
        metrics["structure_score"] = min(1.0, len(headings) / 5)  # Score based on presence of headings
        
        # Check for incorporation of customer info
        customer_info_count = 0
        for key, value in customer_info.items():
            if value and value not in [None, 'None']:
                if str(value).lower() in proposal.lower():
                    customer_info_count += 1
        
        metrics["customer_info_usage"] = customer_info_count / max(1, sum(1 for v in customer_info.values() if v and v not in [None, 'None']))
        
        # Check for package information incorporation
        package_info_count = 0
        for package in packages:
            # Check for location, activities, etc.
            if package.get('location') and package.get('location').lower() in proposal.lower():
                package_info_count += 1
            
            # Check for activities
            activities = []
            if isinstance(package.get('activities'), list):
                for activity in package.get('activities'):
                    if isinstance(activity, dict) and 'name' in activity:
                        activities.append(activity['name'].lower())
                    elif isinstance(activity, str):
                        activities.append(activity.lower())
            
            for activity in activities:
                if activity in proposal.lower():
                    package_info_count += 1
        
        metrics["package_info_usage"] = min(1.0, package_info_count / (len(packages) * 2))  # Normalize to 0-1
        
        # Check for day-by-day itinerary
        day_pattern = r'day\s+\d+'
        day_mentions = re.findall(day_pattern, proposal.lower())
        metrics["day_structure"] = len(set(day_mentions))
        
        # Information density (proportion of lines with concrete details)
        lines = proposal.strip().split('\n')
        detail_lines = 0
        for line in lines:
            # Lines with dates, times, prices, or specific places likely have concrete details
            if re.search(r'\d+[:.]\d+|[$€£]\d+|^\s*-\s+\w+', line):
                detail_lines += 1
        
        metrics["information_density"] = detail_lines / max(1, len(lines))
        
        # Calculate overall quality score (weighted average of other metrics)
        metrics["quality_score"] = (
            metrics["structure_score"] * 0.3 +
            metrics["customer_info_usage"] * 0.3 +
            metrics["package_info_usage"] * 0.2 +
            metrics["information_density"] * 0.2
        )
        
        metrics["process_time_ms"] = (time.time() - start_time) * 1000
        
        # Save to session
        self.session_metrics["generation"].append(metrics)
        
        # Compare with baseline
        comparison = {}
        if self.baseline_metrics["generation"]:
            for key in metrics:
                if key in ['timestamp']:
                    continue
                if key in self.baseline_metrics["generation"]:
                    baseline_value = self.baseline_metrics["generation"][key]
                    current_value = metrics[key]
                    if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                        change = current_value - baseline_value
                        percent_change = (change / baseline_value) * 100 if baseline_value != 0 else float('inf')
                        comparison[key] = {
                            "baseline": baseline_value,
                            "current": current_value,
                            "change": change,
                            "percent_change": percent_change
                        }
        
        return {
            "metrics": metrics,
            "comparison": comparison
        }
    
    def evaluate_end_to_end(self, email_text, proposal, processing_time=None):
        """
        Evaluate end-to-end pipeline performance.
        
        Args:
            email_text: Original email text
            proposal: Final generated proposal
            processing_time: Optional total processing time in seconds
        """
        start_time = time.time()
        
        metrics = {
            "timestamp": datetime.datetime.now().isoformat(),
            "process_time_ms": 0,
            "query_length": len(email_text),
            "response_length": len(proposal),
            "total_processing_time": processing_time,
            "efficiency_ratio": 0  # Will calculate below
        }
        
        # Calculate efficiency ratio (response length / processing time)
        if processing_time:
            metrics["efficiency_ratio"] = len(proposal) / max(0.1, processing_time)
        
        # Calculate response complexity
        paragraph_count = proposal.count('\n\n') + 1
        word_count = len(proposal.split())
        sentence_count = len(re.findall(r'[.!?]+', proposal))
        
        metrics["paragraph_count"] = paragraph_count
        metrics["word_count"] = word_count
        metrics["sentence_count"] = sentence_count
        metrics["words_per_sentence"] = word_count / max(1, sentence_count)
        
        # Score on richness of response (using proxy metrics)
        metrics["content_richness"] = min(1.0, paragraph_count / 10)
        
        metrics["process_time_ms"] = (time.time() - start_time) * 1000
        
        # Save to session
        self.session_metrics["end_to_end"].append(metrics)
        
        # Compare with baseline
        comparison = {}
        if self.baseline_metrics["end_to_end"]:
            for key in metrics:
                if key in ['timestamp']:
                    continue
                if key in self.baseline_metrics["end_to_end"]:
                    baseline_value = self.baseline_metrics["end_to_end"][key]
                    current_value = metrics[key]
                    if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                        change = current_value - baseline_value
                        percent_change = (change / baseline_value) * 100 if baseline_value != 0 else float('inf')
                        comparison[key] = {
                            "baseline": baseline_value,
                            "current": current_value,
                            "change": change,
                            "percent_change": percent_change
                        }
        
        return {
            "metrics": metrics,
            "comparison": comparison
        }
    
    def get_summary_report(self):
        """Generate a summary report of all metrics in the current session."""
        summary = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "extraction": self._calculate_avg_metrics(self.session_metrics["extraction"]),
            "retrieval": self._calculate_avg_metrics(self.session_metrics["retrieval"]),
            "generation": self._calculate_avg_metrics(self.session_metrics["generation"]),
            "end_to_end": self._calculate_avg_metrics(self.session_metrics["end_to_end"]),
            "sample_count": {
                "extraction": len(self.session_metrics["extraction"]),
                "retrieval": len(self.session_metrics["retrieval"]),
                "generation": len(self.session_metrics["generation"]),
                "end_to_end": len(self.session_metrics["end_to_end"])
            }
        }
        
        # Add comparison with baseline
        if self.baseline_metrics:
            summary["baseline_comparison"] = {}
            
            for component in ["extraction", "retrieval", "generation", "end_to_end"]:
                summary["baseline_comparison"][component] = {}
                
                for key, value in summary[component].items():
                    if key in self.baseline_metrics[component]:
                        baseline_value = self.baseline_metrics[component][key]
                        change = value - baseline_value
                        percent_change = (change / baseline_value) * 100 if baseline_value != 0 else float('inf')
                        
                        summary["baseline_comparison"][component][key] = {
                            "baseline": baseline_value,
                            "current": value,
                            "change": change,
                            "percent_change": percent_change
                        }
        
        return summary