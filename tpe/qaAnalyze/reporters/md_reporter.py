import os
from typing import Dict, List, Any
from i18n import i18n


class MDReporter:
    """Markdown Report Generator, generates easy-to-read summary reports."""

    def generate(self, log_metadata: dict, analysis_results: list, output_path: str):
        """Generate a Markdown format report.
        
        Args:
            log_metadata (dict): TPE log metadata
            analysis_results (list): List of analysis results
            output_path (str): Full save path for the report file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate Markdown content
        content = []
        content.append("# TPE QA Analysis Report")
        content.append("")
        
        # Add metadata
        content.append(f"## {i18n.t('Test Metadata')}")
        content.append(f"| {i18n.t('Field')} | {i18n.t('Value')} |")
        content.append("|-------|-------|")
        for key, value in log_metadata.items():
            content.append(f"| {key} | {value} |")
        content.append("")
        
        # Add analysis results summary
        content.append(f"## {i18n.t('Analysis Results Summary')}")
        content.append(f"| {i18n.t('Analyzer')} | {i18n.t('Score')} | {i18n.t('Details')} |")
        content.append("|----------|-------|---------|")
        
        for result in analysis_results:
            analyzer = result.get('analyzer', '')
            # Translate analyzer name
            translated_analyzer = i18n.t(analyzer)
            
            score = result.get('score', 'N/A')
            details = str(result.get('details', ''))
            content.append(f"| {translated_analyzer} | {score} | {details} |")
        
        # Write to Markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))