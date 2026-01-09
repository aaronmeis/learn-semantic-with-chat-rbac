"""
Validation Agent - Validates responses before delivery
"""

from typing import Dict, Any, List, Optional
import logging
import re

from .base import BaseAgent
from ..rbac.framework import Permission
from ..semantic_store import SemanticStore


class ValidationAgent(BaseAgent):
    """Agent responsible for validating chatbot responses"""
    
    def __init__(self, agent_id: str, rbac, user_id: str, 
                 semantic_store: SemanticStore, policies: Optional[Dict[str, Any]] = None):
        """
        Initialize Validation Agent
        
        Args:
            agent_id: Unique agent identifier
            rbac: RBAC framework instance
            user_id: User ID for permission checking
            semantic_store: Semantic data store instance
            policies: Validation policies dictionary
        """
        super().__init__(agent_id, "ValidationAgent", rbac, user_id)
        self.semantic_store = semantic_store
        self.policies = policies or self._default_policies()
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{agent_id}")
    
    def execute(self, response: str, query: str, **kwargs) -> Dict[str, Any]:
        """
        Validate a chatbot response
        
        Args:
            response: Response text to validate
            query: Original query
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with validation results
        """
        # Check permissions
        self.require_permission(Permission.VALIDATION_EXECUTE)
        self.require_permission(Permission.DATA_READ)
        self.require_permission(Permission.POLICY_READ)
        
        try:
            self.log_request({"response_length": len(response), "query": query})
            
            validation_results = {
                "is_valid": True,
                "checks": {},
                "warnings": [],
                "errors": [],
                "score": 0.0
            }
            
            # Run validation checks
            checks = [
                self._check_length(response),
                self._check_safety(response),
                self._check_factual_consistency(response, query),
                self._check_policy_compliance(response),
                self._check_format(response)
            ]
            
            for check_name, check_result in checks:
                validation_results["checks"][check_name] = check_result
                if not check_result.get("passed", False):
                    validation_results["is_valid"] = False
                    if check_result.get("severity") == "error":
                        validation_results["errors"].append(check_result.get("message", ""))
                    else:
                        validation_results["warnings"].append(check_result.get("message", ""))
            
            # Calculate validation score
            passed_checks = sum(1 for c in validation_results["checks"].values() if c.get("passed", False))
            total_checks = len(validation_results["checks"])
            validation_results["score"] = passed_checks / total_checks if total_checks > 0 else 0.0
            
            self.logger.info(f"Validation completed: valid={validation_results['is_valid']}, score={validation_results['score']:.2f}")
            
            return validation_results
            
        except PermissionError:
            raise
        except Exception as e:
            self.log_error(e, {"response": response[:100]})
            raise
    
    def _check_length(self, response: str) -> tuple:
        """Check if response length is appropriate"""
        min_length = self.policies.get("min_length", 10)
        max_length = self.policies.get("max_length", 10000)
        
        length = len(response)
        passed = min_length <= length <= max_length
        
        return ("length_check", {
            "passed": passed,
            "severity": "error" if not passed else "info",
            "message": f"Response length {length} is {'within' if passed else 'outside'} acceptable range ({min_length}-{max_length})",
            "value": length
        })
    
    def _check_safety(self, response: str) -> tuple:
        """Check for inappropriate or unsafe content"""
        # Simple keyword-based safety check (can be enhanced with ML models)
        unsafe_patterns = self.policies.get("unsafe_patterns", [
            r"\b(hack|exploit|violence|harm)\b",
            # Add more patterns as needed
        ])
        
        warnings = []
        for pattern in unsafe_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                warnings.append(f"Potential unsafe content detected: {pattern}")
        
        passed = len(warnings) == 0
        
        return ("safety_check", {
            "passed": passed,
            "severity": "warning" if warnings else "info",
            "message": "Safety check passed" if passed else "; ".join(warnings),
            "warnings": warnings
        })
    
    def _check_factual_consistency(self, response: str, query: str) -> tuple:
        """Check factual consistency with data store"""
        # This is a simplified check - in production, use more sophisticated fact-checking
        try:
            # Search for key claims in the response
            key_terms = self._extract_key_terms(response)
            consistency_score = 0.0
            
            if key_terms:
                # Verify against semantic store
                for term in key_terms[:3]:  # Check top 3 terms
                    results = self.semantic_store.search(term, limit=1)
                    if results:
                        consistency_score += 0.33
            
            passed = consistency_score >= 0.5
            
            return ("factual_consistency", {
                "passed": passed,
                "severity": "warning" if not passed else "info",
                "message": f"Factual consistency score: {consistency_score:.2f}",
                "score": consistency_score
            })
        except Exception as e:
            self.logger.warning(f"Error in factual consistency check: {e}")
            return ("factual_consistency", {
                "passed": True,  # Fail open
                "severity": "warning",
                "message": f"Could not verify factual consistency: {e}"
            })
    
    def _check_policy_compliance(self, response: str) -> tuple:
        """Check compliance with defined policies"""
        # Check against policy rules
        policy_rules = self.policies.get("rules", [])
        violations = []
        
        for rule in policy_rules:
            rule_type = rule.get("type")
            pattern = rule.get("pattern")
            if pattern and re.search(pattern, response, re.IGNORECASE):
                violations.append(rule.get("name", "Unknown rule violation"))
        
        passed = len(violations) == 0
        
        return ("policy_compliance", {
            "passed": passed,
            "severity": "error" if violations else "info",
            "message": "Policy compliant" if passed else f"Policy violations: {', '.join(violations)}",
            "violations": violations
        })
    
    def _check_format(self, response: str) -> tuple:
        """Check response format"""
        # Basic format checks
        has_content = len(response.strip()) > 0
        has_proper_ending = response.rstrip().endswith(('.', '!', '?')) or len(response) < 50
        
        passed = has_content
        
        return ("format_check", {
            "passed": passed,
            "severity": "warning" if not has_proper_ending else "info",
            "message": "Format check passed" if passed else "Response format issues detected",
            "has_proper_ending": has_proper_ending
        })
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text (simplified)"""
        # Simple extraction - in production, use NLP libraries
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', text)
        # Return unique words, limited to top 10
        return list(set(words))[:10]
    
    def _default_policies(self) -> Dict[str, Any]:
        """Default validation policies"""
        return {
            "min_length": 10,
            "max_length": 10000,
            "unsafe_patterns": [],
            "rules": []
        }
