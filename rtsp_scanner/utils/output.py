"""Output formatting utilities"""

import json
import csv
from typing import List, Dict
from pathlib import Path


class OutputFormatter:
    """Format and export scan results"""

    @staticmethod
    def _format_response_time(time_value) -> str:
        """
        Format response time to be human-readable

        Args:
            time_value: Response time in seconds (float)

        Returns:
            Formatted string (e.g., "1.5ms", "234ms", "1.2s")
        """
        if time_value is None or time_value == '':
            return ''

        try:
            time_float = float(time_value)
            if time_float < 0.001:  # Less than 1ms
                return f"{time_float * 1000000:.0f}µs"
            elif time_float < 1:  # Less than 1 second
                return f"{time_float * 1000:.1f}ms"
            else:  # 1 second or more
                return f"{time_float:.2f}s"
        except (ValueError, TypeError):
            return str(time_value)

    @staticmethod
    def format_table(results: List[Dict], headers: List[str] = None) -> str:
        """
        Format results as an ASCII table

        Args:
            results: List of result dictionaries
            headers: Optional list of headers to display

        Returns:
            Formatted table string
        """
        if not results:
            return "No results to display"

        # Auto-detect headers if not provided
        if headers is None:
            headers = list(results[0].keys())

        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = len(str(header))

        # Format values for display
        formatted_results = []
        for result in results:
            formatted = {}
            for header in headers:
                value = result.get(header, '')
                # Format response_time specially
                if header == 'response_time':
                    value = OutputFormatter._format_response_time(value)
                # Format working status as checkmark/cross
                elif header == 'working':
                    if value is True:
                        value = '✓'
                    elif value is False:
                        value = '✗'
                    else:
                        value = '-'
                # Format channel status with symbols
                elif header == 'status':
                    status_map = {
                        'ok': '✓ OK',
                        'auth_error': '✗ Auth',
                        'forbidden': '⊘ Forbidden',
                        'not_found': '- N/A',
                        'timeout': '? Timeout',
                        'error': '! Error',
                    }
                    value = status_map.get(value, value or '-')
                formatted[header] = value
            formatted_results.append(formatted)

        for formatted in formatted_results:
            for header in headers:
                value = formatted.get(header, '')
                col_widths[header] = max(col_widths[header], len(str(value)))

        # Build table
        separator = '+' + '+'.join('-' * (col_widths[h] + 2) for h in headers) + '+'
        header_row = '|' + '|'.join(f" {h:<{col_widths[h]}} " for h in headers) + '|'

        table = [separator, header_row, separator]

        for formatted in formatted_results:
            row = '|' + '|'.join(
                f" {str(formatted.get(h, '')):<{col_widths[h]}} " for h in headers
            ) + '|'
            table.append(row)

        table.append(separator)

        return '\n'.join(table)

    @staticmethod
    def format_json(results: List[Dict], pretty: bool = True) -> str:
        """
        Format results as JSON

        Args:
            results: List of result dictionaries
            pretty: Pretty print with indentation

        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(results, indent=2, default=str)
        return json.dumps(results, default=str)

    @staticmethod
    def export_json(results: List[Dict], filepath: str):
        """
        Export results to JSON file

        Args:
            results: List of result dictionaries
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    @staticmethod
    def export_csv(results: List[Dict], filepath: str):
        """
        Export results to CSV file

        Args:
            results: List of result dictionaries
            filepath: Output file path
        """
        if not results:
            return

        headers = list(results[0].keys())

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)

    @staticmethod
    def format_summary(results: List[Dict], scan_type: str = "scan") -> str:
        """
        Format a simple summary of scan results

        Args:
            results: List of result dictionaries
            scan_type: Type of scan performed

        Returns:
            Formatted summary string
        """
        if not results:
            return f"\n{scan_type}: No results found\n"

        # For port scan, show open ports
        if 'status' in results[0]:
            open_count = sum(1 for r in results if r.get('status') == 'open')
            if open_count > 0:
                return f"\nFound {open_count} camera(s)\n"
            else:
                return f"\nNo cameras found\n"

        # For channel scan, show unique hosts
        if 'host' in results[0]:
            unique_hosts = len(set(r.get('host') for r in results))
            channel_count = len(results)
            return f"\nFound {unique_hosts} camera(s) with {channel_count} channel(s)\n"

        return f"\n{scan_type}: Found {len(results)} result(s)\n"
