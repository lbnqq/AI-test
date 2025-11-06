import argparse
import json
import os
import sys
from typing import Dict, List, Any

from config.config_loader import load_config
from analyzers.in_character import InCharacterAnalyzer
from analyzers.character_break import CharacterBreakAnalyzer
from analyzers.conflict_handler import ConflictHandlerAnalyzer
from analyzers.response_quality import ResponseQualityAnalyzer
from reporters.csv_reporter import CSVReporter
from reporters.json_reporter import JSONReporter
from reporters.md_reporter import MDReporter
from i18n import i18n


def main():
    """
    TPE QA Analyzer Main Execution Function.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=i18n.t('TPE QA Analyzer - Analyze TPE tool generated log files'))
    parser.add_argument('--log_file', required=True, help=i18n.t('TPE generated JSON log file path'))
    parser.add_argument('--output_dir', default='./analysis_reports', help=i18n.t('Analysis report output directory'))
    parser.add_argument('--config', default='config/config.json', help=i18n.t('Custom configuration file path'))
    
    args = parser.parse_args()
    
    # Check if log file exists
    if not os.path.exists(args.log_file):
        print(f"{i18n.t('Error')}: {i18n.t('File not found')}: {args.log_file}")
        sys.exit(1)
    
    # Check if output directory exists, create if not
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Load configuration file
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"{i18n.t('Error')}: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{i18n.t('Error')}: {i18n.t('JSON decode error')}: {e}")
        sys.exit(1)
    
    # Set language
    language = config.get('language', 'en')
    i18n.set_language(language)
    
    # Read and parse TPE log file
    try:
        with open(args.log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"{i18n.t('Error')}: {i18n.t('JSON decode error')}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{i18n.t('Error')}: {e}")
        sys.exit(1)
    
    # Initialize analyzer instances
    analyzers = [
        InCharacterAnalyzer(config),
        CharacterBreakAnalyzer(config),
        ConflictHandlerAnalyzer(config),
        ResponseQualityAnalyzer(config)
    ]
    
    # Iterate through execution_results, call analyze method of each analyzer
    execution_results = log_data.get('execution_results', [])
    all_analysis_results = []
    
    # Get role_applied from top level
    role_applied = log_data.get('role_applied', '')
    
    for i, result_item in enumerate(execution_results):
        # Add scenario ID to each result item
        result_item['scenario_id'] = f"scenario_{i+1}"
        # Add role_applied to each result item
        result_item['role_applied'] = role_applied
        
        # Call each analyzer for analysis
        for analyzer in analyzers:
            try:
                analysis_result = analyzer.analyze(result_item)
                # Add scenario ID to analysis result
                analysis_result['scenario_id'] = result_item['scenario_id']
                all_analysis_results.append(analysis_result)
            except Exception as e:
                print(f"Warning: Analyzer {analyzer.get_name()} encountered an error processing scenario {result_item['scenario_id']}: {e}")
    
    # Collect log metadata
    log_metadata = {
        'tested_model': log_data.get('tested_model', 'unknown'),
        'role_applied': log_data.get('role_applied', 'unknown'),
        'pressure_plan_file': log_data.get('pressure_plan_file', 'unknown'),
        'total_scenarios': len(execution_results)
    }
    
    # Call report generators to generate reports
    output_config = config.get('output', {})
    
    if output_config.get('csv', True):
        csv_reporter = CSVReporter()
        csv_reporter.generate(
            log_metadata, 
            all_analysis_results, 
            os.path.join(args.output_dir, 'report.csv')
        )
    
    if output_config.get('json', True):
        json_reporter = JSONReporter()
        json_reporter.generate(
            log_metadata, 
            all_analysis_results, 
            os.path.join(args.output_dir, 'report.json')
        )
    
    if output_config.get('markdown', True):
        md_reporter = MDReporter()
        md_reporter.generate(
            log_metadata, 
            all_analysis_results, 
            os.path.join(args.output_dir, 'report.md')
        )
    
    print(f"{i18n.t('Analysis complete, reports saved to')}: {args.output_dir}")


if __name__ == '__main__':
    main()