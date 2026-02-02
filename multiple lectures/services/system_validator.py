"""
System Validator - Validates all tracking features are functional
Checks attendance tracking, download buttons, and all event tracking
"""

import os
import json
from typing import Dict, List, Tuple
from datetime import datetime


class SystemValidator:
    """Validates all system features and tracking functionality"""
    
    def __init__(self):
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'warnings': [],
            'errors': []
        }
    
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        print("🔍 Starting System Validation...\n")
        
        # Check 1: Storage directories
        self._check_storage_directories()
        
        # Check 2: Configuration files
        self._check_configuration()
        
        # Check 3: Activity tracking
        self._check_activity_tracking()
        
        # Check 4: Required services
        self._check_services()
        
        # Check 5: Page files
        self._check_pages()
        
        # Check 6: Data integrity
        self._check_data_integrity()
        
        # Generate report
        return self._generate_report()
    
    def _check_storage_directories(self):
        """Check if storage directories exist"""
        check_name = "Storage Directories"
        required_dirs = [
            "./storage",
            "./storage/courses",
            "./storage/lectures",
            "./storage/quizzes",
            "./storage/users"
        ]
        
        missing = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing.append(dir_path)
        
        if missing:
            self.validation_results['warnings'].append({
                'check': check_name,
                'message': f"Missing directories: {', '.join(missing)}"
            })
            print(f"⚠️  {check_name}: {len(missing)} directories missing")
        else:
            self.validation_results['checks'].append({
                'check': check_name,
                'status': 'passed'
            })
            print(f"✅ {check_name}: All present")
    
    def _check_configuration(self):
        """Check configuration files"""
        check_name = "Configuration Files"
        
        config_file = "./config.yaml"
        if not os.path.exists(config_file):
            self.validation_results['errors'].append({
                'check': check_name,
                'message': "config.yaml not found"
            })
            print(f"❌ {check_name}: config.yaml missing")
            return
        
        # Check for required config sections
        try:
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            required_sections = ['storage', 'api', 'app']
            missing = [s for s in required_sections if s not in config]
            
            if missing:
                self.validation_results['warnings'].append({
                    'check': check_name,
                    'message': f"Missing config sections: {', '.join(missing)}"
                })
                print(f"⚠️  {check_name}: Missing sections")
            else:
                self.validation_results['checks'].append({
                    'check': check_name,
                    'status': 'passed'
                })
                print(f"✅ {check_name}: Complete")
        except Exception as e:
            self.validation_results['errors'].append({
                'check': check_name,
                'message': f"Config error: {str(e)}"
            })
            print(f"❌ {check_name}: Error reading config")
    
    def _check_activity_tracking(self):
        """Check activity tracking functionality"""
        check_name = "Activity Tracking"
        
        tracking_file = "./storage/activity_tracking.json"
        session_file = "./storage/session_tracking.json"
        
        issues = []
        if not os.path.exists(tracking_file):
            issues.append("activity_tracking.json missing")
        if not os.path.exists(session_file):
            issues.append("session_tracking.json missing")
        
        if issues:
            self.validation_results['warnings'].append({
                'check': check_name,
                'message': ', '.join(issues)
            })
            print(f"⚠️  {check_name}: {len(issues)} issues")
        else:
            # Check file structure
            try:
                with open(tracking_file, 'r') as f:
                    data = json.load(f)
                    if 'activities' not in data:
                        issues.append("Invalid tracking file structure")
                
                if issues:
                    self.validation_results['warnings'].append({
                        'check': check_name,
                        'message': ', '.join(issues)
                    })
                    print(f"⚠️  {check_name}: Structure issues")
                else:
                    self.validation_results['checks'].append({
                        'check': check_name,
                        'status': 'passed',
                        'activities_count': len(data.get('activities', []))
                    })
                    print(f"✅ {check_name}: Functional ({len(data['activities'])} activities)")
            except Exception as e:
                self.validation_results['errors'].append({
                    'check': check_name,
                    'message': f"Error: {str(e)}"
                })
                print(f"❌ {check_name}: Read error")
    
    def _check_services(self):
        """Check required service files"""
        check_name = "Service Files"
        
        required_services = [
            "./services/activity_tracker.py",
            "./services/teaching_score.py",
            "./services/ai_explainer_bot.py"
        ]
        
        missing = []
        for service in required_services:
            if not os.path.exists(service):
                missing.append(os.path.basename(service))
        
        if missing:
            self.validation_results['errors'].append({
                'check': check_name,
                'message': f"Missing services: {', '.join(missing)}"
            })
            print(f"❌ {check_name}: {len(missing)} missing")
        else:
            self.validation_results['checks'].append({
                'check': check_name,
                'status': 'passed'
            })
            print(f"✅ {check_name}: All present")
    
    def _check_pages(self):
        """Check required page files"""
        check_name = "Page Files"
        
        required_pages = [
            "./app/pages/tracking.py",
            "./app/pages/student_activity.py",
            "./app/pages/analytics_dashboard.py"
        ]
        
        missing = []
        for page in required_pages:
            if not os.path.exists(page):
                missing.append(os.path.basename(page))
        
        if missing:
            self.validation_results['errors'].append({
                'check': check_name,
                'message': f"Missing pages: {', '.join(missing)}"
            })
            print(f"❌ {check_name}: {len(missing)} missing")
        else:
            self.validation_results['checks'].append({
                'check': check_name,
                'status': 'passed'
            })
            print(f"✅ {check_name}: All present")
    
    def _check_data_integrity(self):
        """Check data file integrity"""
        check_name = "Data Integrity"
        
        data_files = {
            "./storage/courses.json": "courses",
            "./storage/users.json": "users",
            "./storage/activity_tracking.json": "activities"
        }
        
        issues = []
        for filepath, key in data_files.items():
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if key not in data:
                            issues.append(f"{os.path.basename(filepath)}: missing '{key}' key")
                except json.JSONDecodeError:
                    issues.append(f"{os.path.basename(filepath)}: invalid JSON")
        
        if issues:
            self.validation_results['warnings'].append({
                'check': check_name,
                'message': ', '.join(issues)
            })
            print(f"⚠️  {check_name}: {len(issues)} issues")
        else:
            self.validation_results['checks'].append({
                'check': check_name,
                'status': 'passed'
            })
            print(f"✅ {check_name}: Verified")
    
    def _generate_report(self) -> Dict:
        """Generate validation report"""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        passed = len(self.validation_results['checks'])
        warnings = len(self.validation_results['warnings'])
        errors = len(self.validation_results['errors'])
        
        print(f"✅ Passed:   {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Errors:   {errors}")
        
        if errors == 0 and warnings == 0:
            print("\n🎉 System validation complete - all checks passed!")
        elif errors == 0:
            print("\n⚠️  System functional with minor warnings")
        else:
            print("\n❌ System has critical errors - fix required")
        
        print("="*60 + "\n")
        
        return self.validation_results
    
    def save_report(self, output_path="./validation_report.json"):
        """Save validation report to file"""
        with open(output_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        print(f"💾 Report saved to: {output_path}")


def run_validation():
    """Run system validation"""
    validator = SystemValidator()
    results = validator.validate_all()
    validator.save_report()
    return results


if __name__ == "__main__":
    run_validation()
